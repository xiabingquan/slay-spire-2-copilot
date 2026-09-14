#!/usr/bin/env bash
# Build SpireBridge and verify it is installed into the STS2 mods folder.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MOD_DIR="$ROOT/mod/SpireBridge"
GAME_MODS="${GAME_MODS_DIR:-$HOME/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/MacOS/mods}"
TARGET="$GAME_MODS/mimo-spire-bridge"

dotnet build "$MOD_DIR/SpireBridge.csproj" -c Release

if [ ! -f "$TARGET/mimo-spire-bridge.dll" ] || [ ! -f "$TARGET/mimo-spire-bridge.json" ]; then
  echo "ERROR: mod files missing under $TARGET" >&2
  exit 1
fi
echo "OK: mod installed at $TARGET"
ls -la "$TARGET"
