#!/usr/bin/env python3
"""Commit changed files by task area and push the current branch."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TaskGroup:
    """A path-based commit group."""

    message: str
    prefixes: tuple[str, ...] = ()
    exact: tuple[str, ...] = ()

    def matches(self, path: str) -> bool:
        """Return whether the path belongs to this task group."""
        return path in self.exact or any(path.startswith(prefix) for prefix in self.prefixes)


TASK_GROUPS = (
    TaskGroup(
        message="chore: update project safety and config",
        exact=(".gitignore", ".env.example"),
        prefixes=("configs/",),
    ),
    TaskGroup(
        message="docs: update operating documentation",
        exact=("README.md", "AGENTS.md"),
        prefixes=(".agents/skills/", "docs/", "agents/broadcasting/README.md"),
    ),
    TaskGroup(
        message="feat: update broadcasting content pipeline",
        prefixes=(
            "agents/broadcasting/pipeline/",
            "agents/broadcasting/prompts/",
            "agents/broadcasting/schemas/",
        ),
    ),
    TaskGroup(
        message="feat: update Discord bot",
        prefixes=("apps/discord-bot/",),
    ),
    TaskGroup(
        message="feat: update publishing integrations",
        prefixes=("agents/broadcasting/publishers/", "scripts/linkedin_oauth_server.py"),
    ),
)


SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]+"),
    re.compile(r"(DISCORD_BOT_TOKEN|OPENAI_API_KEY|LINKEDIN_ACCESS_TOKEN|LINKEDIN_CLIENT_SECRET)=\S+"),
)


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command in the project root."""
    return subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def changed_files() -> list[str]:
    """Return modified, deleted, staged, and untracked non-ignored files."""
    commands = (
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
        ["git", "ls-files", "--others", "--exclude-standard"],
        ["git", "ls-files", "--deleted"],
    )
    files: set[str] = set()
    for command in commands:
        output = run(command).stdout
        files.update(line.strip() for line in output.splitlines() if line.strip())
    return sorted(files)


def scan_for_secrets(files: list[str]) -> None:
    """Abort when a changed text file appears to contain secrets."""
    offenders: list[str] = []
    for relative_path in files:
        path = PROJECT_ROOT / relative_path
        if not path.exists() or path.is_dir():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                offenders.append(relative_path)
                break

    if offenders:
        joined = "\n".join(f"- {path}" for path in offenders)
        raise SystemExit(f"Potential secrets found. Commit aborted.\n{joined}")


def run_checks(files: list[str]) -> None:
    """Run lightweight checks for changed Python files."""
    python_files = [path for path in files if path.endswith(".py") and (PROJECT_ROOT / path).exists()]
    if not python_files:
        return

    python = PROJECT_ROOT / ".venv" / "bin" / "python"
    command = [str(python) if python.exists() else sys.executable, "-m", "py_compile", *python_files]
    print("Running Python syntax checks...")
    print(run(command).stdout, end="")


def partition_files(files: list[str]) -> list[tuple[str, list[str]]]:
    """Partition changed files into task commit groups."""
    remaining = set(files)
    commits: list[tuple[str, list[str]]] = []

    for group in TASK_GROUPS:
        matched = sorted(path for path in remaining if group.matches(path))
        if matched:
            commits.append((group.message, matched))
            remaining.difference_update(matched)

    if remaining:
        commits.append(("chore: update project files", sorted(remaining)))

    return commits


def stage_and_commit(message: str, files: list[str], *, dry_run: bool) -> bool:
    """Stage and commit one task group."""
    print(f"\n== {message}")
    for path in files:
        print(f"  {path}")

    if dry_run:
        return False

    run(["git", "add", "--", *files])
    diff_result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_ROOT)
    if diff_result.returncode == 0:
        print("No staged changes for this group.")
        return False

    print(run(["git", "commit", "-m", message]).stdout, end="")
    return True


def push_current_branch(*, dry_run: bool) -> None:
    """Push the current branch to origin."""
    branch = run(["git", "branch", "--show-current"]).stdout.strip() or "main"
    remote_result = run(["git", "remote"], check=False).stdout.splitlines()
    if "origin" not in remote_result:
        raise SystemExit("No origin remote configured. Add origin before pushing.")

    if dry_run:
        print(f"\nDRY RUN: would push branch {branch} to origin.")
        return

    print(run(["git", "push", "-u", "origin", branch]).stdout, end="")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show planned commits without changing git state")
    parser.add_argument("--no-push", action="store_true", help="Commit but do not push")
    parser.add_argument("--skip-checks", action="store_true", help="Skip syntax checks")
    return parser.parse_args()


def main() -> int:
    """Run task-based commit and push workflow."""
    args = parse_args()
    files = changed_files()
    if not files:
        print("No changes to commit.")
        if not args.no_push:
            push_current_branch(dry_run=args.dry_run)
        return 0

    scan_for_secrets(files)
    if not args.skip_checks:
        run_checks(files)

    committed = False
    for message, group_files in partition_files(files):
        committed = stage_and_commit(message, group_files, dry_run=args.dry_run) or committed

    if args.no_push:
        return 0

    if committed:
        push_current_branch(dry_run=args.dry_run)
    else:
        print("No commits created; skipping push.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
