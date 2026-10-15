import sys, re, json, subprocess
FIELDS=['Client','Country','Sector','Value','Completion','Description']
out=[]
for practice,f in [(a.split('=')[0],a.split('=')[1]) for a in sys.argv[1:]]:
  t=subprocess.run(['python3','-I','tools/text.py',f],capture_output=True,text=True).stdout
  t=t.split('<img /images/bsam.png alt=Logo>',1)[1].split('Copyright')[0]
  lines=[l.strip() for l in t.split('\n') if l.strip() and 'medical-definitions' not in l]
  cur=None; last=None
  for i,l in enumerate(lines):
    if l.startswith('<img ') and i>0 and not lines[i-1].startswith(('[','<')):
      if cur and cur.get('description','').endswith(lines[i-1]):
        cur['description']=cur['description'][:-len(lines[i-1])].strip()
      cur={'practice':practice,'name':lines[i-1],'logo':re.search(r'<img (\S+)',l).group(1)}
      out.append(cur); last=None; continue
    if cur is None: continue
    m=re.match(r'(%s)\s*:\s*(.*)'%'|'.join(FIELDS),l)
    if m:
      last=m.group(1).lower(); cur[last]=m.group(2).strip()
    elif last=='description':
      cur['description']=(cur['description']+' '+l).strip()
json.dump(out,sys.stdout,ensure_ascii=False,indent=1)
