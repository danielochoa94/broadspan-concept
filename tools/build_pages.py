"""Wraps src/pages/*.html bodies in the shared layout and writes them to site/."""
import os, re

BASE_URL = 'https://danielochoa94.github.io/broadspan-concept/'

NAV = [('firm.html', 'The Firm'), ('transactions.html', 'Transactions'), ('news.html', 'News')]

LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0b1a2e">
<meta property="og:type" content="website">
<meta property="og:site_name" content="BroadSpan Capital">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body data-page="{page}">
<div class="concept">Design concept<span class="long"> for BroadSpan Capital</span> &middot; Preview only, not the live site</div>
<header class="site-header">
  <div class="wrap">
    <a class="wordmark" href="index.html" aria-label="BroadSpan Capital home">
      <span class="wm-top">BroadSpan</span><span class="wm-rule"></span><span class="wm-bottom">Capital</span>
    </a>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
    <nav class="nav" id="nav">
{nav}
      <a class="nav-cta" href="index.html#contact">Contact</a>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <a class="wordmark" href="index.html" aria-label="BroadSpan Capital home">
        <span class="wm-top">BroadSpan</span><span class="wm-rule"></span><span class="wm-bottom">Capital</span>
      </a>
      <div class="footer-links">
{footer_nav}
        <a href="index.html#contact">Contact</a>
        <a href="https://brocap.com/bsam/" target="_blank" rel="noopener">BroadSpan Asset Management ↗</a>
        <a href="mailto:info@brocap.com">info@brocap.com</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>BroadSpan Securities LLC is a member of FINRA and SIPC. BroadSpan&rsquo;s asset management activities are conducted through BroadSpan Asset Management LLC.</p>
      <p>&copy; 2026 BroadSpan Capital</p>
    </div>
  </div>
</footer>
<dialog class="bio" aria-labelledby="bio-title">
  <button class="bio-close" type="button" aria-label="Close">&times;</button>
  <div class="bio-inner bio-content"></div>
</dialog>
<script src="assets/js/data.js"></script>
<script src="assets/js/site.js"></script>
</body>
</html>"""


def main():
  src = 'src/pages'
  for f in sorted(os.listdir(src)):
    raw = open(os.path.join(src, f)).read()
    meta, body = raw.split('\n---\n', 1)
    m = dict(re.findall(r'^(\w+):\s*(.*)$', meta, re.M))
    nav = '\n'.join(f'      <a href="{h}"{" aria-current=\"page\"" if h == f else ""}>{t}</a>' for h, t in NAV)
    footer_nav = '\n'.join(f'        <a href="{h}">{t}</a>' for h, t in NAV)
    html = LAYOUT.format(
      title=m['title'], og_title=m.get('og_title', m['title']), description=m['description'], page=m['page'],
      url=BASE_URL + ('' if f == 'index.html' else f), base=BASE_URL, nav=nav, footer_nav=footer_nav,
      body=body.strip('\n'))
    open(os.path.join('site', f), 'w').write(html)
    print('built', f)


main()
