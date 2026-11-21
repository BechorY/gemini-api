#!/usr/bin/env bash
# Idempotent: installs gemini-cli and the global Claude skill (~/.claude/skills/gemini-api).
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${CLAUDE_HOME:-$HOME/.claude}/skills"

python3 -m pip install --user --quiet -e "$REPO" 2>/dev/null \
  || python3 -m pip install --quiet -e "$REPO"

mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/gemini-api"
cp -r "$REPO/skills/gemini-api" "$SKILLS_DIR/gemini-api"

echo "Skill installed: $SKILLS_DIR/gemini-api/SKILL.md"
echo "Verify: gemini-cli --help  (ensure ~/.local/bin is on PATH)"
echo "Then set GEMINI_SECURE_1PSID / GEMINI_SECURE_1PSIDTS and run: gemini-cli 'Reply with OK'"
