#!/usr/bin/env python3
"""Resolve archive pictures using live Library of Congress item metadata.
Does not invent pictures or silently substitute an unrelated illustration.
"""
from pathlib import Path
import json, time, urllib.request, urllib.error, urllib.parse, re

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'assets'/'images'
DEST.mkdir(parents=True,exist_ok=True)
MANIFEST=ROOT/'assets'/'image_manifest.json'
ITEMS={
 'archive_01.jpg':'https://www.loc.gov/item/99614139/',
 'archive_02.jpg':'https://www.loc.gov/item/2017793162/',
 'archive_03.jpg':'https://www.loc.gov/resource/cph.3b23576/',
 'archive_04.jpg':'https://www.loc.gov/item/2016797005/',
 'archive_05.jpg':'https://www.loc.gov/resource/g3701p.rr000070/',
 'archive_06.jpg':'https://www.loc.gov/item/2004671834/',
 'archive_07.jpg':'https://www.loc.gov/item/gm70005360/',
 'archive_08.jpg':'https://www.loc.gov/item/96688053/',
 'archive_09.jpg':'https://www.loc.gov/item/93502015/'
}
HEADERS={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36','Accept':'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'}

def get(url,referer=None):
 headers=dict(HEADERS)
 if referer: headers['Referer']=referer
 req=urllib.request.Request(url, headers=headers)
 with urllib.request.urlopen(req,timeout=22) as r:
  return r.read(),r.headers.get('Content-Type','')

def identify(data):
 if data[:3]==b'\xff\xd8\xff':return 'jpg'
 if data[:8]==b'\x89PNG\r\n\x1a\n':return 'png'
 if data[:4] in (b'RIFF',):return 'webp'
 return None

def collect(x,urls):
 if isinstance(x,dict):
  for key,val in x.items():
   if key in ('image','images','url','id','download','full','medium','large','service','resource_url','thumbnail'):
    collect(val,urls)
   elif isinstance(val,(dict,list)):
    collect(val,urls)
 elif isinstance(x,list):
  for val in x:collect(val,urls)
 elif isinstance(x,str) and x.startswith('https://') and (('tile.loc.gov/' in x or 'loc.gov/' in x or 'cdn.loc.gov/' in x) and re.search(r'\.(jpg|jpeg|png|gif|webp)(?:[?]|$)',x,re.I)):
  urls.append(x)

def metadata_urls(record):
 api=record.rstrip('/')+'/?fo=json'
 data,_=get(api,record)
 meta=json.loads(data)
 links=[]
 collect(meta,links)
 # Prefer reasonable JPG derivative. GIF and Jp2 files are deliberately excluded.
 links=[u for u in links if re.search(r'\.(jpg|jpeg|png)(?:\?|$)',u,re.I)]
 # Bigger copies appear first but avoid giant master downloads.
 links.sort(key=lambda u: (0 if re.search(r'_(?:640px|1024px|medium|v|r)\.',u) else 1, len(u)))
 return list(dict.fromkeys(links))

manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
found=0;missing=[]
for entry in manifest:
 filename=entry['file'];dst=DEST/filename;record=ITEMS[filename]
 if dst.exists() and dst.stat().st_size>1000 and identify(dst.read_bytes()):
  print('OK (already downloaded):',filename);found+=1;continue
 old=entry['url']; candidates=[]
 try:
  candidates=metadata_urls(record)
  print(f'{filename}: {len(candidates)} source images found in LOC metadata')
 except Exception as ex:
  print(f'{filename}: metadata unavailable ({str(ex)[:70]})')
 # Original link is a last resort. It is known that many originals are broken.
 candidates=list(dict.fromkeys(candidates+[old]))
 errors=[]
 for url in candidates[:18]:
  try:
   blob,mime=get(url,record)
   kind=identify(blob)
   if len(blob)<1500 or kind!='jpg':
    errors.append('not a JPEG');continue
   dst.write_bytes(blob)
   entry['downloaded_from']=url
   entry['record']=record
   print('SAVED',filename,len(blob),'bytes')
   found+=1
   break
  except Exception as e:errors.append(str(e)[:55])
 else:
  missing.append(filename)
  print('NOT SAVED',filename,'; sample errors:',', '.join(errors[:2]))
 time.sleep(.2)

MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'\nRESULT: {found}/9 genuine images present.')
if missing:
 print('Still missing:',', '.join(missing))
 print('Some archive hosts forbid scripted downloading. Use record links in assets/image_manifest.json.')
else:
 print('All local images downloaded. You can now open index.html.')
input('Press Enter to close...')
