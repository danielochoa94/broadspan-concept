"""Wraps src/pages/*.html bodies in the shared layout, renders src/data/ into them and writes site/ with its sitemap,
robots.txt and llms.txt files.

PRODUCTION=1 builds for brocap.com and lets crawlers index it; the default preview build is hidden from them.
"""
import datetime, hashlib, json, os, re, subprocess, unicodedata
from html import escape, unescape

PRODUCTION = os.environ.get('PRODUCTION') == '1'
BASE_URL = 'https://brocap.com/' if PRODUCTION else 'https://danielochoa94.github.io/broadspan-concept/'

NAV = [('firm.html', 'Who We Are'), ('what-we-do.html', 'What We Do'), ('transactions.html', 'Experience'),
       ('alliance.html', 'Mergers Alliance'), ('news.html', 'News'), ('contact.html', 'Contact')]

# BroadSpan Asset Management: its own section with a sub-nav, linked from the footer rather than the header
BSAM_NAV = [('asset-management.html', 'Overview'), ('asset-management-who-we-are.html', 'Who We Are'),
            ('asset-management-team.html', 'Investment Team'), ('asset-management-contact.html', 'Contact'),
            ('asset-management-client-login.html', 'Client Login')]
BSAM_HOME = ('asset-management.html', 'Asset Management')

# city, country code, country, street address, postal code
OFFICES = [
  ('Miami', 'US', 'United States', '1441 Brickell Ave, Suite 1550', 'FL 33131'),
  ('Mexico City', 'MX', 'Mexico', 'Pedregal 24, Piso 3, Col. Lomas Virreyes', '11040'),
  ('Medellín', 'CO', 'Colombia', 'Carrera 43a #1-50, Torre Protección, 6th Floor, Office 652', None),
  ('Caracas', 'VE', 'Venezuela', None, None),
  ('Rio de Janeiro', 'BR', 'Brazil', 'Avenida das Américas 3434, Bloco 4, Sala 406', None),
  ('São Paulo', 'BR', 'Brazil', None, None),
]

SUMMARY = ('BroadSpan Capital is an independent investment bank specializing in Latin America and the Caribbean. Founded '
           'in 2001 and headquartered in Miami, it advises corporations, partnerships and governments on cross-border '
           'mergers and acquisitions, financial restructurings, capital raising, and valuations and fairness opinions.')

PAGE_TYPES = {'home': 'WebPage', 'firm': 'AboutPage', 'contact': 'ContactPage', 'transactions': 'CollectionPage',
              'news': 'CollectionPage'}

LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:site_name" content="BroadSpan Capital">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}assets/img/og.png?v=2">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@300&family=IBM+Plex+Sans:wght@300;400;500&family=Inter:wght@700&display=swap">
<link rel="stylesheet" href="assets/css/site.css?v={css_v}">
<script type="application/ld+json">{jsonld}</script>
</head>
<body data-page="{page}">
{concept}<header class="site-header">
  <div class="inner">
    <a class="logo" href="index.html"><img src="assets/img/logo.png" alt="BroadSpan Capital" width="325" height="86"></a>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
    <nav class="nav" id="nav">
{nav}
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
    </div>
    <div class="footer-col">
      <h4>Offices</h4>
      {offices}
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
<script src="assets/js/site.js?v={js_v}"></script>
</body>
</html>"""

CONCEPT = ('<div class="concept">Design concept<span class="long"> for BroadSpan Capital</span> &middot; Preview only, '
           'not the live site</div>\n')

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']
SHORT = {'ma': 'M&A', 'restructuring': 'Restructuring', 'placements': 'Capital Raising', 'valuations': 'Valuation'}
TEAM_GROUPS = [('all', 'All'), ('board', 'Board of Managers'), ('team', 'Investment Banking & Restructuring'),
               ('advisors', 'Senior Advisors')]
DEALS_PER_PAGE = 24

D = json.load(open('src/data/site.json'))
A = json.load(open('src/data/alliance.json'))
DEALS = {d['id']: d for d in D['deals']}


def esc(s):
  return escape(str(s or ''))


def slug(s):
  return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip('-')


# Prefixed so BSAM bios (written for asset management) don't collide with the same person's BroadSpan bio
BSAM_TEAM = [{**p, 'key': 'bsam-' + slug(p['name'])} for p in D['bsam_team']]


def month_year(o, short=False):
  if not o.get('year'):
    return ''
  return (MONTHS[o['month'] - 1][:3 if short else None] + ' ' if o.get('month') else '') + str(o['year'])


def news_href(n):
  return f'href="{n["page"]}"' if n.get('page') else f'href="{n["pdf"]}" target="_blank" rel="noopener"'


def flag_imgs(codes):
  return ''.join(f'<img class="flag" src="assets/img/flags/{c}.svg" alt="" width="22" height="17">' for c in codes)


def flagged(codes, country):
  return f'<span class="flagged">{flag_imgs(codes)}<span>{esc(country)}</span></span>'


def initials(name):
  return ''.join(w[0] for w in name.split() if re.match(r'[A-ZÁÉÍÓÚ]', w))[:2]


def avatar(p, lazy=False):
  inner = (f'<img src="{p["img"]}" alt=""{" loading=\"lazy\"" if lazy else ""} width="190" height="190">' if p.get('img')
           else f'<span class="initials">{initials(p["name"])}</span>')
  return f'<span class="avatar">{inner}</span>'


def logo_block(d):
  return (f'<img src="{d["logo"]}" alt="{esc(d["name"])}" loading="lazy">' if d.get('logo')
          else f'<span class="wordlogo">{esc(d["name"])}</span>')


def deal_desc(d):
  if d.get('desc'):
    return d['desc']
  if d['practice'] == 'valuations':
    return f'Valuation and fairness opinion advisory{" for " + d["client"] if d.get("client") and d["client"] != d["name"] else ""}.'
  return ''


def deal_card(d):
  return f"""
      <button class="ts" type="button" data-deal="{d['id']}" data-practice="{d['practice']}" data-region="{esc(d['region'])}" data-sector="{esc(d['sector'])}">
        <div class="ts-logo">{logo_block(d)}</div>
        <div class="ts-body">
          <div class="ts-top">{flagged(d['flags'], d['country'])}<time>{month_year(d, True)}</time></div>
          <h3 class="ts-name">{esc(d['name'])}</h3>
          <div class="ts-practice">{esc(SHORT[d['practice']])}</div>
          <div class="ts-value{'' if d['value'] else ' undisclosed'}">{esc(d['value']) if d['value'] else 'Undisclosed'}</div>
        </div>
      </button>"""


def deal_detail(d):
  country = flagged(d['flags'], d['country']) if d['flags'] else esc(d['country'] or '—')
  client = f'<p class="modal-meta">Client: {esc(d["client"])}</p>' if d.get('client') and d['client'] != d['name'] else ''
  more = f'<a class="more" href="{d["page"]}">View full transaction <span class="chev"></span></a>' if d.get('page') else ''
  return f"""
      <div class="deal-modal">
        <div class="deal-modal-logo">{logo_block(d)}</div>
        <h2>{esc(d['name'])}</h2>
        <dl class="facts">
          <div><dt>Practice</dt><dd>{esc(D['practices'][d['practice']])}</dd></div>
          <div><dt>Country</dt><dd>{country}</dd></div>
          <div><dt>Completed</dt><dd>{month_year(d) or '—'}</dd></div>
          <div><dt>Value</dt><dd>{esc(d['value'] or 'Undisclosed')}</dd></div>
        </dl>
        <div class="copy"><p>{esc(deal_desc(d))}</p></div>
        {client}
        {more}
      </div>"""


def person_card(p, cls):
  extra = ''
  if cls == 'person':
    extra = (('\n          <span class="ec">Executive Committee</span>' if p['exec'] else '') +
             '\n          <span class="more">View Bio <span class="chev"></span></span>')
  group = f' data-group="{p["group"]}"' if cls == 'person' else ''
  return f"""
        <button class="{cls}" type="button" data-person="{p.get('key') or slug(p['name'])}"{group}>{avatar(p)}<span class="n">{esc(p['name'])}</span><span class="t">{esc(p['title'])}</span>{extra}
        </button>"""


def person_bio(p):
  langs = f'<p class="modal-meta">Languages: {esc(p["languages"])}</p>' if p.get('languages') else ''
  bio = ''.join(f'<p>{esc(b)}</p>' for b in p['bio'])
  return f"""
      <div class="bio-head">{avatar(p, lazy=True)}<div><h2>{esc(p['name'])}</h2><p>{esc(p['title'])}{' · Executive Committee' if p['exec'] else ''}</p></div></div>
      <div class="copy">{bio}</div>
      {langs}"""


def latest_news():
  return ''.join(f"""
      <a class="news-item" {news_href(n)}><h3>{esc(n['title'])}</h3><time>{month_year(n)}</time></a>""" for n in D['news'][:3])


def slides():
  out = []
  for i, f in enumerate(D['featured']):
    line1 = f'<a href="{f["page"]}">{esc(f["line1"])} <span class="chev"></span></a>' if f.get('page') else esc(f['line1'])
    out.append(f"""
      <div class="slide{'' if i else ' active'}" role="tabpanel" aria-hidden="{'true' if i else 'false'}">
        <div class="logo"><img src="{f['logo']}" alt="{esc(f['name'])}"></div>
        <p class="line1">{line1}</p>
        <p class="line2">{esc(f['line2'])}</p>
        <p class="role"><span>{esc(f['role'])}</span><span class="sep"></span><span>{esc(f['value'] or f['year'])}</span></p>
        <p class="where">{flagged(f['flags'], f['country'])}</p>
      </div>""")
  return ''.join(out)


def dots():
  return ''.join(f'<button type="button" role="tab" aria-label="{esc(f["name"])}" aria-current="{"false" if i else "true"}"></button>'
                 for i, f in enumerate(D['featured']))


def leadership():
  people = [p for p in D['team'] if p['group'] == 'board'] + [next(p for p in D['team'] if p['name'] == 'Luis Camarena')]
  return ''.join(person_card(p, 'mini') for p in people)


def team_tabs():
  count = lambda k: len(D['team']) if k == 'all' else sum(p['group'] == k for p in D['team'])
  return ''.join(f'<button type="button" data-group="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(label)}<span>{count(k)}</span></button>'
                 for k, label in TEAM_GROUPS)


def news_list():
  out = []
  for y in dict.fromkeys(n['year'] for n in D['news']):
    out.append(f'<h2 class="year">{y}</h2>' + ''.join(f"""
      <a class="news-row" {news_href(n)}>
        <time>{month_year(n, True)}</time><h3>{esc(n['title'])}</h3><span class="chev"></span><p>{esc(n['summary'])}</p>
      </a>""" for n in D['news'] if n['year'] == y))
  return ''.join(out)


def research():
  return ''.join(f"""
      <div class="research-card"><h3>{esc(r['sector'])}</h3>
        {''.join(f'<a href="{i["pdf"]}" target="_blank" rel="noopener">{esc(i["title"])}<span>{i.get("date") or "PDF"}</span></a>' for i in r['items'])}
      </div>""" for r in D['research'])


def pins():
  # Partner pins first so BroadSpan's sit on top where offices overlap (Miami and Fort Lauderdale)
  return ''.join(f"""
      <button class="pin{' own' if f['slug'] == 'broadspan' else ''}" type="button" data-firm="{f['slug']}" style="left:{o['x']}%;top:{o['y']}%" aria-label="{esc(f['name'])}, {esc(o['city'])}">
        <span class="tip"><b>{esc(o['city'])}</b>{esc(f['name'])}</span>
      </button>""" for f in A['firms'][1:] + A['firms'][:1] for o in f['offices'])


def members():
  out = []
  for f in A['firms']:
    body = f"""
        <span class="member-logo"><img src="{f['logo']}" alt="{esc(f['name'])}" loading="lazy"></span>
        <span class="member-name">{esc(f['name'])}</span>
        <span class="member-flags">{flag_imgs(dict.fromkeys(o['flag'] for o in f['offices']))}</span>
        <span class="member-cities">{' · '.join(esc(o['city']) for o in f['offices'])}</span>
        <span class="member-est">Est. {f['est']}</span>"""
    cls = f'member{" own" if f["slug"] == "broadspan" else ""}'
    out.append(f'<a class="{cls}" data-firm="{f["slug"]}" href="{f["url"]}" target="_blank" rel="noopener">{body}</a>' if f['url']
               else f'<div class="{cls}" data-firm="{f["slug"]}">{body}</div>')
  return ''.join(out)


def practice_tabs():
  tabs = [('all', 'All', len(D['deals']))] + [(k, v, sum(d['practice'] == k for d in D['deals'])) for k, v in D['practices'].items()]
  return ''.join(f'<button type="button" data-practice="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(label)}<span>{n}</span></button>'
                 for k, label, n in tabs)


def options(label, values, key):
  return f'<option value="">{label}</option>' + ''.join(f'<option>{esc(v)}</option>' for v in values if any(d[key] == v for d in D['deals']))


def bsam_nav(f):
  links = ''.join(f'\n  <a href="{h}"{" aria-current=\"page\"" if h == f else ""}>{t}</a>' for h, t in BSAM_NAV)
  return f'<nav class="practice-nav bsam-nav" aria-label="BroadSpan Asset Management">\n  <span class="bsam-mark">BSAM</span>{links}\n</nav>'


BSAM_DISCLOSURE = ('BroadSpan Asset Management LLC is an investment adviser registered with the Florida Office of Financial Regulation. '
  'Such registration does not imply that the Firm is recommended or approved by the United States government or any regulatory agency. '
  'BroadSpan Asset Management L.L.C may only transact business or render personalized investment advice in those states and '
  'international jurisdictions where it is registered, has notice filed, or is otherwise excluded or exempted from registration '
  'requirements. The purpose of this website is for information distribution only and should not be construed as an offer to buy or '
  'sell securities or to offer investment advice. Past results are no guarantee of future results and no representation is made that '
  'a client will or is likely to achieve results that are similar to those described. An investor should consider his or her '
  'investment objectives, risks, charges and expenses carefully before investing. Please refer to BroadSpan Asset Management '
  'L.L.C’s ADV Part 2 for additional information and risks.')


RENDER = {
  'latest-news': latest_news, 'slides': slides, 'dots': dots, 'leadership': leadership, 'team-tabs': team_tabs,
  'team-grid': lambda: ''.join(person_card(p, 'person') for p in D['team']), 'news': news_list, 'research': research,
  'pins': pins, 'members': members, 'practice-filter': practice_tabs,
  'region-filter': lambda: options('All regions', D['regions'], 'region'),
  'sector-filter': lambda: options('All sectors', D['sectors'], 'sector'),
  'deals': lambda: ''.join(deal_card(d) for d in D['deals']),
  'result-count': lambda: f'{len(D["deals"])} transactions',
  'bsam-team': lambda: ''.join(person_card(p, 'person') for p in BSAM_TEAM),
  'bsam-mosaic': lambda: ''.join(person_card(p, 'mini') for p in BSAM_TEAM),
  'bsam-disclosure': lambda: f'<h2 class="label">Important Disclosures</h2><p>{esc(BSAM_DISCLOSURE)}</p>',
}

COUNTS = {
  'stat': lambda k: D['stats'][k],
  'count': lambda k: f'{sum(d["practice"] == k for d in D["deals"])} transactions',
  'tally': lambda k: sum(d['practice'] == k for d in D['deals']),
  'count-sovereign': lambda _: sum(d['practice'] == 'restructuring' and d['sector'] == 'Sovereign & Public' for d in D['deals']),
  'alliance': lambda k: A['stats'][k],
}


def render(body):
  """Fills the page's data placeholders; returns the body and whether it used src/data/."""
  used = False

  def by_id(m):
    nonlocal used
    tag, attrs, el_id = m.groups()
    if el_id not in RENDER:
      return m.group(0)
    used = True
    return f'<{tag}{attrs}>{RENDER[el_id]()}</{tag}>'

  def by_deals(m):
    nonlocal used
    used = True
    return f'<{m[1]}{m[2]}>{"".join(deal_card(DEALS[i]) for i in m[3].split())}</{m[1]}>'

  def by_count(m):
    nonlocal used
    used = True
    return f'{m[1]}{COUNTS[m[3]](m[4])}{m[5]}'

  body = re.sub(r'<(\w+)([^>]*?\bid="([\w-]+)"[^>]*)></\1>', by_id, body)
  body = re.sub(r'<(\w+)([^>]*?\bdata-deals="([^"]+)"[^>]*)></\1>', by_deals, body)
  body = re.sub(r'(<(\w+)[^>]*?\bdata-(stat|count-sovereign|count|tally|alliance)(?:="([^"]*)")?[^>]*>)[^<]*(</\2>)', by_count, body)

  # Modal content ships in the page so crawlers and agents can read it without running JavaScript
  details = [f'<article id="deal-{i}">{deal_detail(DEALS[i])}\n    </article>'
             for i in dict.fromkeys(re.findall(r'data-deal="([^"]+)"', body))]
  team = {slug(p['name']): p for p in D['team']} | {p['key']: p for p in BSAM_TEAM}
  details += [f'<article id="bio-{s}">{person_bio(team[s])}\n    </article>'
              for s in dict.fromkeys(re.findall(r'data-person="([^"]+)"', body))]
  if details:
    body += '\n<div class="details" hidden>\n  ' + '\n  '.join(details) + '\n</div>'
  return body, used


def version(path):
  # Content hash in asset URLs so returning visitors never pair new pages with a cached old script or stylesheet
  return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:8]


def page_url(f):
  return BASE_URL + ('' if f == 'index.html' else f)


def organization():
  def place(city, code, country, street, postal):
    address = {'@type': 'PostalAddress', 'addressLocality': city, 'addressCountry': code}
    if street:
      address['streetAddress'] = street
    if postal:
      address['postalCode'] = postal
    return {'@type': 'Place', 'name': f'BroadSpan Capital {city}', 'address': address}

  return {
    '@type': 'Organization', '@id': BASE_URL + '#organization', 'name': 'BroadSpan Capital', 'alternateName': 'BroadSpan',
    'url': BASE_URL, 'logo': BASE_URL + 'assets/img/logo.png', 'image': BASE_URL + 'assets/img/og.png?v=2',
    'description': SUMMARY, 'email': 'info@brocap.com', 'foundingDate': '2001',
    'address': {'@type': 'PostalAddress', 'streetAddress': '1441 Brickell Ave, Suite 1550', 'addressLocality': 'Miami',
                'addressRegion': 'FL', 'postalCode': '33131', 'addressCountry': 'US'},
    'location': [place(*o) for o in OFFICES],
    'areaServed': ['Latin America', 'Caribbean'],
    'knowsAbout': list(D['practices'].values()) + ['Sovereign debt restructuring', 'Cross-border transactions'],
    'memberOf': {'@type': 'Organization', 'name': 'Mergers Alliance', 'url': 'https://www.mergers-alliance.com/'},
    'subOrganization': [
      {'@type': 'Organization', 'name': 'BroadSpan Securities LLC', 'description': 'Member of FINRA and SIPC.'},
      {'@type': 'Organization', 'name': 'BroadSpan Asset Management LLC', 'url': 'https://brocap.com/bsam/'}],
  }


def jsonld(f, m):
  url = page_url(f)
  org = {'@id': BASE_URL + '#organization'}
  graph = [organization(), {'@type': 'WebSite', '@id': BASE_URL + '#website', 'url': BASE_URL, 'name': 'BroadSpan Capital',
                            'publisher': org}]
  webpage = {'@type': PAGE_TYPES.get(m['page'], 'WebPage'), '@id': url + '#webpage', 'url': url, 'name': m['title'],
             'description': m['description'], 'isPartOf': {'@id': BASE_URL + '#website'}, 'about': org, 'inLanguage': 'en'}
  if f != 'index.html':
    crumbs = [('Home', BASE_URL)]
    if m['page'] == 'deal':
      crumbs += [('Experience', page_url('transactions.html')), (m.get('og_title', m['title']), url)]
    elif f.startswith('asset-management'):
      crumbs += [(BSAM_HOME[1], page_url(BSAM_HOME[0]))] + ([(dict(BSAM_NAV)[f], url)] if f != BSAM_HOME[0] else [])
    else:
      crumbs += [(dict(NAV)[f], url)]
    webpage['breadcrumb'] = {'@type': 'BreadcrumbList', 'itemListElement': [
      {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]}
  graph.append(webpage)
  if m['page'] == 'firm':
    graph += [{'@type': 'Person', 'name': p['name'], 'jobTitle': p['title'], 'worksFor': org, 'description': p['bio'][0],
               **({'image': BASE_URL + p['img']} if p.get('img') else {})} for p in D['team']]
  # Escape "<" so no string can close the script element early
  return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('<', '\\u003c')


def git_date(*paths):
  out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', *paths], capture_output=True, text=True).stdout.strip()
  return out or datetime.date.today().isoformat()


def sitemap(pages):
  urls = ''.join(f'  <url><loc>{escape(page_url(f))}</loc><lastmod>{lastmod}</lastmod></url>\n' for f, _, lastmod in pages)
  return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def robots():
  if not PRODUCTION:
    return 'User-agent: *\nDisallow: /\n'
  # Search, answer-engine and AI training crawlers are all welcome
  return f'User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n'


def llms(pages):
  meta = {f: m for f, m, _ in pages}
  practices = '\n'.join(f'- {v}: {sum(d["practice"] == k for d in D["deals"])} transactions' for k, v in D['practices'].items())
  offices = ', '.join(o[0] for o in OFFICES)
  links = '\n'.join(f'- [{label}]({page_url(f)}): {meta[f]["description"]}' for f, label in NAV + [BSAM_HOME] + BSAM_NAV[1:])
  deals = '\n'.join(f'- [{meta[f].get("og_title", meta[f]["title"])}]({page_url(f)}): {meta[f]["description"]}'
                    for f in meta if meta[f]['page'] == 'deal')
  return f"""# BroadSpan Capital

> {SUMMARY}

BroadSpan has advised on {len(D['deals'])} transactions across four practices:

{practices}

Offices: {offices}. Contact: info@brocap.com, 1441 Brickell Ave, Suite 1550, Miami, FL 33131.

BroadSpan is a member of Mergers Alliance, a partnership of {A['stats']['firms']} independent corporate finance firms in {A['stats']['countries']} countries.
BroadSpan Securities LLC is a member of FINRA and SIPC. Asset management activities are conducted through BroadSpan Asset Management LLC.

## Pages

- [Home]({BASE_URL}): {meta['index.html']['description']}
{links}

## Transactions

{deals}

## Optional

- [Full transaction record, team biographies and news]({BASE_URL}llms-full.txt)
"""


def llms_full():
  def deal(d):
    facts = [D['practices'][d['practice']], d['country'], month_year(d), d['value'] or 'Undisclosed value']
    client = f' Client: {d["client"]}.' if d.get('client') and d['client'] != d['name'] else ''
    link = f' Details: {page_url(d["page"])}' if d.get('page') else ''
    return f'- **{d["name"]}** ({", ".join(x for x in facts if x)}). {deal_desc(d)}{client}{link}'

  def person(p):
    langs = f'\n\nLanguages: {p["languages"]}' if p.get('languages') else ''
    return f'### {p["name"]}\n\n{p["title"]}{", Executive Committee" if p["exec"] else ""}\n\n' + '\n\n'.join(p['bio']) + langs

  def news(n):
    link = page_url(n['page']) if n.get('page') else n['pdf']
    return f'- **{n["title"]}** ({month_year(n)}): {n["summary"]} {link}'

  def office(city, _, country, street, postal):
    return f'- {city}, {country}' + (f': {street}' + (f', {postal}' if postal else '') if street else '')

  groups = '\n\n'.join(f'### {label}\n\n' + '\n'.join(deal(d) for d in D['deals'] if d['practice'] == k)
                       for k, label in D['practices'].items())
  members = '\n'.join(f'- {f["name"]}: {", ".join(o["city"] for o in f["offices"])}' for f in A['firms'])
  return f"""# BroadSpan Capital

> {SUMMARY}

## Offices

{chr(10).join(office(*o) for o in OFFICES)}

Contact: info@brocap.com

## Transactions

{groups}

## Team

{chr(10).join(person(p) for p in D['team'])}

## BroadSpan Asset Management investment team

{chr(10).join(person(p) for p in BSAM_TEAM)}

## News

{chr(10).join(news(n) for n in D['news'])}

## Mergers Alliance members

{members}
"""


def main():
  src = 'src/pages'
  nav_for = lambda f: '\n'.join(f'      <a href="{h}"{" aria-current=\"page\"" if h == f else ""}>{t}</a>' for h, t in NAV)
  footer_nav = '\n'.join(f'      <a href="{h}">{t}</a>' for h, t in [('index.html', 'Home')] + NAV + [BSAM_HOME])
  pages = []
  for f in sorted(os.listdir(src)):
    raw = open(os.path.join(src, f)).read()
    meta, body = raw.split('\n---\n', 1)
    m = {k: unescape(v) for k, v in re.findall(r'^(\w+):\s*(.*)$', meta, re.M)}
    body, used_data = render(body.strip('\n').replace('<nav id="bsam-nav"></nav>', bsam_nav(f)))
    html = LAYOUT.format(
      title=esc(m['title']), og_title=esc(m.get('og_title', m['title'])), description=esc(m['description']),
      page=m['page'], url=page_url(f), base=BASE_URL, nav=nav_for(f), footer_nav=footer_nav, body=body,
      robots='index, follow, max-image-preview:large' if PRODUCTION else 'noindex, nofollow',
      concept='' if PRODUCTION else CONCEPT, css_v=version('site/assets/css/site.css'), js_v=version('site/assets/js/site.js'), offices=''.join(f'<p>{o[0]}</p>' for o in OFFICES), jsonld=jsonld(f, m))
    open(os.path.join('site', f), 'w').write(html)
    pages.append((f, m, git_date(os.path.join(src, f), *(['src/data'] if used_data else []))))
    print('built', f)
  open('site/sitemap.xml', 'w').write(sitemap(pages))
  open('site/robots.txt', 'w').write(robots())
  open('site/llms.txt', 'w').write(llms(pages))
  open('site/llms-full.txt', 'w').write(llms_full())
  print('built sitemap.xml, robots.txt, llms.txt, llms-full.txt', '(production)' if PRODUCTION else '(preview)')


main()
