# gemini-api

Wrapper + Claude Code skill for [HanaokaYuzu/Gemini-API](https://github.com/HanaokaYuzu/Gemini-API) (`gemini_webapi`).

## Setup
**Recommended (reliable):** create a key at https://aistudio.google.com/apikey and run `setx GEMINI_API_KEY "<key>"` (Windows) or `export GEMINI_API_KEY=...`. The CLI uses it automatically. The cookie steps below are the unofficial fallback and can break when Google changes things.

1. Linux/macOS: `bash scripts/install-skill.sh`; Windows PowerShell: `powershell -ExecutionPolicy Bypass -File scripts\install-skill.ps1` — installs `gemini-cli` and the global skill in `~/.claude/skills/gemini-api`.
2. Get cookies: log in at https://gemini.google.com (Firefox private window recommended), DevTools → Network → any request → copy `__Secure-1PSID` and `__Secure-1PSIDTS`.
3. Export `GEMINI_SECURE_1PSID` and `GEMINI_SECURE_1PSIDTS` (see `.env.example`; never commit them).
4. Test: `gemini-cli "Reply with OK"`.

## Cloud sessions
Add the two variables in the Claude environment settings, allow host `gemini.google.com`, and use a setup script that runs `scripts/install-skill.sh` after cloning this repo.

## Setup on another PC
Step-by-step commands: [docs/SETUP.md](docs/SETUP.md)

## Tests
`pip install -e .[dev] && pytest -q`
