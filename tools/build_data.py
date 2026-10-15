"""Normalize scraped brocap.com content (ref/*.json) into site/assets/js/data.js."""
import json, re, shutil, os, unicodedata

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


def deals():
  out = []
  for d in json.load(open('ref/deals.json')):
    country = COUNTRY_FIX.get(d.get('country'), d.get('country'))
    if country is None and 'Transmissora' in d['name']:
      country = 'Brazil'
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
  out.sort(key=lambda p: (RANK.index(p['title']), p['name'].split()[-1]))
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
  d, n, t = deals(), news(), team()
  r = [{'sector': s, 'items': [{'title': a, 'date': b, 'pdf': 'https://brocap.com/pdf/' + c} for a, b, c in items]}
       for s, items in research()]
  restructured = sum(x['usd'] or 0 for x in d if x['practice'] == 'restructuring')
  stats = {'deals': len(d), 'restructuredUsdBn': round(restructured / 1000, 1),
           'countries': len({x['country'] for x in d if x['country']})}
  js = ('window.BSC = ' + json.dumps({'practices': PRACTICES, 'regions': list(REGIONS) + ['Latin America'],
                                      'sectors': [s for s, _ in SECTORS] + ['Other'], 'deals': d, 'news': n,
                                      'team': t, 'research': r, 'stats': stats}, ensure_ascii=False) + ';\n')
  open('site/assets/js/data.js', 'w').write(js)
  print(stats, {k: sum(1 for x in d if x['practice'] == k) for k in PRACTICES})


main()
