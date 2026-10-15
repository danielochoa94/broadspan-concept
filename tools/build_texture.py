"""Generates site/assets/img/lines.svg: two families of fanning curves that form soft moiré on navy panels."""
import math

W, H = 1600, 1200


def family(n, f):
  paths = []
  for i in range(n):
    t = i / (n - 1)
    (x0, y0), (c1x, c1y), (c2x, c2y), (x1, y1) = f(t)
    paths.append(f'<path d="M{x0:.1f},{y0:.1f}C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {x1:.1f},{y1:.1f}"/>')
  return ''.join(paths)


def sweep(t):
  y0 = -200 + t * 1700
  y1 = 250 + t * 420
  return (-100, y0), (W * 0.38, y0 + 420 * math.sin(t * math.pi)), (W * 0.62, y1 - 520 * t), (W + 100, y1)


def counter(t):
  x0 = 300 + t * 1500
  return (x0, H + 100), (x0 - 200, H * 0.55), (W * 0.9 - t * 300, H * 0.35), (W + 100, -100 + t * 500)


svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
       f'<g fill="none" stroke="#86acdf" stroke-width="1">'
       f'<g stroke-opacity=".17">{family(150, sweep)}</g>'
       f'<g stroke-opacity=".10">{family(90, counter)}</g>'
       '</g></svg>')
open('site/assets/img/lines.svg', 'w').write(svg)
