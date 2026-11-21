# Idempotent (Windows PowerShell): installs gemini-cli and the global Claude skill.
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
$ClaudeHome = if ($env:CLAUDE_HOME) { $env:CLAUDE_HOME } else { Join-Path $env:USERPROFILE ".claude" }
$Dest = Join-Path $ClaudeHome "skills\gemini-api"

$py = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { throw "Python 3.10+ not found. Install from python.org first." }
& $py -m pip install --user --quiet -e $Repo
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null
if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
Copy-Item -Recurse (Join-Path $Repo "skills\gemini-api") $Dest

$scripts = & $py -c "import sysconfig;print(sysconfig.get_path('scripts','nt_user'))"
Write-Host "Skill installed: $Dest\SKILL.md"
Write-Host "Add to PATH if gemini-cli is not found: $scripts"
Write-Host "Then set cookies (persistent):"
Write-Host '  setx GEMINI_SECURE_1PSID "<value>"'
Write-Host '  setx GEMINI_SECURE_1PSIDTS "<value>"'
Write-Host "Open a NEW terminal and run: gemini-cli 'Reply with OK'"
