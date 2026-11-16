# BroadSpan Capital: website concept

Redesign concept for [brocap.com](https://brocap.com), built from the live site's content.

- `./build.sh` regenerates `src/data/` from `ref/` (scraped content, gitignored), then renders `src/pages/` and `src/data/` into static HTML in `site/`, with `sitemap.xml`, `robots.txt`, `llms.txt` and `llms-full.txt`.
- `site/` is static and deploys to GitHub Pages on push to `main` as the hidden preview.
- Netlify (`netlify.toml`) runs the production build itself from the committed `src/` data and serves `site/`, so the repo's `site/` stays the preview.
  `site/_redirects` sends the old Joomla URLs to the new pages, and `site/pdf/` keeps the old PDFs at their original paths.
- Both contact forms post to Netlify Forms; set the notification email in the Netlify UI.
  The preview build has no backend, so its forms only show the confirmation.
- `archive/` is a snapshot of the old site; see its README.
- `PRODUCTION=1 ./build.sh` builds for brocap.com: crawlers allowed, canonical URLs and sitemap on brocap.com, no preview banner. The default build stays hidden from search engines.
- Preview locally: `python3 -m http.server -d site 8765`.
