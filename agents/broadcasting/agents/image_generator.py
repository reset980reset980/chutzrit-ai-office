"""Image Generator Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .types import JSONDict
from agents.broadcasting.pipeline.config import RuntimeConfig


class ImageClient(Protocol):
    """Minimal image client interface used by the Image Generator Agent."""

    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        *,
        size: str,
        quality: str,
    ) -> dict[str, str]:
        """Generate one image and write it to output_path."""


class ImageGeneratorAgent:
    """Generate image files from approved image prompts."""

    name = "ImageGeneratorAgent"

    def __init__(self, config: RuntimeConfig, image_client: ImageClient) -> None:
        self.config = config
        self.image_client = image_client

    def run(self, image_prompts: JSONDict, output_path: Path) -> JSONDict:
        """Generate visual assets under the saved package directory."""
        prompts = image_prompts.get("prompts", {})
        if not isinstance(prompts, dict) or not prompts:
            return {
                "status": "skipped",
                "reason": "이미지 프롬프트가 없어 이미지 생성을 건너뛰었다.",
                "assets": {},
            }

        visuals_dir = output_path / "visuals"
        visuals_dir.mkdir(parents=True, exist_ok=True)
        assets: dict[str, dict[str, str]] = {}
        failures: dict[str, str] = {}

        for channel, spec in prompts.items():
            if channel not in {"blog", "linkedin", "telegram"} or not isinstance(spec, dict):
                continue
            prompt = str(spec.get("prompt", "")).strip()
            if not prompt:
                failures[channel] = "empty_prompt"
                continue

            file_path = visuals_dir / f"{channel}.png"
            size = str(spec.get("size") or self.config.image_size)
            quality = str(spec.get("quality") or self.config.image_quality)
            try:
                result = self.image_client.generate_image(
                    prompt,
                    file_path,
                    size=size,
                    quality=quality,
                )
            except Exception as exc:  # noqa: BLE001
                failures[channel] = f"{type(exc).__name__}: {exc}"
                continue

            assets[channel] = {
                "status": "generated",
                "path": str(file_path),
                "relative_path": str(file_path.relative_to(output_path)),
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "provider": result.get("provider", "openai_images"),
                "model": result.get("model", self.config.image_model),
            }

        status = "generated" if assets and not failures else "partial" if assets else "failed"
        return {
            "status": status,
            "assets": assets,
            "failures": failures,
        }
