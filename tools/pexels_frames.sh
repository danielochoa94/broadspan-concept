#!/usr/bin/env bash
# Usage: tools/pexels_frames.sh <id>...  -> ref/stock/frames/<id>.jpg (frame at 3s) and ref/stock/urls.txt
for id in "$@"; do
  url=$(curl -sI "https://www.pexels.com/download/video/$id/" | grep -i '^location' | tr -d '\r' | cut -d' ' -f2)
  echo "$id $url" >> ref/stock/urls.txt
  ffmpeg -loglevel error -y -ss 3 -i "$url" -frames:v 1 -vf scale=480:-2 "ref/stock/frames/$id.jpg" &
done
wait
