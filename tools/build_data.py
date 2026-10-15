"""Normalize scraped brocap.com content (ref/*.json) into site/assets/js/data.js."""
import json, re, shutil, os, subprocess, unicodedata

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
          'november', 'december']

NAME_FIX = {
  'BANCO DI CARIBE': 'Banco di Caribe',
  'BELIZE CREDITORS COMMITTEE': 'Belize Creditors Committee',
  'COLFIRE': 'Colonial Fire & General Insurance (COLFIRE)',
  'COMMONWEALTH OF PUERTO RICO - ERS': 'Puerto Rico Employees Retirement System',
  'Commonwealth of Puerto Rico – COFINA': 'Puerto Rico Sales Tax Financing Corp. (COFINA)',
  'CREDITO REAL USA': 'Crédito Real USA Finance',
  'FIP DOLOMITAS AND NI* VENTURES': 'FIP Dolomitas and NI* Ventures',
  'GFN': 'Grupo Financiero Nacional',
  'GLOBAL PACKAGING GROUP': 'Global Packaging Group',
  'GUARDIAN GROUP': 'Guardian Group',
  'KOHLER CO.': 'Kohler Co.',
  'MASSY': 'Massy',
  'OURONOVA': 'ouronova',
  'THE COMMITTEE OF CAP CANA BONDHOLDERS': 'Cap Cana Bondholders Committee',
  'TRINIDAD PETROLEUM HOLDINGS LIMITED– PETROTRIN': 'Trinidad Petroleum Holdings (Petrotrin)',
  'UNICURITIBA': 'UniCuritiba',
  'Ansa McAl': 'ANSA McAL',
  'Province of Buenos Aires Committee': 'Province of Buenos Aires',
  'Province of Cordoba Creditors Committee': 'Province of Córdoba',
  'Ecuador Creditors Committee': 'Republic of Ecuador',
  'Indura Beach & Golf Resort (Phase I)': 'Indura Beach & Golf Resort (Phase I)',
  'Instacredit Debt Raise': 'Instacredit',
  'Latin American Agribusiness Development Corp. ("LAAD")': 'Latin American Agribusiness Development Corp.',
}

COUNTRY_FIX = {
  'Trinidad': 'Trinidad & Tobago', 'Trinidad and Tobago': 'Trinidad & Tobago', 'USA': 'United States',
  'Panamá': 'Panama', 'Curacao and Dutch Caribbean': 'Curaçao', 'Government of Belize': 'Belize',
  'Trinidad, Barbados, Jamaica': 'Trinidad, Barbados & Jamaica', 'Trinidad & Tobago and Barbados':
  'Trinidad & Tobago, Barbados',
}

REGIONS = {
  'Brazil': ['Brazil'],
  'Mexico': ['Mexico'],
  'South America': ['Argentina', 'Colombia', 'Ecuador', 'Peru', 'Bolivia'],
  'Central America': ['Costa Rica', 'El Salvador', 'Guatemala', 'Honduras', 'Panama', 'Belize'],
  'Caribbean': ['Trinidad & Tobago', 'Dominican Republic', 'Puerto Rico', 'Barbados', 'Jamaica', 'Grenada',
                'Curaçao', 'Antigua', 'St. Lucia', 'Haiti', 'Bahamas', 'St. Kitts & Nevis', 'Caribbean',
                'Trinidad, Barbados & Jamaica', 'Trinidad & Tobago, Barbados'],
  'U.S. & Europe': ['United States', 'Spain', 'Switzerland'],
}
REGION_OF = {c: r for r, cs in REGIONS.items() for c in cs}

SECTORS = [
  ('Sovereign & Public', r'sovereign|municipal|province'),
  ('Financial Services', r'financ|bank|insurance|transatlantic'),
  ('Energy & Natural Resources', r'oil|energy|mining|bioenergy|pulp'),
  ('Infrastructure & Logistics', r'logistic|transport|maritime|port|infrastructure|parking'),
  ('Technology, Media & Telecom', r'tech|software|telecom|broadband|cable|media|publishing|broadcast|printing|office'),
  ('Industrials & Chemicals', r'industr|chemical|agrochem|cement|construction|packaging|manufactur|automotive|'
                              r'environment|conglomerate'),
  ('Consumer, Health & Education', r'pharma|health|retail|beverage|beer|consumer|education|hospitality|real estate|'
                                    r'agribusiness'),
]

PRACTICES = {
  'ma': 'Mergers & Acquisitions',
  'restructuring': 'Financial Restructuring',
  'placements': 'Capital Raising',
  'valuations': 'Valuations & Fairness Opinions',
}

ACRONYMS = {'AGS', 'ERS', 'COFINA', 'TPHL', 'FMO', 'DEG', 'ANSA', 'USA', 'VIX', 'S.A.', 'II'}
SMALL = {'a', 'an', 'and', 'as', 'at', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with', 'di'}
WORD_FIX = {'Mcal': 'McAL', 'Ouronova': 'ouronova', 'Broadspan': 'BroadSpan', "Brazil'S": "Brazil's",
            "Salvador'S": "Salvador's", "Rica'S": "Rica's", "Argentina'S": "Argentina's", "France'S": "France's",
            'Tphl’S': 'TPHL’s', 'Aires’': 'Aires’', 'Belize’S': 'Belize’s', 'Brazil’S': 'Brazil’s', 'Latam': 'LatAm',
            'Province’S': 'Province’s', 'A.r.': 'A.R.', 'Court-appointed': 'Court-Appointed',
            'Colfire': 'COLFIRE', 'Tphl’s': 'TPHL’s', 'Cordoba': 'Córdoba', 'Negrao': 'Negrão', 'Quimicas': 'Químicas'}


def title_case(s):
  words = s.split()
  out = []
  for i, w in enumerate(words):
    bare = w.strip('(),.“”"')
    if bare.upper() in ACRONYMS:
      out.append(w.replace(bare, bare.upper()))
    elif i and w.lower() in SMALL:
      out.append(w.lower())
    else:
      out.append(w[:1].upper() + w[1:].lower())
  t = ' '.join(out)
  for k, v in WORD_FIX.items():
    t = t.replace(k, v)
  return t


def parse_date(s):
  if not s:
    return None, None
  s = s.lower().replace('announced', '').strip(' .')
  m = re.match(r'([a-z]+)\s+(?:\d{1,2}\s+)?(\d{4})', s)
  if not m:
    return None, None
  return int(m.group(2)), MONTHS.index(m.group(1)) + 1


def parse_value(s):
  """Returns (display, usd_millions_or_None)."""
  if not s or s.lower().startswith('undisclosed'):
    return None, None
  s = s.strip()
  cur = 'R$' if s.startswith('R$') else 'US$'
  num = s.replace('US$', '').replace('R$', '').replace('$', '').replace(',', '').strip()
  m = re.match(r'([\d.]+)\s*(billion|million|mm)?', num, re.I)
  if not m:
    return s, None
  n = float(m.group(1))
  unit = (m.group(2) or '').lower()
  millions = n * 1000 if unit == 'billion' else n if unit in ('million', 'mm') else n / 1e6
  disp = f'{cur}{millions / 1000:.1f} billion' if millions >= 1000 else f'{cur}{millions:.1f} million'
  disp = disp.replace('.0 ', ' ')
  return disp, (millions if cur == 'US$' else None)


def sector_group(s):
  if not s:
    return None
  for name, rx in SECTORS:
    if re.search(rx, s, re.I):
      return name
  return None


FLAGS = {
  'Brazil': 'br', 'Trinidad & Tobago': 'tt', 'Dominican Republic': 'do', 'United States': 'us', 'Mexico': 'mx',
  'Colombia': 'co', 'Belize': 'bz', 'Puerto Rico': 'pr', 'Barbados': 'bb', 'Costa Rica': 'cr', 'Spain': 'es',
  'Argentina': 'ar', 'El Salvador': 'sv', 'Curaçao': 'cw', 'Panama': 'pa', 'Jamaica': 'jm', 'Grenada': 'gd',
  'Guatemala': 'gt', 'Antigua': 'ag', 'St. Lucia': 'lc', 'Haiti': 'ht', 'Bahamas': 'bs', 'Honduras': 'hn', 'Peru': 'pe',
  'Ecuador': 'ec', 'Switzerland': 'ch', 'St. Kitts & Nevis': 'kn', 'Bolivia': 'bo',
  'Trinidad, Barbados & Jamaica': 'tt bb jm', 'Trinidad & Tobago, Barbados': 'tt bb',
}

# Sharper Wikimedia Commons artwork for deals whose brocap.com logo is too small; coats of arms are rasterized.
LOGO_OVERRIDE = {
  'Bancolombia': 'bancolombia', 'Republic of Ecuador': 'ecuador', 'Province of Buenos Aires': 'buenos-aires',
  'Province of Córdoba': 'cordoba', 'Puerto Rico Employees Retirement System': 'puerto-rico',
  'Puerto Rico Sales Tax Financing Corp. (COFINA)': 'puerto-rico', 'Zurich Insurance Group': 'zurich',
  'EOG Resources': 'eog', 'Kohler Co.': 'kohler', 'Sandals Resort': 'sandals', 'Belize Creditors Committee': 'belize',
  'Banco Sabadell': 'sabadell', 'Nortel Networks': 'nortel', 'SNC Lavalin': 'snc-lavalin',
  "The Grenada Creditor's Committee": 'grenada', 'Grenada Creditors Committee': 'grenada',
}
RASTERIZE = {'ecuador', 'buenos-aires', 'cordoba', 'puerto-rico', 'belize', 'grenada'}

# brocap.com "logos" that are only typed names; rendered as text instead.
TEXT_LOGOS = {'Pica de Hule Natural, S.A.', 'Caribbean Project Acquisition, LLC', 'Ático Florestal FIP',
              'Benoit, Wallerius, FASA', 'HNB Acquisition Corp.'}

FEATURED = [
  ('Republic of Ecuador', 'Advising the Ecuador Steering Committee', 'on the restructuring of Ecuador’s sovereign debt',
   'Co-Financial Advisor'),
  ('Bancolombia', 'Advising Bancolombia', 'on the settlement of the obligations of ATN3, a subsidiary of Abengoa Perú',
   'Exclusive Financial Advisor'),
  ('Province of Buenos Aires', 'Advising the Bondholder Steering Committee',
   'on the restructuring of the Province of Buenos Aires’ external debt', 'Financial Advisor'),
  ('EOG Resources', 'Advising EOG Resources', 'on the sale of its equity interests in two Caribbean ammonia plants',
   'Financial Advisor'),
  ('Puerto Rico Employees Retirement System', 'Advising the UBS Puerto Rico Family of Funds',
   'on the restructuring of the Employees Retirement System’s debt', 'Exclusive Financial Advisor'),
  ('Banco Sabadell', 'Advising Banco Sabadell', 'on its acquisition of Mellon United National Bank from BNY Mellon',
   'Exclusive Financial Advisor'),
  ('Sandals Resort', 'Advising Sandals Resorts', 'on the sale of Grand Pineapple Beach Antigua to Elite Island Resorts',
   'Exclusive Financial Advisor'),
]


def trim_logo(src, dst):
  """Crops near-white margins so logos of different source sizes render at a consistent visual weight."""
  from PIL import Image, ImageChops
  im = Image.open(src).convert('RGBA')
  flat = Image.new('RGBA', im.size, (255, 255, 255, 255))
  flat.alpha_composite(im)
  diff = ImageChops.difference(flat.convert('RGB'), Image.new('RGB', im.size, (255, 255, 255)))
  bbox = diff.point(lambda p: 255 if p > 24 else 0).getbbox()
  if bbox:
    flat = flat.crop(bbox)
  flat.convert('RGB').save(dst, quality=92)


def logo_for(d, used):
  name = NAME_FIX.get(d['name'], d['name'].strip())
  if name in TEXT_LOGOS or d['name'] in TEXT_LOGOS:
    return None
  if name in LOGO_OVERRIDE:
    key = LOGO_OVERRIDE[name]
    src = f'ref/svg-logos/{key}.svg'
    if key in RASTERIZE:
      dst = f'assets/img/logos/{key}.png'
      if dst not in used:
        subprocess.run(['rsvg-convert', '-h', '240', '-o', 'site/' + dst, src], check=True)
    else:
      dst = f'assets/img/logos/{key}.svg'
      shutil.copy(src, 'site/' + dst)
    used.add(dst)
    return dst
  src = 'ref/logos/' + d['logo'].lstrip('/').replace('/', '__')
  if not os.path.exists(src):
    return None
  try:
    dst = 'assets/img/logos/' + re.sub(r'[^a-z0-9]+', '-', os.path.splitext(os.path.basename(src))[0].lower()) + '.jpg'
    if dst not in used:
      trim_logo(src, 'site/' + dst)
    used.add(dst)
    return dst
  except OSError:
    return None


def deals():
  out = []
  used = set()
  os.makedirs('site/assets/img/logos', exist_ok=True)
  for d in json.load(open('ref/deals.json')):
    country = COUNTRY_FIX.get(d.get('country'), d.get('country'))
    if country is None and 'Transmissora' in d['name']:
      country = 'Brazil'
    country = {'Ansa McAl': 'Trinidad & Tobago', 'Caribbean Communications Network Ltd.': 'Trinidad & Tobago'}.get(d['name'].strip(), country)
    if country == 'Regional':
      country = 'Latin America'
    year, month = parse_date(d.get('completion'))
    value, usd = parse_value(d.get('value'))
    name = NAME_FIX.get(d['name'], d['name'].strip())
    desc = (d.get('description') or '').strip()
    desc = re.sub(r'\s+', ' ', desc).replace('Broadspan', 'BroadSpan').replace('Credtors', 'Creditors').replace('outsanding', 'outstanding')
    out.append({
      'name': name,
      'client': (d.get('client') or '').strip(),
      'practice': d['practice'],
      'country': country,
      'region': REGION_OF.get(country, 'Latin America'),
      'sector': sector_group(d.get('sector')) or 'Other',
      'year': year, 'month': month,
      'value': value, 'usd': usd,
      'desc': desc,
      'logo': logo_for(d, used),
      'flags': FLAGS.get(country, '').split(),
    })
  out.sort(key=lambda d: (-(d['year'] or 0), -(d['month'] or 0)))
  return out


def news():
  out = []
  for n in json.load(open('ref/news.json')):
    year, month = parse_date(n['date'])
    out.append({'title': title_case(n['title']), 'summary': n['summary'], 'pdf': n['pdf'], 'year': year,
                'month': month, 'kind': n['kind']})
  out.sort(key=lambda n: (-n['year'], -n['month']))
  return out


RANK = ['Chairman', 'Senior Managing Director', 'Managing Director', 'Board Member', 'Director', 'Vice President',
        'Associate', 'Analyst', 'Senior Advisor']
EXEC_COMMITTEE = {'Michael L. Gerrard', 'Leonardo Antunes', 'Noah Kessler'}
BOARD = EXEC_COMMITTEE | {'Gonzalo Valdes-Fauli', 'Timothy Davis'}


def team():
  out = []
  os.makedirs('site/assets/img/team', exist_ok=True)
  for p in json.load(open('ref/team.json')):
    img = None
    if p['img']:
      src = 'ref/img/staff/' + os.path.basename(p['img'])
      ascii_name = unicodedata.normalize('NFKD', p['name']).encode('ascii', 'ignore').decode()
      slug = re.sub(r'[^a-z]+', '-', ascii_name.lower()).strip('-')
      img = f'assets/img/team/{slug}{os.path.splitext(src)[1]}'
      shutil.copy(src, 'site/' + img)
    name = p['name'].replace('Vinicius Días', 'Vinicius Dias')
    group = 'advisors' if 'senior-advisors' in p['groups'] else 'board' if name in BOARD else 'team'
    out.append({
      'name': name, 'title': p['title'], 'img': img, 'languages': p['languages'],
      'bio': [b.replace('Broadspan', 'BroadSpan') for b in p['bio']], 'group': group, 'exec': p['name'] in EXEC_COMMITTEE,
    })
  out.sort(key=lambda p: (['board', 'team', 'advisors'].index(p['group']), RANK.index(p['title']), p['name'].split()[-1]))
  return out


def research():
  return [
    ('Country Reports', [('Brazil Macro & Political Report', 'Dec 2017', 'Country-Reports/BSC_-_Brazil_Macro_and_Political_Report_-_Dec17.pdf'),
                         ('Brazil', '2013', 'Country-Reports/Brazil.pdf'), ('Spain', '2013', 'Country-Reports/Spain.pdf')]),
    ('Energy', [('Brazil Oil & Gas', None, 'Energy/Brazil-Oil-and-Gas.pdf'), ('Renewable Energy', None, 'Energy/Renewable-Energy.pdf')]),
    ('Industrials', [('Aerospace & Defence', '2019', 'Industrial-and-Engineering/2019-Aerospace-and-Defence-M&A-forecasted-trends-(2020-2030).pdf'),
                     ('Plastic Packaging', '2020', 'Industrial-and-Engineering/Spring2020-PackagingM&AReport.pdf'),
                     ('Automotive Interiors', None, 'Industrial-and-Engineering/Automotive-Interiors.pdf'),
                     ('Mining', None, 'Industrial-and-Engineering/Mining.pdf')]),
    ('Technology, Media & Telecom', [('Business Process Outsourcing', None, 'Techology-Media-and-Telecoms/Business-Process-Outsourcing.pdf'),
                                     ('Sensors', None, 'Techology-Media-and-Telecoms/Sensors.pdf'),
                                     ('Web Hosting', None, 'Techology-Media-and-Telecoms/Web-Hosting.pdf')]),
    ('Consumer & Services', [('Global Education Market', '2020', 'Education/2020-Global-Educaton-Market-Report.pdf'),
                             ('Bakery & Pastry', None, 'Consumer-Products/Bakery-and-Pastry.pdf'),
                             ('Food Ingredients', None, 'Consumer-Products/Food-Ingredients.pdf'),
                             ('Sportswear', None, 'Consumer-Products/Sportswear.pdf'),
                             ('Global Facilities Management', None, 'Business-Services/Global-Facilities-Management.pdf')]),
    ('Financial Services', [('Financial Technology', None, 'Financial-Services/Financial-Technology.pdf')]),
  ]


def main():
  shutil.rmtree('site/assets/img/logos', ignore_errors=True)
  d, n, t = deals(), news(), team()
  os.makedirs('site/assets/img/flags', exist_ok=True)
  for code in {c for x in d for c in x['flags']}:
    shutil.copy(f'ref/flags/{code}.svg', f'site/assets/img/flags/{code}.svg')
  featured = []
  for name, line1, line2, role in FEATURED:
    deal = next(x for x in d if x['name'] == name)
    featured.append({'name': name, 'line1': line1, 'line2': line2, 'role': role, 'logo': deal['logo'],
                     'value': deal['value'], 'year': deal['year'], 'country': deal['country'], 'flags': deal['flags']})
  r = [{'sector': s, 'items': [{'title': a, 'date': b, 'pdf': 'https://brocap.com/pdf/' + c} for a, b, c in items]}
       for s, items in research()]
  stats = {'deals': len(d)}
  js = ('window.BSC = ' + json.dumps({'practices': PRACTICES, 'regions': list(REGIONS) + ['Latin America'],
                                      'sectors': [s for s, _ in SECTORS] + ['Other'], 'deals': d, 'featured': featured, 'news': n,
                                      'team': t, 'research': r, 'stats': stats}, ensure_ascii=False) + ';\n')
  open('site/assets/js/data.js', 'w').write(js)
  print(stats, {k: sum(1 for x in d if x['practice'] == k) for k in PRACTICES})


main()
