import json,time,re,calendar,os
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
JOURNALS=['Cell','Nature','Science','Nat Cell Biol','Nat Commun','Sci Adv','Sci Transl Med','Sci Immunol','Immunity','Nat Immunol','Nat Med','Cell Stem Cell','Dev Cell','Cell Metab','Cell Rep','J Clin Invest','JCI Insight','J Exp Med','Circulation','Circ Res']
def api(kind,**args):
    time.sleep(.4)
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'+kind+'.fcgi?'+urlencode(dict(tool='ZhaoLabLungFrontier',email='zhaogan@xmu.edu.cn',**args))
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'ZhaoLabLungFrontier/1.0'}),timeout=60) as r:return r.read()
        except Exception:
            if attempt==2:raise
            time.sleep(2**attempt)
def main():
    now=datetime.now(timezone(timedelta(hours=8)))
    month=os.environ.get('FRONTIER_MONTH',now.strftime('%Y-%m'))
    y,m=map(int,month.split('-')); serial=y*12+m-1-2; sy,sm=divmod(serial,12); start=f'{sy}/{sm+1:02}/01';start_month=f'{sy}-{sm+1:02}';end=f'{y}/{m:02}/{calendar.monthrange(y,m)[1]}'
    if month==now.strftime('%Y-%m'):end=now.strftime('%Y/%m/%d')
    q='('+' OR '.join('"'+j+'"[Journal]' for j in JOURNALS)+') AND (lung[Title/Abstract] OR pulmonary[Title/Abstract] OR alveolar[Title/Abstract]) AND (injur*[Title/Abstract] OR repair[Title/Abstract] OR fibros*[Title/Abstract] OR develop*[Title/Abstract] OR regenerat*[Title/Abstract] OR pneumonia[Title/Abstract] OR infection[Title/Abstract] OR epithel*[Title/Abstract] OR endothel*[Title/Abstract] OR vascular[Title/Abstract]) NOT (neoplasms[MeSH Terms] OR cancer[Title] OR tumor[Title] OR tumour[Title] OR carcinoma[Title] OR metastas*[Title]) AND ("'+start+'"[Date - Publication] : "'+end+'"[Date - Publication])'
    data=json.loads(api('esearch',db='pubmed',term=q,retmode='json',retmax=10000,sort='pub date'))['esearchresult'];ids=data['idlist']
    if len(ids)!=int(data['count']):raise RuntimeError('Incomplete search results')
    items=[]
    def txt(n):return ''.join(n.itertext()).strip() if n is not None else ''
    for offset in range(0,len(ids),100):
        root=E.fromstring(api('efetch',db='pubmed',id=','.join(ids[offset:offset+100]),retmode='xml'))
        for a in root.findall('PubmedArticle'):
            ar=a.find('MedlineCitation/Article');pmid=txt(a.find('MedlineCitation/PMID'));title=txt(ar.find('ArticleTitle'));abstract=' '.join(txt(x) for x in ar.findall('Abstract/AbstractText'));types=[txt(x) for x in ar.findall('PublicationTypeList/PublicationType')]
            if any(x in types for x in ['Review','Editorial','Comment','News','Published Erratum','Retracted Publication']):continue
            if re.search(r'cancer|tumou?r|carcinoma|metasta|neopla',title+' '+abstract,re.I):continue
            date=ar.find('ArticleDate')
            if date is None:date=ar.find('Journal/JournalIssue/PubDate')
            date_text='-'.join(txt(date.find(x)) for x in ['Year','Month','Day']) if date is not None else ''
            # Prefer electronic publication date over the later print issue.
            if not (start_month <= date_text[:7] <= month) or date_text[:10] > now.strftime('%Y-%m-%d'):continue
            items.append(dict(pmid=pmid,title=title,journal=txt(ar.find('Journal/Title')),date=date_text,abstract=abstract,url='https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/'))
    dest=ROOT/'content/lung-frontier-candidates.json';dest.write_text(json.dumps(dict(month=month,checked_at=now.isoformat(),query=q,search_count=int(data['count']),items=items),ensure_ascii=False,indent=2),encoding='utf-8')
    cache_path=ROOT/'content/lung-frontier-summaries.json';cache=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}
    published=[]
    for item in items:
        summary=cache.get(item['pmid'])
        if summary and summary.get('include'):
            published.append({k:v for k,v in item.items() if k!='abstract'}|{'summary_zh':summary['zh'],'summary_en':summary['en']})
    output=dict(start_month=start_month,month=month,checked_at=now.isoformat(),query=q,pending_count=sum(i['pmid'] not in cache for i in items),items=published)
    (ROOT/'content/lung-frontier.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Month:',month,'search hits:',data['count'],'candidates:',len(items),'published:',len(published),'pending:',output['pending_count'])
if __name__=='__main__':main()
