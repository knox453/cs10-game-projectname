#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --user -r requirements.txt pyinstaller
python3 -m PyInstaller --onefile --windowed --name OneLongDay game.py

echo "Mac build complete:"
echo "  dist/OneLongDay"
echo "  dist/OneLongDay.app"
