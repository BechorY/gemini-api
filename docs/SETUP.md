# Gemini API + Claude skill — setup on a new PC

Ordered commands to reproduce the working setup: `gemini-cli` + the global Claude Code skill
`gemini-api`, using the **official Gemini API key**. About 5 minutes.
Never paste keys or cookies into chat, and never commit them.

## Windows (PowerShell)

### 1. Prerequisites
Install [Git](https://git-scm.com/download/win) and [Python 3.10+](https://www.python.org/downloads/), then check both:
```powershell
git --version
py --version
```

### 2. Clone the repo
```powershell
cd $env:USERPROFILE
git clone https://github.com/BechorY/gemini-api.git
cd gemini-api
```

### 3. Install the CLI and the global skill
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-skill.ps1
```
This installs `gemini-cli` and copies the skill to `%USERPROFILE%\.claude\skills\gemini-api`,
so the skill works in every local project.

### 4. Put `gemini-cli` on PATH
Do not use `setx PATH` here: it truncates long PATH values at 1024 characters.
```powershell
$scripts = py -c "import sysconfig;print(sysconfig.get_path('scripts','nt_user'))"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$scripts*") { [Environment]::SetEnvironmentVariable("Path", "$userPath;$scripts", "User") }
$env:PATH += ";$scripts"
```

### 5. Set the API key
Create a key at https://aistudio.google.com/apikey, then replace `PASTE_KEY_HERE` with it:
```powershell
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "PASTE_KEY_HERE", "User")
$env:GEMINI_API_KEY = "PASTE_KEY_HERE"
```

### 6. Test
```powershell
gemini-cli "Reply with OK"
```
Expected output: `OK`. If the default model is busy, you may first see a
`warning: ... trying next model` line; that is normal.

### 7. Verify the Claude skill
```powershell
Test-Path "$env:USERPROFILE\.claude\skills\gemini-api\SKILL.md"
```
Expected output: `True`. Then open Claude Code in any project and say: *ask Gemini to reply with OK*.

### Update later
```powershell
cd $env:USERPROFILE\gemini-api
git pull
powershell -ExecutionPolicy Bypass -File scripts\install-skill.ps1
```

## Linux / macOS
```bash
git clone https://github.com/BechorY/gemini-api.git && cd gemini-api
bash scripts/install-skill.sh
echo 'export GEMINI_API_KEY="PASTE_KEY_HERE"' >> ~/.bashrc   # or ~/.zshrc
export GEMINI_API_KEY="PASTE_KEY_HERE"
export PATH="$HOME/.local/bin:$PATH"
gemini-cli "Reply with OK"
```

## Useful commands
| Command | Purpose |
|---|---|
| `gemini-cli "prompt"` | Ask Gemini (default model `gemini-3.8-flash`, auto-fallback) |
| `gemini-cli --model gemini-3.5-flash-lite "prompt"` | Use one specific model, no fallback |
| `gemini-cli --file .\doc.pdf "Summarize this"` | Attach a file (repeat `--file` for more) |
| `gemini-cli --json "prompt"` | Output as JSON `{"text": ...}` |
| `gemini-cli --list-models` | List models your key can use |

Optional settings (user environment variables): `GEMINI_MODEL` overrides the default model, and
`GEMINI_FALLBACK_MODELS` (comma-separated) sets the fallback order.

## Troubleshooting (issues already solved once)
| Symptom | Cause | Fix |
|---|---|---|
| `'gemini-cli' is not recognized` | PATH not updated in this window | Open a new window, or redo step 4 |
| `'bash' is not recognized` | Windows has no bash | Use the `.ps1` installer (step 3) |
| `No module named 'gemini_webapi'` when running `python ...` | `python` is a different interpreter than `py` | Use `py`, not `python` |
| `GEMINI_API_KEY is not set` (exit code 2) | Key missing in this window | Redo step 5 |
| `404 NOT_FOUND ... model ... not found / no longer available` | Model retired for your key | Run `gemini-cli --list-models`, then pass `--model <name>` |
| `400 ... unexpected model name format` | `GEMINI_MODEL` holds a placeholder or invalid value | `[Environment]::SetEnvironmentVariable("GEMINI_MODEL", $null, "User")` then `Remove-Item Env:GEMINI_MODEL` |
| `setx ... ""` gives `ERROR: Invalid syntax` | `setx` cannot clear a variable | Use `[Environment]::SetEnvironmentVariable("NAME", $null, "User")` |
| `503 UNAVAILABLE ... high demand` | Google-side load | Retried automatically; if every model fails, try again later |

## Optional: cookie backend (unofficial, not recommended)
The repo also includes the [HanaokaYuzu/Gemini-API](https://github.com/HanaokaYuzu/Gemini-API) cookie backend
(`--backend cookies`, env vars `GEMINI_SECURE_1PSID` and `GEMINI_SECURE_1PSIDTS`). On this account Google
rejected the cookies with HTTP 400, so use the API key instead. If you try it anyway, copy the cookies from a
**Firefox private window**: cookies from Edge or Chrome are device-bound and expire fast.

## Cloud sessions (claude.ai/code)
Already configured in the Default environment: host `generativelanguage.googleapis.com` is allowed, and a
setup script installs the skill. The API key goes in environment **Edit → Network secrets**:
host `generativelanguage.googleapis.com`, header `x-goog-api-key`.
