"""Visual asset orchestration for saved broadcasting packages."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agents.broadcasting.agents.image_generator import ImageClient, ImageGeneratorAgent
from agents.broadcasting.agents.visual_quality import VisualQualityAgent
from agents.broadcasting.agents.types import JSONClient

from .config import RuntimeConfig
from .image_client import OpenAIImageClient
from .openai_client import OpenAIClient
from .prompts import build_visual_observation_prompt
from .storage import refresh_visual_files, saved_package_targets


ProgressCallback = Callable[[str], None]


def generate_visual_assets_for_saved_package(
    package: dict[str, Any],
    config: RuntimeConfig,
    draft_path: Path,
    *,
    client: JSONClient | None = None,
    image_client: ImageClient | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Generate image files for a package that has already been saved."""
    visual_assets = package.get("visual_assets", {})
    if visual_assets.get("status") != "pending_generation":
        return visual_assets

    active_image_client = image_client or OpenAIImageClient(
        api_key=config.openai_api_key,
        model=config.image_model,
    )
    active_json_client = client or OpenAIClient(api_key=config.openai_api_key, model=config.openai_model)
    emit(progress_callback, "🎨 Image Generator Agent가 대표 이미지를 생성합니다.")
    generated = ImageGeneratorAgent(config, active_image_client).run(
        package.get("image_prompts", {}),
        draft_path,
    )
    package["visual_assets"] = generated

    if generated.get("assets"):
        emit(progress_callback, "👁️ Visual Observation Agent가 실제 이미지를 확인합니다.")
        package["visual_observations"] = inspect_generated_visuals(
            active_json_client,
            package,
            draft_path,
            generated,
        )
        emit(progress_callback, "🖼️ Visual Quality Agent가 이미지 적합성을 점검합니다.")
        try:
            package["visual_quality"] = VisualQualityAgent(active_json_client).run(
                package,
                package.get("visual_strategy", {}),
                package.get("image_prompts", {}),
                generated,
                package.get("visual_observations", {}),
            )
        except Exception as exc:  # noqa: BLE001
            package["visual_quality"] = {
                "score": 0,
                "passed": False,
                "problems": [f"Visual Quality Agent 평가 실패: {type(exc).__name__}: {exc}"],
                "recommendations": ["이미지 파일은 유지하고 사람이 최종 적합성을 확인한다."],
            }
        emit(
            progress_callback,
            "## 🖼️ Visual Quality Agent 완료\n"
            f"이미지 점수 {package['visual_quality'].get('score', 'unknown')}\n"
            f"생성 이미지 {len(generated.get('assets', {}))}개",
        )
    else:
        package["visual_quality"] = {
            "score": 0,
            "passed": False,
            "problems": ["생성된 이미지가 없다."],
            "recommendations": ["이미지 생성 설정과 API 상태를 확인하라."],
        }

    sync_visual_assets(package, draft_path)
    refresh_visual_files(package, draft_path)
    return package["visual_assets"]


def sync_visual_assets(package: dict[str, Any], draft_path: Path) -> None:
    """Copy generated visual files from draft output to final output."""
    targets = saved_package_targets(package, draft_path)
    if len(targets) < 2:
        return

    source_dir = draft_path / "visuals"
    if not source_dir.exists():
        return

    for target in targets[1:]:
        target_dir = target / "visuals"
        target_dir.mkdir(parents=True, exist_ok=True)
        for source_file in source_dir.iterdir():
            if source_file.is_file():
                shutil.copy2(source_file, target_dir / source_file.name)


def inspect_generated_visuals(
    client: JSONClient,
    package: dict[str, Any],
    draft_path: Path,
    visual_assets: dict[str, Any],
) -> dict[str, Any]:
    """Inspect actual generated image pixels when the active client supports image input."""
    create_json_with_images = getattr(client, "create_json_with_images", None)
    if not callable(create_json_with_images):
        return {
            "pixel_audited": False,
            "reason": "active_json_client_does_not_support_images",
            "channels": {},
            "overall_problems": ["실제 이미지 픽셀 검수 없이 메타데이터 기반 평가만 가능하다."],
            "recommendations": ["운영 환경에서는 OpenAIClient의 이미지 입력 평가를 사용한다."],
        }

    image_paths: list[tuple[str, Path]] = []
    for channel, asset in sorted((visual_assets.get("assets") or {}).items()):
        if not isinstance(asset, dict):
            continue
        relative_path = str(asset.get("relative_path") or "")
        image_path = draft_path / relative_path
        if image_path.exists() and image_path.is_file():
            image_paths.append((channel, image_path))

    if not image_paths:
        return {
            "pixel_audited": False,
            "reason": "no_image_files_found",
            "channels": {},
            "overall_problems": ["검수할 실제 이미지 파일을 찾지 못했다."],
            "recommendations": ["visual-assets.json의 relative_path와 저장된 파일을 확인한다."],
        }

    try:
        return create_json_with_images(
            build_visual_observation_prompt(
                package,
                package.get("visual_strategy", {}),
                package.get("image_prompts", {}),
                visual_assets,
            ),
            image_paths,
            max_output_tokens=4000,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "pixel_audited": False,
            "reason": f"{type(exc).__name__}: {exc}",
            "channels": {},
            "overall_problems": ["실제 이미지 픽셀 검수 호출에 실패했다."],
            "recommendations": ["이미지 파일은 유지하고 사람이 최종 적합성을 확인한다."],
        }


def emit(progress_callback: ProgressCallback | None, message: str) -> None:
    """Emit a progress message when available."""
    if progress_callback:
        progress_callback(message)
