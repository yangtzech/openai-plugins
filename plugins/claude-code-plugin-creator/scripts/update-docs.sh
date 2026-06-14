#!/usr/bin/env bash
# Fetch the latest Claude Code plugin documentation from ericbuess/claude-code-docs
# into the references/ directory. Run this periodically to stay up-to-date.
#
# Usage:
#   bash plugins/plugin-creator/scripts/update-docs.sh
#   bash plugins/plugin-creator/scripts/update-docs.sh --check   # just check for updates
#
# Mirror fallback: if GitHub is unreachable, automatically falls back to
# https://gitcode.com/gh_mirrors/cl/claude-code-docs

set -euo pipefail

REPO="ericbuess/claude-code-docs"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/docs"
MIRROR_URL="https://gitcode.com/gh_mirrors/cl/claude-code-docs/raw/${BRANCH}/docs"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REF_DIR="${SCRIPT_DIR}/../references"

# Docs relevant to plugin development
DOCS=(
  "plugins.md"
  "plugins-reference.md"
  "skills.md"
  "sub-agents.md"
  "hooks.md"
  "hooks-guide.md"
  "plugin-marketplaces.md"
  "plugin-dependencies.md"
  "discover-plugins.md"
  "plugin-hints.md"
  "mcp.md"
  "settings.md"
)

mkdir -p "$REF_DIR"

check_only=false
if [[ "${1:-}" == "--check" ]]; then
  check_only=true
fi

# Detect which source is reachable; prefer GitHub, fall back to GitCode mirror.
echo "Checking GitHub source..."
if curl -fsSL --connect-timeout 5 --max-time 10 "${BASE_URL}/${DOCS[0]}" -o /dev/null 2>/dev/null; then
  SOURCE_URL="$BASE_URL"
  echo "Using GitHub source: ${BASE_URL}"
else
  echo "[!] GitHub unreachable, trying GitCode mirror..."
  if curl -fsSL --connect-timeout 5 --max-time 10 "${MIRROR_URL}/${DOCS[0]}" -o /dev/null 2>/dev/null; then
    SOURCE_URL="$MIRROR_URL"
    echo "Using GitCode mirror: ${MIRROR_URL}"
  else
    echo "[✗] Both GitHub and GitCode mirror are unreachable. Please check your network."
    exit 1
  fi
fi
echo "---"

changed=0
errors=0

for doc in "${DOCS[@]}"; do
  target="${REF_DIR}/${doc}"
  tmp="${target}.tmp"

  if ! curl -fsSL "${SOURCE_URL}/${doc}" -o "$tmp" 2>/dev/null; then
    echo "  [!] ${doc} — fetch failed"
    rm -f "$tmp"
    errors=$((errors + 1))
    continue
  fi

  if $check_only; then
    if [[ -f "$target" ]]; then
      if diff -q "$target" "$tmp" >/dev/null 2>&1; then
        echo "  [=] ${doc} — up to date"
      else
        echo "  [~] ${doc} — has updates"
        changed=$((changed + 1))
      fi
    else
      echo "  [+] ${doc} — new"
      changed=$((changed + 1))
    fi
    rm -f "$tmp"
  else
    if [[ -f "$target" ]] && diff -q "$target" "$tmp" >/dev/null 2>&1; then
      echo "  [=] ${doc}"
      rm -f "$tmp"
    else
      mv "$tmp" "$target"
      if [[ -f "$target" ]]; then
        echo "  [~] ${doc} — updated"
      else
        echo "  [+] ${doc} — fetched"
      fi
      changed=$((changed + 1))
    fi
  fi
done

echo "---"
if $check_only; then
  echo "Check complete: ${changed} with updates, ${errors} errors, ${#DOCS[@]} total"
else
  echo "Done: ${changed} updated, ${errors} errors, ${#DOCS[@]} total"
  echo "Docs saved to: ${REF_DIR}"
fi
