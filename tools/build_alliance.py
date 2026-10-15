"""Builds the Mergers Alliance dot map (site/assets/img/world-dots.svg), member logos and site/assets/js/alliance.js.

Members and offices come from mergers-alliance.com/member-firms (October 2026); logos were saved to ref/alliance/.
"""
import json, math, os, shutil
from PIL import Image, ImageDraw

LON0, LON1, LAT0, LAT1 = -168, 180, 76, -56
W = 1400
STEP = 7

# slug, name, website, logo file, established, offices as (city, flag, lat, lon); the first office is the HQ
FIRMS = [
  ('broadspan', 'BroadSpan Capital', 'https://brocap.com/', 'Broadspan-col.png', 2001, [
    ('Miami', 'us', 25.762, -80.192), ('Mexico City', 'mx', 19.433, -99.133), ('Medellín', 'co', 6.244, -75.581),
    ('Rio de Janeiro', 'br', -22.907, -43.173), ('São Paulo', 'br', -23.551, -46.633)]),
  ('aurignac', 'Aurignac Finance', 'https://aurfi.com/', 'Aurignac-col.png', 2004, [('Paris', 'fr', 48.857, 2.352)]),
  ('bacp', 'Buenos Aires Capital Partners', 'https://www.bacp.com.ar/', 'BACP-monotrim-dresner25.png', 1991, [
    ('Buenos Aires', 'ar', -34.604, -58.382)]),
  ('blair-franklin', 'Blair Franklin', 'https://www.blairfranklin.com/', '248.jpg', 2003, [
    ('Toronto', 'ca', 43.653, -79.383)]),
  ('dresner', 'Dresner Partners', 'https://www.dresnerpartners.com/', '420x210-dresner25.png', 1991, [
    ('Chicago', 'us', 41.878, -87.630), ('New York', 'us', 40.713, -74.006), ('Fort Lauderdale', 'us', 26.122, -80.137)]),
  ('efic', 'EFIC Partners', 'https://efic.pe/', 'Efic-col.png', 2008, [('Lima', 'pe', -12.046, -77.043)]),
  ('ethica', 'Ethica Group', 'https://ethica-group.com/en/', 'Ethica-col.png', 2010, [('Milan', 'it', 45.464, 9.190)]),
  ('evolve', 'Evolve Corporate Finance', 'https://evolvecf.co.uk/', '253.png', 2022, [
    ('Birmingham', 'gb', 52.486, -1.890), ('London', 'gb', 51.507, -0.128), ('Nottingham', 'gb', 52.954, -1.158)]),
  ('greenstone', 'Greenstone Partners', 'https://greenstonepartners.com.au/', '420x210-greenstone.png', 2003, [
    ('Sydney', 'au', -33.869, 151.209)]),
  ('intercapital', 'InterCapital', 'https://inter.capital/', 'Intercapital-col.png', 2001, [
    ('Zagreb', 'hr', 45.815, 15.982), ('Ljubljana', 'si', 46.057, 14.506)]),
  ('ipopema', 'IPOPEMA', 'https://ipopema.pl/investment-banking,p2,en', 'ipopema-col.png', 2003, [
    ('Warsaw', 'pl', 52.230, 21.012)]),
  ('khronos', 'Khronos Advisory', 'http://www.khronosadvisory.com/', 'khronos-col.png', 2009, [
    ('Bangkok', 'th', 13.756, 100.502)]),
  ('montminy', 'Montminy & Co.', 'https://www.montminyco.com/', 'montminy-col.png', 2009, [
    ('Santa Monica', 'us', 34.019, -118.491), ('Orange County', 'us', 33.684, -117.826), ('Phoenix', 'us', 33.448, -112.074)]),
  ('norgestion', 'Norgestion', 'https://www.norgestion.com/', 'norgestion-col.png', 1972, [
    ('Madrid', 'es', 40.417, -3.704), ('Barcelona', 'es', 41.385, 2.173), ('Bilbao', 'es', 43.263, -2.935),
    ('San Sebastián', 'es', 43.318, -1.981), ('Pamplona', 'es', 42.812, -1.646)]),
  ('oxeye-monthis', 'Oxeye Monthis', 'http://www.monthis.com', 'oxeyemonthis-420x210-1.png', 2004, [
    ('Amsterdam', 'nl', 52.370, 4.895)]),
  ('proventis', 'Proventis Partners', 'https://proventis.com/en/home/', 'Proventis-col-v2.png', 2001, [
    ('Zurich', 'ch', 47.377, 8.542), ('Frankfurt', 'de', 50.110, 8.682), ('Hamburg', 'de', 53.551, 9.994)]),
  ('altis', 'Altis', 'https://www.altis.cl/', 'Altis-col.png', 2006, [('Santiago', 'cl', -33.449, -70.669)]),
  ('singhi', 'Singhi Advisors', 'https://singhi.com/', '420x210-singhi.png', 1989, [
    ('Mumbai', 'in', 19.076, 72.878), ('New Delhi', 'in', 28.614, 77.209), ('Bengaluru', 'in', 12.972, 77.595)]),
  ('stewart', 'Stewart & Co', None, 'stewartnco-420x210-1.png', 2023, [('Seoul', 'kr', 37.567, 126.978)]),
  ('tokyo-kyodo', 'Tokyo Kyodo FAS', 'https://www.tkao.com/e/about-us/', 'Tokyo-Kyodo.png', 1993, [
    ('Tokyo', 'jp', 35.676, 139.650)]),
]

# Alliance-wide deal figures quoted on mergers-alliance.com
ALLIANCE_DEALS = '1,260+'
ALLIANCE_VALUE = '$62B+'


def miller_y(lat):
  return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))


SCALE = W / (LON1 - LON0)
Y0 = miller_y(LAT0)
H = round((Y0 - miller_y(LAT1)) * math.degrees(1) * SCALE)


def project(lon, lat):
  return (lon - LON0) * SCALE, (Y0 - miller_y(max(min(lat, 85), -85))) * math.degrees(1) * SCALE


def land_polygons(path):
  topo = json.load(open(path))
  (sx, sy), (tx, ty) = topo['transform']['scale'], topo['transform']['translate']
  arcs = []
  for arc in topo['arcs']:
    x = y = 0
    pts = []
    for dx, dy in arc:
      x += dx
      y += dy
      pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)

  def ring(idx):
    pts = []
    for i in idx:
      a = arcs[i] if i >= 0 else arcs[~i][::-1]
      pts.extend(a if not pts else a[1:])
    return pts

  for geom in topo['objects']['land']['geometries']:
    polys = geom['arcs'] if geom['type'] == 'MultiPolygon' else [geom['arcs']]
    for poly in polys:
      yield [ring(r) for r in poly]


def build_map():
  img = Image.new('L', (W, H), 0)
  draw = ImageDraw.Draw(img)
  for rings in land_polygons('ref/alliance/land-50m.json'):
    for n, r in enumerate(rings):
      # Rings crossing the antimeridian (Chukotka, Fiji) would smear across the map; unwrap them and draw both copies
      pts = [r[0]]
      for lon, lat in r[1:]:
        prev = pts[-1][0]
        pts.append((lon + 360 * round((prev - lon) / 360), lat))
      for shift in (0, -360) if max(p[0] for p in pts) > 180 else (0, 360) if min(p[0] for p in pts) < -180 else (0,):
        draw.polygon([project(lon + shift, lat) for lon, lat in pts], fill=0 if n else 255)
  px = img.load()
  dots = []
  for gy in range(STEP // 2, H, STEP):
    for gx in range(STEP // 2, W, STEP):
      cell = [px[x, y] for x in range(gx - STEP // 2, min(gx + STEP // 2 + 1, W)) for y in range(gy - STEP // 2, min(gy + STEP // 2 + 1, H))]
      if sum(c > 0 for c in cell) / len(cell) > 0.12:
        dots.append(f'M{gx} {gy}h0')
  svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><path d="{"".join(dots)}" stroke="#fff" '
         f'stroke-opacity=".26" stroke-width="3.6" stroke-linecap="round" fill="none"/></svg>')
  open('site/assets/img/world-dots.svg', 'w').write(svg)
  print(f'world-dots.svg: {len(dots)} dots, {W}x{H}, {len(svg) // 1024}KB')


def build_logo(slug, src):
  im = Image.open(f'ref/alliance/{src}').convert('RGBA')
  if slug == 'bacp':
    # White-on-transparent seal: recolour to the brand navy so it reads on white tiles
    alpha = im.getchannel('A')
    im = Image.new('RGBA', im.size, (11, 35, 65, 255))
    im.putalpha(alpha)
  bg = Image.new('RGBA', im.size, 'white')
  bg.alpha_composite(im)
  ink = Image.eval(bg.convert('L'), lambda v: 255 if v < 245 else 0)
  im = im.crop(ink.getbbox())
  im.thumbnail((400, 160))
  im.save(f'site/assets/img/alliance/{slug}.png', optimize=True)


def main():
  build_map()
  os.makedirs('site/assets/img/alliance', exist_ok=True)
  firms = []
  for slug, name, url, logo, est, offices in FIRMS:
    build_logo(slug, logo)
    firms.append({
      'slug': slug, 'name': name, 'url': url, 'logo': f'assets/img/alliance/{slug}.png', 'est': est,
      'offices': [{'city': c, 'flag': f, 'x': round(project(lon, lat)[0] / W * 100, 3),
                   'y': round(project(lon, lat)[1] / H * 100, 3)} for c, f, lat, lon in offices]})
    for _, f, _, _ in offices:
      shutil.copy(f'ref/flags/{f}.svg', f'site/assets/img/flags/{f}.svg')
  stats = {'firms': len(firms), 'offices': sum(len(f['offices']) for f in firms),
           'countries': len({o['flag'] for f in firms for o in f['offices']}), 'deals': ALLIANCE_DEALS, 'value': ALLIANCE_VALUE}
  open('site/assets/js/alliance.js', 'w').write(f'window.ALLIANCE = {json.dumps({"stats": stats, "firms": firms}, ensure_ascii=False)};\n')
  print('alliance.js:', stats)


main()
