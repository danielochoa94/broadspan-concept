#!/usr/bin/env bash
# Usage: tools/shot.sh <path> <width> <height> <outfile> [full]
export XDG_CACHE_HOME=/home/daniel/projects/.cache PLAYWRIGHT_BROWSERS_PATH=/home/daniel/projects/.cache/ms-playwright
pw() { playwright-cli -s=shots "$@" >/dev/null 2>&1; }
pw resize "$2" "$3"
pw goto "http://localhost:8765/$1"
sleep 2.5
pw eval "async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } window.scrollTo(0, 0); document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')); return 1; }"
sleep 0.8
if [ "${5:-}" = full ]; then
  playwright-cli -s=shots screenshot --full-page --filename="$4" 2>&1 | grep -i error
else
  playwright-cli -s=shots screenshot --filename="$4" 2>&1 | grep -i error
fi
true
