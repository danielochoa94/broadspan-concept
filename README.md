# BroadSpan Capital: website concept

Redesign concept for [brocap.com](https://brocap.com), built from the live site's content.

- `./build.sh` regenerates `src/data/` from `ref/` (scraped content, gitignored), then renders `src/pages/` and `src/data/` into static HTML in `site/`, with `sitemap.xml`, `robots.txt`, `llms.txt` and `llms-full.txt`.
- `site/` is static and deploys to GitHub Pages on push to `main`.
- `PRODUCTION=1 ./build.sh` builds for brocap.com: crawlers allowed, canonical URLs and sitemap on brocap.com, no preview banner. The default build stays hidden from search engines.
- Preview locally: `python3 -m http.server -d site 8765`.
