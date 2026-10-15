import sys, re, html
from html.parser import HTMLParser
class P(HTMLParser):
  def __init__(s):
    super().__init__(); s.out=[]; s.skip=0
  def handle_starttag(s,t,a):
    if t in('script','style','noscript'): s.skip+=1
    if t=='a':
      h=dict(a).get('href','')
      if h and not h.startswith(('#','/media','/templates')): s.out.append(f' [{h}] ')
    if t=='img':
      d=dict(a); s.out.append(f" <img {d.get('src','')} alt={d.get('alt','')}> ")
    if t in('p','div','br','li','h1','h2','h3','h4','tr','td'): s.out.append('\n')
  def handle_endtag(s,t):
    if t in('script','style','noscript'): s.skip-=1
  def handle_data(s,d):
    if not s.skip: s.out.append(d)
p=P(); p.feed(open(sys.argv[1],encoding='utf-8',errors='ignore').read())
t=re.sub(r'[ \t]+',' ',''.join(p.out)); t=re.sub(r'\n\s*\n+','\n',t)
print(t)
