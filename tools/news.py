import sys, re, json, subprocess
out=[]
for f in sys.argv[1:]:
  t=subprocess.run(['python3','-I','tools/text.py',f],capture_output=True,text=True).stdout
  t=t.split('<img /images/bsam.png alt=Logo>',1)[1].split('Copyright')[0]
  lines=[l.strip() for l in t.split('\n') if l.strip() and 'medical-definitions' not in l]
  i=0
  while i+3<len(lines):
    if re.search(r'(?i)(press release|announcement)\s*[–-]',lines[i]) and 'Link to a PDF' in lines[i+3]:
      kind,date=[s.strip() for s in re.split(r'\s*[–-]\s*',lines[i],1)]
      pdf=re.search(r'\[([^\]]+)\]',lines[i+3]).group(1)
      out.append({'kind':kind.title(),'date':date.title().replace(',',''),'title':lines[i+1],'summary':lines[i+2],'pdf':'https://brocap.com'+pdf.replace(' ','%20')})
      i+=4
    else: i+=1
json.dump(out,sys.stdout,ensure_ascii=False,indent=1)
