#!/usr/bin/env bash
# Adobe Substance 3D + Audition Wine Panel installer (Arch Linux)
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="/opt/adobe-wine-panel"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "▸ Installing Python deps (PyQt6)..."
python3 -m pip install --user -r "$REPO_DIR/requirements.txt" 2>/dev/null || pip install --user -r "$REPO_DIR/requirements.txt"

echo "▸ Installing to $TARGET (needs sudo)..."
sudo install -d "$TARGET"
sudo install -m 0755 "$REPO_DIR/adobe-wine-panel.py" "$TARGET/adobe-wine-panel.py"

echo "▸ Installing desktop entry + icon..."
mkdir -p "$DESKTOP_DIR" "$ICON_DIR"
sed "s|/opt/adobe-wine-panel/adobe-wine-panel.py|$TARGET/adobe-wine-panel.py|" "$REPO_DIR/adobe-wine-panel.desktop" > "$DESKTOP_DIR/adobe-wine-panel.desktop"
chmod 0755 "$DESKTOP_DIR/adobe-wine-panel.desktop"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "✔ Done. Run: python3 $TARGET/adobe-wine-panel.py"
echo "  Optional custom prefix: WINEPREFIX=~/wine-adobe python3 $TARGET/adobe-wine-panel.py"
