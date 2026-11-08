"""Refresh official news feeds; preserve existing summaries and tolerate source outages."""
import json,os,re,time,html
from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.request import Request,urlopen
from urllib.parse import urlsplit,urlunsplit
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'content/science-news.json'
FEEDS={'Nature':'https://www.nature.com/nature.rss','Science':'https://www.science.org/rss/news_current.xml','Cell':'https://www.cell.com/cell/inpress.rss'}
def request(url,data=None,headers=None):
 for attempt in range(3):
  try:
   with urlopen(Request(url,data=data,headers={'User-Agent':'ZhaoganLabNews/1.0',**(headers or {})}),timeout=45) as r:return r.read()
  except Exception:
   if attempt==2:raise
   time.sleep(2**attempt)
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s))).strip()
def fields(node):return {x.tag.split('}')[-1]:''.join(x.itertext()).strip() for x in node}
def generate(title,brief):
 key=os.getenv('NEWS_AI_API_KEY')
 if not key:return None
 body={'model':(os.getenv('NEWS_AI_MODEL') or 'gpt-4.1-mini'),'messages':[{'role':'system','content':'Summarize only the supplied publisher news title and teaser, not an unseen full article. Return JSON with zh (Chinese title), en (English title), summary_zh (one concise Chinese paragraph), summary_en (one concise English paragraph). Paraphrase, do not invent details or overstate evidence.'},{'role':'user','content':json.dumps({'title':title,'teaser':brief})}],'response_format':{'type':'json_object'}}
 result=json.loads(request(os.getenv('NEWS_AI_ENDPOINT','https://api.openai.com/v1/chat/completions'),json.dumps(body).encode(),{'Authorization':'Bearer '+key,'Content-Type':'application/json'}))
 value=json.loads(result['choices'][0]['message']['content']);assert all(isinstance(value.get(k),str) and value[k].strip() for k in ['zh','en','summary_zh','summary_en']);return value

def main():
 now=datetime.now(timezone(timedelta(hours=8)));month=now.strftime('%Y-%m');today=now.strftime('%Y-%m-%d');old=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {'items':[]}
 known={i['url']:i for i in old['items'] if i['date'].startswith(month) and not (i.get('rss_preview') and re.search(r'books in brief|book review|podcast|correction',i.get('en',''),re.I))};statuses={};success=0
 for source,url in FEEDS.items():
  try:
   root=ET.fromstring(request(url));found=0
   for node in root.iter():
    if node.tag.split('}')[-1]!='item':continue
    f=fields(node);date=(f.get('date') or f.get('publicationDate') or '')[:10];link=f.get('link','');title=clean(f.get('title',''));brief=clean(f.get('description') or f.get('encoded',''));section=f.get('section','')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date) or date[:7]!=month or date>today:continue
    if source=='Nature' and ('/articles/d41586-' not in link or re.search(r'books in brief|book review|podcast|correction',title,re.I)):continue
    if source=='Cell' and not re.search(r'news',section,re.I):continue
    if source=='Science' and '/content/article/' not in link:continue
    domain=urlsplit(link).hostname
    if domain not in ['www.nature.com','www.science.org','www.cell.com']:continue
    link=urlunsplit(('https',domain,urlsplit(link).path,'',''));found+=1
    if link in known and not known[link].get('rss_preview'):continue
    brief=re.sub(r'^Nature, Published online:.*?doi:\S+\s*','',brief)
    if not title or not brief:continue
    try:summary=generate(title,brief)
    except Exception as exc:
     statuses[source+'_summary']='Summary service failed; RSS preview retained: '+type(exc).__name__;summary=None
    # Short, explicitly labelled syndicated teaser when no summarizer is configured.
    preview=' '.join(brief.split()[:max(0,24-len(title.split()))])
    item={'date':date,'source':source,'url':link,**(summary or {'zh':title,'en':title,'summary_zh':'来源英文简讯：'+preview,'summary_en':'Publisher teaser: '+preview}),'rss_preview':not bool(summary)}
    known[link]=item
   statuses[source]={'ok':True,'matching_items':found};success+=1
  except Exception as exc:statuses[source]={'ok':False,'error':type(exc).__name__+': '+str(exc)[:150]}
 if not success:raise RuntimeError('All news feeds failed; previous data preserved')
 result={'month':month,'checked_at':now.isoformat(),'sources':statuses,'summary_mode':'ai' if os.getenv('NEWS_AI_API_KEY') else 'rss_preview','items':sorted(known.values(),key=lambda i:(i['date'],i['url']),reverse=True)}
 temp=OUT.with_suffix('.tmp');temp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(OUT)
 print(json.dumps({'month':month,'items':len(result['items']),'sources':statuses},ensure_ascii=False))
if __name__=='__main__':main()
