"""gemini-cli: ask Gemini from the terminal."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from gemini_tool import client as cookie_backend
from gemini_tool import official
from gemini_tool.client import MissingCredentialsError

EXIT_OK, EXIT_API_ERROR, EXIT_NO_CREDS = 0, 1, 2
OVERALL_TIMEOUT_SEC = 120


def run(coro):
    """Run a coroutine on a Selector loop (curl_cffi stalls on Windows' Proactor loop)."""
    async def guarded():
        return await asyncio.wait_for(coro, OVERALL_TIMEOUT_SEC)

    return asyncio.run(guarded(), loop_factory=asyncio.SelectorEventLoop)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gemini-cli", description="Ask Gemini via gemini_webapi.")
    p.add_argument("prompt", nargs="?", help="Prompt text (reads stdin if omitted)")
    p.add_argument("--file", "-f", action="append", default=[], help="Attach file (repeatable)")
    p.add_argument("--model", "-m", help="Model name, e.g. pro, flash")
    p.add_argument(
        "--backend", choices=["auto", "official", "cookies"], default="auto",
        help="auto: official API if GEMINI_API_KEY is set, else cookies (default)",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON {text: ...}")
    p.add_argument("--save-history", action="store_true", help="Save chat in Gemini history")
    p.add_argument("--list-models", action="store_true", help="List models and exit")
    return p


def pick_backend(choice: str):
    if choice == "official" or (choice == "auto" and official.has_api_key()):
        return official
    return cookie_backend


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    backend = pick_backend(args.backend)
    try:
        if args.list_models:
            print("\n".join(run(backend.list_models())))
            return EXIT_OK
        prompt = args.prompt if args.prompt is not None else sys.stdin.read()
        if not prompt.strip():
            print("error: empty prompt", file=sys.stderr)
            return EXIT_API_ERROR
        kwargs = {} if backend is official else {"temporary": not args.save_history}
        text = run(backend.ask(prompt, files=args.file, model=args.model, **kwargs))
    except (MissingCredentialsError, official.MissingApiKeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_NO_CREDS
    except TimeoutError:
        print(f"error: no response within {OVERALL_TIMEOUT_SEC}s", file=sys.stderr)
        return EXIT_API_ERROR
    except Exception as exc:  # network/auth/API failures
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_API_ERROR
    print(json.dumps({"text": text}, ensure_ascii=False) if args.json else text)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
