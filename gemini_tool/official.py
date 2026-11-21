"""Backend using Google's official Gemini API (google-genai SDK) with an API key."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ENV_API_KEY = "GEMINI_API_KEY"
ENV_MODEL = "GEMINI_MODEL"
DEFAULT_MODEL = "gemini-3.8-flash"
ENV_FALLBACKS = "GEMINI_FALLBACK_MODELS"
DEFAULT_FALLBACKS = "gemini-3.5-flash,gemini-3.5-flash-lite"
RETRYABLE_STATUS_CODES = {429, 500, 503}
RETRIES_PER_MODEL = 2
BACKOFF_BASE_SEC = 2


class MissingApiKeyError(RuntimeError):
    """Raised when GEMINI_API_KEY is not set."""


def has_api_key() -> bool:
    return bool(os.environ.get(ENV_API_KEY, "").strip())


def _client():
    from google import genai  # lazy import

    key = os.environ.get(ENV_API_KEY, "").strip()
    if not key:
        raise MissingApiKeyError(
            f"{ENV_API_KEY} is not set. Create a key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=key)


async def ask(prompt: str, files: list[str | Path] | None = None, model: str | None = None) -> str:
    client = _client()
    contents: list = []
    for path in files or []:
        contents.append(await client.aio.files.upload(file=str(path)))
    contents.append(prompt)
    last_error: Exception | None = None
    for candidate in candidate_models(model):
        for attempt in range(RETRIES_PER_MODEL + 1):
            try:
                response = await client.aio.models.generate_content(
                    model=candidate, contents=contents
                )
                return response.text or ""
            except Exception as exc:
                if getattr(exc, "code", None) not in RETRYABLE_STATUS_CODES:
                    raise
                last_error = exc
                if attempt < RETRIES_PER_MODEL:
                    await asyncio.sleep(BACKOFF_BASE_SEC * 2**attempt)
        print(f"warning: {candidate} unavailable, trying next model", file=sys.stderr)
    assert last_error is not None
    raise last_error


def candidate_models(explicit: str | None) -> list[str]:
    """Explicit --model is used alone; otherwise default followed by fallbacks."""
    if explicit:
        return [explicit]
    primary = os.environ.get(ENV_MODEL, "").strip() or DEFAULT_MODEL
    fallbacks = os.environ.get(ENV_FALLBACKS, DEFAULT_FALLBACKS)
    chain = [primary] + [m.strip() for m in fallbacks.split(",") if m.strip()]
    return list(dict.fromkeys(chain))  # dedupe, keep order


async def list_models() -> list[str]:
    client = _client()
    return [m.name for m in client.models.list()]
