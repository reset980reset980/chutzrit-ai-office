"""Runtime status file updates for the office dashboard."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .storage import OUTPUT_ROOT


STATUS_PATH = OUTPUT_ROOT / "logs" / "current-status.json"

AGENT_IDS = [
    "input-parser",
    "content-strategy",
    "insight",
    "blog-writer",
    "linkedin-writer",
    "telegram-newsletter",
    "self-reflection",
    "revision",
    "visual-strategy",
    "image-prompt",
    "image-generator",
    "visual-quality",
    "publish",
]

AGENT_DEFAULT_TASKS = {
    "input-parser": "새 입력을 기다리고 있다.",
    "content-strategy": "콘텐츠 방향 설계 대기 중이다.",
    "insight": "후츠릿 관점 보강 대기 중이다.",
    "blog-writer": "블로그 원고 작성 대기 중이다.",
    "linkedin-writer": "LinkedIn 원고 작성 대기 중이다.",
    "telegram-newsletter": "Telegram 뉴스레터 원고 작성 대기 중이다.",
    "self-reflection": "품질 평가 대기 중이다.",
    "revision": "수정 대상 원고 대기 중이다.",
    "visual-strategy": "이미지 콘셉트 설계 대기 중이다.",
    "image-prompt": "이미지 프롬프트 작성 대기 중이다.",
    "image-generator": "대표 이미지 생성 대기 중이다.",
    "visual-quality": "이미지 적합성 평가 대기 중이다.",
    "publish": "배포 작업 대기 중이다.",
}


def start_runtime_status(*, run_id: str, source: str, source_summary: str) -> None:
    """Create a dashboard status record for a new content job."""
    now = current_timestamp()
    agents = {
        agent_id: {
            "id": agent_id,
            "status": "IDLE",
            "currentTask": AGENT_DEFAULT_TASKS[agent_id],
            "recentOutput": "",
            "nextTask": "현재 작업 단계가 끝나면 다음 에이전트로 넘긴다.",
            "updatedAt": now,
        }
        for agent_id in AGENT_IDS
    }
    agents["input-parser"].update(
        {
            "status": "WORKING",
            "currentTask": "Telegram 입력을 분석하고 링크와 메모를 분리한다.",
            "recentOutput": source_summary,
            "updatedAt": now,
        }
    )
    write_status(
        {
            "runId": run_id,
            "source": source,
            "active": True,
            "updatedAt": now,
            "agents": agents,
        }
    )


def record_runtime_progress(*, run_id: str, source: str, message: str) -> None:
    """Update dashboard status from one progress message."""
    status = read_status()
    if status.get("runId") != run_id:
        start_runtime_status(run_id=run_id, source=source, source_summary="")
        status = read_status()

    now = current_timestamp()
    status["active"] = True
    status["source"] = source
    status["updatedAt"] = now
    agents = status.setdefault("agents", {})

    for agent_id, update in infer_agent_updates(message).items():
        agent = agents.setdefault(agent_id, {"id": agent_id})
        agent.update(update)
        agent["updatedAt"] = now

    write_status(status)


def complete_runtime_status(*, run_id: str, output_path: Path | str | None = None) -> None:
    """Mark the runtime job as complete and leave recent outputs visible."""
    status = read_status()
    if status.get("runId") != run_id:
        return

    now = current_timestamp()
    status["active"] = False
    status["updatedAt"] = now
    status["outputPath"] = str(output_path or "")
    agents = status.setdefault("agents", {})
    for agent_id in AGENT_IDS:
        agent = agents.setdefault(agent_id, {"id": agent_id})
        agent["id"] = agent_id
        agent["status"] = "IDLE"
        agent.setdefault("recentOutput", "")
        agent["currentTask"] = "작업 완료. 다음 Telegram 입력을 기다린다."
        agent["nextTask"] = "새 입력이 들어오면 자동으로 파이프라인을 시작한다."
        agent["updatedAt"] = now
    agents["publish"]["recentOutput"] = f"최근 산출물 {output_path}" if output_path else "최근 작업 완료"
    write_status(status)


def fail_runtime_status(*, run_id: str, error: str) -> None:
    """Mark the current runtime job as failed."""
    status = read_status()
    if status.get("runId") != run_id:
        return

    now = current_timestamp()
    status["active"] = False
    status["updatedAt"] = now
    status["error"] = error
    agents = status.setdefault("agents", {})
    publish = agents.setdefault("publish", {"id": "publish"})
    publish.update(
        {
            "status": "ERROR",
            "currentTask": "작업 중 오류가 발생했다.",
            "recentOutput": error,
            "nextTask": "로그를 확인하고 실패 원인을 수정한다.",
            "updatedAt": now,
        }
    )
    write_status(status)


def infer_agent_updates(message: str) -> dict[str, dict[str, str]]:
    """Infer agent status transitions from pipeline progress text."""
    updates: dict[str, dict[str, str]] = {}

    if "Input Parser Agent가" in message:
        updates["input-parser"] = working("Telegram 입력 분석 중", message)
    elif "Input Parser 완료" in message:
        updates["input-parser"] = idle("입력 분석 완료", message)

    if "Content Strategy Agent가" in message:
        updates["content-strategy"] = working("콘텐츠 전략 설계 중", message)
    elif "Content Strategy Agent 완료" in message:
        updates["content-strategy"] = idle("콘텐츠 전략 설계 완료", message)

    if "Insight Agent가" in message:
        updates["insight"] = working("후츠릿 관점 인사이트 정리 중", message)
    elif "Insight Agent 완료" in message:
        updates["insight"] = idle("인사이트 정리 완료", message)

    if "Platform Writer Agents가" in message:
        for agent_id in ("blog-writer", "linkedin-writer", "telegram-newsletter"):
            updates[agent_id] = working("채널별 원고 병렬 작성 중", message)
    elif "Platform Writer Agents 완료" in message:
        for agent_id in ("blog-writer", "linkedin-writer", "telegram-newsletter"):
            updates[agent_id] = idle("채널별 원고 작성 완료", message)

    if "Self Reflection Agent가" in message:
        updates["self-reflection"] = working("품질 평가 중", message)
    elif "콘텐츠배포팀 평가 결과" in message:
        status = "IDLE" if "상태 통과" in message else "REVIEW"
        updates["self-reflection"] = {
            "status": status,
            "currentTask": "품질 평가 완료",
            "recentOutput": compact(message),
            "nextTask": "기준 미달 채널은 Revision Agent가 수정한다.",
        }

    if "Revision Agent" in message and "시작" in message:
        updates["revision"] = working("기준 미달 원고 수정 중", message)
    elif "Revision Agent" in message and "완료" in message:
        updates["revision"] = idle("수정 완료", message)

    if "Visual Strategy Agent가" in message:
        updates["visual-strategy"] = working("이미지 콘셉트 설계 중", message)
    elif "Visual Strategy Agent 완료" in message:
        updates["visual-strategy"] = idle("이미지 콘셉트 설계 완료", message)

    if "Image Prompt Agent가" in message:
        updates["image-prompt"] = working("채널별 이미지 프롬프트 작성 중", message)
    elif "Image Prompt Agent 완료" in message:
        updates["image-prompt"] = idle("이미지 프롬프트 작성 완료", message)

    if "Image Generator Agent가" in message:
        updates["image-generator"] = working("대표 이미지 생성 중", message)

    if "Visual Quality Agent가" in message:
        updates["image-generator"] = idle("대표 이미지 생성 완료", message)
        updates["visual-quality"] = working("이미지 적합성 평가 중", message)
    elif "Visual Quality Agent 완료" in message:
        updates["visual-quality"] = idle("이미지 적합성 평가 완료", message)

    if "Final Quality Gate" in message:
        updates["self-reflection"] = idle("최종 품질 게이트 완료", message)
        updates["publish"] = working("이미지 제작 후 배포 계획 정리 대기 중", message)

    if "Publish Agent" in message:
        updates["publish"] = working("채널별 배포 계획 정리 중", message)

    if "파일 저장 완료" in message or "최종 배포물" in message:
        updates["publish"] = working("최종 산출물 저장 및 Telegram 발송 중", message)

    return updates


def working(task: str, message: str) -> dict[str, str]:
    """Build a working status update."""
    return {
        "status": "WORKING",
        "currentTask": task,
        "recentOutput": compact(message),
        "nextTask": "현재 단계 완료 후 다음 에이전트로 넘긴다.",
    }


def idle(task: str, message: str) -> dict[str, str]:
    """Build an idle status update that preserves the latest output."""
    return {
        "status": "IDLE",
        "currentTask": task,
        "recentOutput": compact(message),
        "nextTask": "다음 단계의 에이전트가 이어서 처리한다.",
    }


def compact(message: str, limit: int = 220) -> str:
    """Compact multiline progress text for dashboard cards."""
    text = " ".join(str(message or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def read_status() -> dict[str, Any]:
    """Read the current runtime status file."""
    try:
        data = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_status(status: dict[str, Any]) -> None:
    """Write the current runtime status file atomically."""
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = STATUS_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(STATUS_PATH)


def current_timestamp() -> str:
    """Return an ISO timestamp for status records."""
    return datetime.now().isoformat(timespec="seconds")
