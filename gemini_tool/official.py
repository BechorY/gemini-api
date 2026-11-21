"""Backend using Google's official Gemini API (google-genai SDK) with an API key."""
from __future__ import annotations

import os
from pathlib import Path

ENV_API_KEY = "GEMINI_API_KEY"
ENV_MODEL = "GEMINI_MODEL"
DEFAULT_MODEL = "gemini-2.5-flash"


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
    response = await client.aio.models.generate_content(
        model=model or os.environ.get(ENV_MODEL) or DEFAULT_MODEL, contents=contents
    )
    return response.text or ""


async def list_models() -> list[str]:
    client = _client()
    return [m.name for m in client.models.list()]
