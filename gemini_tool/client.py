"""Credential loading and one-shot prompting via gemini_webapi."""
from __future__ import annotations

import os
from pathlib import Path

ENV_PSID = "GEMINI_SECURE_1PSID"
ENV_PSIDTS = "GEMINI_SECURE_1PSIDTS"
INIT_TIMEOUT_SEC = 30


class MissingCredentialsError(RuntimeError):
    """Raised when the Gemini cookie env vars are not set."""


def load_credentials() -> tuple[str, str | None]:
    psid = os.environ.get(ENV_PSID, "").strip()
    if not psid:
        raise MissingCredentialsError(
            f"{ENV_PSID} is not set. Copy the __Secure-1PSID cookie from "
            "gemini.google.com (see README) and export it."
        )
    return psid, os.environ.get(ENV_PSIDTS, "").strip() or None


async def create_client():
    from gemini_webapi import GeminiClient  # lazy: keeps --help/tests fast

    psid, psidts = load_credentials()
    client = GeminiClient(psid, psidts)
    await client.init(timeout=INIT_TIMEOUT_SEC, auto_close=False, auto_refresh=False)
    return client


async def ask(
    prompt: str,
    files: list[str | Path] | None = None,
    model: str | None = None,
    temporary: bool = True,
) -> str:
    client = await create_client()
    try:
        kwargs: dict = {"temporary": temporary}
        if files:
            kwargs["files"] = [Path(f) for f in files]
        if model:
            kwargs["model"] = client.resolve_model(model)
        response = await client.generate_content(prompt, **kwargs)
        return response.text
    finally:
        await client.close()


async def list_models() -> list[str]:
    client = await create_client()
    try:
        return [str(m) for m in client.list_models()]
    finally:
        await client.close()
