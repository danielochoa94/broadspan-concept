# BroadSpan Capital: website concept

Redesign concept for [brocap.com](https://brocap.com), built from the live site's content.

- `./build.sh` regenerates `site/` from `ref/` (scraped content, gitignored) and `src/pages/`.
- `site/` is static and deploys to GitHub Pages on push to `main`.
- Preview locally: `python3 -m http.server -d site 8765`.
