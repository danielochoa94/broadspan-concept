# brocap.com archive

Snapshot of the old Joomla site at brocap.com, crawled Nov 16, 2026 with wget (`wget.log`), before the cutover to the new site.

- `brocap.com/`: every public page, plus its images, CSS, scripts and the 47 PDFs under `pdf/` (press releases and research reports).
  Query strings and other characters Windows can't store in filenames became `_`, so some links between archived pages don't resolve.
- `old-urls.txt`: the 87 page URLs found by the crawl, each covered by a rule in `site/_redirects`.

Not covered: the Joomla database, admin area and anything behind the BSAM client login.
Those need a backup from the developer who hosts the site.
