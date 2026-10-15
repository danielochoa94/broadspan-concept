"""Generates site/assets/img/network.svg: offices and deal locations across the Americas, arcs from Miami."""
import math

W, H = 600, 660
LON0, LON1, LAT0, LAT1 = -104, -36, 30, -38

OFFICES = {
  'Miami': (25.76, -80.19), 'Mexico City': (19.43, -99.13), 'Medellín': (6.24, -75.58),
  'Rio de Janeiro': (-22.91, -43.17), 'São Paulo': (-23.55, -46.63),
}
LABEL_SIDE = {'Miami': 'r', 'Mexico City': 'r', 'Medellín': 'l', 'Rio de Janeiro': 'r', 'São Paulo': 'l'}

DEALS = [
  (10.65, -61.5), (-34.6, -58.4), (-0.18, -78.47), (18.47, -66.1), (17.25, -88.76), (18.49, -69.93), (8.98, -79.52),
  (9.93, -84.08), (12.17, -68.98), (-31.42, -64.18), (-12.05, -77.04), (14.63, -90.51), (13.69, -89.22), (18.0, -76.8),
  (13.1, -59.6), (12.05, -61.75), (17.3, -62.72), (14.0, -61.0), (17.12, -61.85), (25.05, -77.35), (18.54, -72.34),
  (15.5, -88.03), (-16.5, -68.15), (-25.43, -49.27), (-26.3, -48.85), (-3.73, -38.52), (-8.05, -34.9), (-19.92, -43.94),
  (-30.03, -51.23), (-12.97, -38.5), (-15.79, -47.88), (4.71, -74.07), (3.45, -76.53), (25.67, -100.31),
  (20.67, -103.35), (28.63, -106.07),
]


def xy(lat, lon):
  x = (lon - LON0) / (LON1 - LON0) * W
  y = (lat - LAT0) / (LAT1 - LAT0) * H
  return round(x, 1), round(y, 1)


def arc(a, b, bend=0.22):
  (x1, y1), (x2, y2) = a, b
  mx, my = (x1 + x2) / 2, (y1 + y2) / 2
  dx, dy = x2 - x1, y2 - y1
  cx, cy = mx + dy * bend, my - dx * bend
  return f'M{x1},{y1} Q{cx:.1f},{cy:.1f} {x2},{y2}', math.hypot(dx, dy) * 1.15


def main():
  hub = xy(*OFFICES['Miami'])
  parts = []
  grid = []
  for lat in range(30, -41, -10):
    y = xy(lat, LON0)[1]
    grid.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
  for lon in range(-100, -35, 10):
    x = xy(LAT0, lon)[0]
    grid.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
  parts.append(f'<g class="grid">{"".join(grid)}</g>')

  arcs = []
  for i, (lat, lon) in enumerate(DEALS):
    d, length = arc(hub, xy(lat, lon), 0.18 if i % 2 else -0.14)
    arcs.append(f'<path class="a" d="{d}" style="--l:{length:.0f};--d:{0.4 + i * 0.045:.2f}s"/>')
  for i, (name, ll) in enumerate(OFFICES.items()):
    if name == 'Miami':
      continue
    d, length = arc(hub, xy(*ll), 0.2)
    arcs.append(f'<path class="o" d="{d}" style="--l:{length:.0f};--d:{0.2 + i * 0.15:.2f}s"/>')
  parts.append(f'<g fill="none">{"".join(arcs)}</g>')

  dots = [f'<circle class="dd" cx="{x}" cy="{y}" r="2.6"/>' for x, y in (xy(*p) for p in DEALS)]
  parts.append(f'<g>{"".join(dots)}</g>')

  offices = []
  for name, ll in OFFICES.items():
    x, y = xy(*ll)
    side = LABEL_SIDE[name]
    tx, anchor = (x + 14, 'start') if side == 'r' else (x - 14, 'end')
    offices.append(f'<circle class="halo" cx="{x}" cy="{y}" r="11"/><circle class="od" cx="{x}" cy="{y}" r="4.5"/>'
                   f'<text x="{tx}" y="{y + 4}" text-anchor="{anchor}">{name}</text>')
  parts.append(f'<g>{"".join(offices)}</g>')

  style = """
.grid line{stroke:#fff;stroke-opacity:.05;stroke-width:1}
.a{stroke:#9db8dd;stroke-opacity:.28;stroke-width:.8;stroke-dasharray:var(--l);stroke-dashoffset:var(--l);animation:draw 1.6s cubic-bezier(.3,.6,.3,1) var(--d) forwards}
.o{stroke:#9db8dd;stroke-opacity:.85;stroke-width:1.4;stroke-dasharray:var(--l);stroke-dashoffset:var(--l);animation:draw 1.4s cubic-bezier(.3,.6,.3,1) var(--d) forwards}
.dd{fill:#9db8dd;fill-opacity:.55}
.od{fill:#fff}
.halo{fill:#9db8dd;fill-opacity:.18;transform-box:fill-box;transform-origin:center;animation:pulse 3.2s ease-in-out infinite}
text{font:500 13px Inter,system-ui,sans-serif;fill:#fff;fill-opacity:.82;letter-spacing:.02em}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes pulse{50%{transform:scale(1.6);fill-opacity:.05}}
@media (prefers-reduced-motion:reduce){.a,.o{animation:none;stroke-dashoffset:0}.halo{animation:none}}
"""
  svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 -20 {W + 120} {H + 40}" role="img" '
         f'aria-label="BroadSpan offices and transaction locations across the Americas"><style>{style}</style>'
         + ''.join(parts) + '</svg>')
  open('site/assets/img/network.svg', 'w').write(svg)


main()
