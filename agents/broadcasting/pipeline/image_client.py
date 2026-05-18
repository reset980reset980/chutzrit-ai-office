"""OpenAI image generation client for broadcasting visuals."""

from __future__ import annotations

import base64
from pathlib import Path
from urllib.request import urlopen

from openai import OpenAI, OpenAIError


class ImageGenerationError(RuntimeError):
    """Raised when image generation fails or returns no usable image."""


class OpenAIImageClient:
    """Generate images with the official OpenAI SDK."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key, timeout=180.0)
        self.model = model

    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        *,
        size: str,
        quality: str,
    ) -> dict[str, str]:
        """Generate one image and write it to output_path."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )
        except OpenAIError as exc:
            raise ImageGenerationError(f"OpenAI image generation failed: {exc}") from exc

        if not response.data:
            raise ImageGenerationError("OpenAI image response did not include image data")

        first = response.data[0]
        b64_json = getattr(first, "b64_json", None)
        image_url = getattr(first, "url", None)
        if b64_json:
            output_path.write_bytes(base64.b64decode(b64_json))
        elif image_url:
            with urlopen(image_url, timeout=60) as response_body:  # noqa: S310
                output_path.write_bytes(response_body.read())
        else:
            raise ImageGenerationError("OpenAI image response had neither b64_json nor url")

        return {
            "provider": "openai_images",
            "model": self.model,
        }
