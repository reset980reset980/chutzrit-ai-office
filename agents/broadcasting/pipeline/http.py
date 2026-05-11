"""Small HTTP helpers used by the broadcasting pipeline."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class HttpRequestError(RuntimeError):
    """Raised when an HTTP request fails."""


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    """Send an HTTP request and parse a JSON response."""
    request_headers = {
        "Accept": "application/json",
        "User-Agent": "ChutzritAIOffice/0.1 (broadcasting-pipeline; Python urllib)",
    }
    if headers:
        request_headers.update(headers)

    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    req = Request(url=url, data=body, headers=request_headers, method=method)

    try:
        with urlopen(req, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
            if not response_body:
                return {"ok": True, "status": response.status}
            return json.loads(response_body)
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise HttpRequestError(f"HTTP {exc.code} from {url}: {error_body[:800]}") from exc
    except URLError as exc:
        raise HttpRequestError(f"Network error for {url}: {exc.reason}") from exc
