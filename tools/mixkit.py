import sys, re, urllib.request
for q in sys.argv[1:]:
  url=f'https://mixkit.co/free-stock-video/{q}/'
  try:
    s=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read().decode('utf-8','ignore')
  except Exception as e:
    print('==',q,'ERR',e); continue
  items=re.findall(r'href="/free-stock-video/([a-z0-9-]+)-(\d+)/" class="item-grid-video-player__overlay-link">\s*([^<]+?)\s*</a>',s)
  print('==',q,len(items))
  for slug,i,t in items: print(f'  {i}\t{t}')
