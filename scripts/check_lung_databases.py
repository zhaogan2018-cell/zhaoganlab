"""Check curated links without deleting records or treating bot blocks as retirement."""
import json,concurrent.futures,re
from html.parser import HTMLParser
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1];PATH=ROOT/'content/lung-databases.json'
def check(item):
 try:
  req=Request(item['url'],headers={'User-Agent':'ZhaoganLabResourceCheck/1.0'})
  with urlopen(req,timeout=20) as r:
   body=r.read(12000).decode('utf-8','replace').lower();code=r.status;resolved=r.url
  if any(x in body for x in ['domain is for sale','buy this domain','this domain has expired']):return item,410,resolved
  return item,code,resolved
 except HTTPError as e:return item,e.code,None
 except Exception:return item,0,None

class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.href=None;self.label=''
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.label=''
 def handle_data(self,data):
  if self.href:self.label+=data
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.links.append((self.href,self.label.strip()));self.href=None

def discover(items):
 try:
  with urlopen(Request('https://app.lungmap.net/',headers={'User-Agent':'ZhaoganLabResourceCheck/1.0'}),timeout=25) as r:body=r.read(1000000).decode()
  parser=Links();parser.feed(body);known={i['url'] for i in items}
  discovered=0;attempted=0
  for href,label in parser.links:
   if attempted>=8:break
   url=urljoin('https://app.lungmap.net/',href)
   if urlsplit(url).hostname not in ['app.lungmap.net','apps.lungmap.net'] or not re.search(r'lung|BPD|ILD|post flu|pediatric',label,re.I) or url in known:continue
   attempted+=1
   item={'name':'LungMAP · '+label,'category':'综合','species':'See source','url':url,'description_zh':'LungMAP官方应用目录新增入口。','description_en':'Resource listed in the official LungMAP application directory.'}
   _,code,_=check(item)
   if 200<=code<300:items.append(item);known.add(url);discovered+=1
 except Exception:pass # Discovery outage must not remove existing links.

def main():
 items=json.loads(PATH.read_text(encoding='utf-8'));discover(items);today=datetime.now(timezone.utc).strftime('%Y-%m-%d');report=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for item,code,url in pool.map(check,items):
   # Count failures once per date, even if manually rerun.
   previous=item.get('last_checked');item['last_checked']=today;item['http_status']=code
   if 200<=code<300:
    item.update(active=True,consecutive_failures=0,health='reachable')
    if url and urlsplit(url).hostname==urlsplit(item['url']).hostname:item['resolved_url']=url
    elif url:item['suggested_url']=url # cross-domain changes require identity review
   elif code in [401,403,429]:item['health']='access_restricted';item['consecutive_failures']=0 # not evidence of retirement
   elif code in [404,410,0] or code>=500:
    failures=item.get('consecutive_failures',0)+(previous!=today);item['consecutive_failures']=failures
    threshold=3 if code in [404,410] else 7
    item['health']='unreachable';item['active']=False if failures>=threshold else item.get('active',True)
   report.append({'name':item['name'],'status':code,'active':item.get('active',True)})
 PATH.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'content/lung-database-health.json').write_text(json.dumps({'checked':today,'items':report},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
