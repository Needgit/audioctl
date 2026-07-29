#!/usr/bin/env bash
set -euo pipefail

# Installs the venv-aware audioctl wrapper to ~/.local/bin/audioctl
# Usage: ./scripts/install-wrapper.sh [repo-path]

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	cat <<'USAGE'
Usage: install-wrapper.sh [repo-path]

Installs the venv-aware audioctl wrapper to ~/.local/bin/audioctl.
If no repo-path is given, the script assumes the project root is the parent
directory of the script (i.e. the repository root).
USAGE
	exit 0
fi

REPO_PATH=${1:-"$(cd "$(dirname "$0")/.." && pwd)"}
TARGET_DIR=${HOME}/.local/bin
TARGET=${TARGET_DIR}/audioctl
TEMPLATE_DIR=$(cd "$(dirname "$0")" && pwd)
TEMPLATE=${TEMPLATE_DIR}/audioctl-wrapper.template

mkdir -p "$TARGET_DIR"
sed "s|@REPO@|$REPO_PATH|g" "$TEMPLATE" > "$TARGET"
chmod +x "$TARGET"
echo "Installed wrapper to $TARGET"
