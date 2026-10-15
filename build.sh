#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -I tools/build_data.py
python3 -I tools/build_texture.py
python3 -I tools/build_alliance.py
python3 -I tools/build_pages.py
