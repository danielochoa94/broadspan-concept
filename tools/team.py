import sys, re, json, subprocess, os
GROUPS={'21':'board','19':'advisory','18':'senior-advisors'}
urls=[l.strip() for l in open(os.path.join(sys.argv[1],'urls.txt')) if l.strip()]
out={}; order=[]
for u in urls:
  group=GROUPS[re.search(r'/(\d+)-',u).group(1)]
  f=os.path.basename(u)+'.html'
  t=subprocess.run(['python3','-I','tools/text.py',os.path.join(sys.argv[1],f)],capture_output=True,text=True).stdout
  block=t.split('237-vinicius-dias] Vinicius Días',1)[1]
  block=re.split(r'This email address|Copyright',block)[0]
  lines=[l.strip() for l in block.split('\n') if l.strip() and 'medical-definitions' not in l]
  img=None
  if lines[0].startswith('<img'):
    img=re.search(r'<img (\S+)',lines[0]).group(1); lines=lines[1:]
  name,title,*paras=lines
  if name==title: name='Mark Rosen'
  langs=None
  if paras and paras[-1].lower().startswith('spoken languages'):
    langs=re.sub(r'(?i)spoken languages:\s*','',paras.pop()).rstrip('. ')
  key=name
  if key in out:
    out[key]['groups'].append(group); continue
  out[key]={'name':name,'title':title,'img':img,'languages':langs,'bio':paras,'groups':[group]}
  order.append(key)
json.dump([out[k] for k in order],sys.stdout,ensure_ascii=False,indent=1)
