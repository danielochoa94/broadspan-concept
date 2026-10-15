"""Wraps src/pages/*.html bodies in the shared layout and writes them to site/."""
import os, re

BASE_URL = 'https://danielochoa94.github.io/broadspan-concept/'

NAV = [('firm.html', 'Who We Are'), ('transactions.html', 'Transactions'), ('alliance.html', 'Mergers Alliance'),
       ('news.html', 'News')]

LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#ffffff">
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@300&family=IBM+Plex+Sans:wght@300;400;500&family=Inter:wght@700&display=swap">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body data-page="{page}">
<div class="concept">Design concept<span class="long"> for BroadSpan Capital</span> &middot; Preview only, not the live site</div>
<header class="site-header">
  <div class="inner">
    <a class="logo" href="index.html"><img src="assets/img/logo.png" alt="BroadSpan Capital" width="325" height="86"></a>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
    <nav class="nav" id="nav">
{nav}
      <a href="index.html#contact">Contact</a>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="footer-grid">
    <div class="footer-col">
      <h4>Explore</h4>
{footer_nav}
      <a href="https://brocap.com/bsam/" target="_blank" rel="noopener">Asset Management</a>
    </div>
    <div class="footer-col">
      <h4>Offices</h4>
      <p>Miami</p><p>Mexico City</p><p>Medellín</p><p>Rio de Janeiro</p><p>São Paulo</p>
    </div>
    <div class="footer-col">
      <h4>Contact</h4>
      <a href="mailto:info@brocap.com">info@brocap.com</a>
      <p>1441 Brickell Ave, Suite 1550<br>Miami, FL 33131</p>
    </div>
    <a class="logo light" href="index.html"><img src="assets/img/logo-white.png" alt="BroadSpan Capital" width="325" height="86"></a>
  </div>
  <div class="footer-legal">
    <p>BroadSpan Securities LLC is a member of FINRA and SIPC. Asset management activities are conducted through BroadSpan Asset Management LLC.</p>
    <p>&copy; 2026 BroadSpan Capital. All rights reserved.</p>
  </div>
</footer>
<dialog class="modal" aria-label="Details">
  <button class="modal-close" type="button" aria-label="Close">&times;</button>
  <div class="modal-body"></div>
</dialog>
<script src="assets/js/data.js"></script>
{scripts}<script src="assets/js/site.js"></script>
</body>
</html>"""


def main():
  src = 'src/pages'
  for f in sorted(os.listdir(src)):
    raw = open(os.path.join(src, f)).read()
    meta, body = raw.split('\n---\n', 1)
    m = dict(re.findall(r'^(\w+):\s*(.*)$', meta, re.M))
    nav = '\n'.join(f'      <a href="{h}"{" aria-current=\"page\"" if h == f else ""}>{t}</a>' for h, t in NAV)
    footer_nav = '\n'.join(f'      <a href="{h}">{t}</a>' for h, t in [('index.html', 'Home')] + NAV)
    html = LAYOUT.format(
      title=m['title'], og_title=m.get('og_title', m['title']), description=m['description'], page=m['page'],
      url=BASE_URL + ('' if f == 'index.html' else f), base=BASE_URL, nav=nav, footer_nav=footer_nav,
      body=body.strip('\n'),
      scripts='<script src="assets/js/alliance.js"></script>\n' if m['page'] == 'alliance' else '')
    open(os.path.join('site', f), 'w').write(html)
    print('built', f)


main()
