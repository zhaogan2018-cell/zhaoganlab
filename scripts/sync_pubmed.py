#!/usr/bin/env python3
"""PubMed E-utilities sync for a hand-curated bibliography.

- Existing accepted papers are linked by PMID with conservative exact-title checks.
- New author-search hits are placed in a review queue ONLY.
- No unreviewed paper is added to the public list.
- This is deliberately not a comprehensive 'all papers by Zhao G' crawler.
"""
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'
PAPERS = CONTENT / 'publications.json'
CANDIDATES = CONTENT / 'pubmed_candidates.json'
STATUS = CONTENT / 'pubmed_status.json'
API = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
CONTACT = os.environ.get('NCBI_CONTACT_EMAIL', 'zhaogan@xmu.edu.cn')


def api(endpoint, params):
    args = {**params, 'tool': 'GanZhaoLabWebsite', 'email': CONTACT}
    key = os.environ.get('NCBI_API_KEY', '')
    if key:
        args['api_key'] = key
    req = Request(API + endpoint + '?' + urlencode(args), headers={'User-Agent':'GanZhaoLabWebsite/1.0 ('+ CONTACT +')'})
    # NCBI allows no more than 3 requests/sec without an API key.
    time.sleep(.40 if not key else .15)
    with urlopen(req, timeout=30) as response:
        return response.read()


def norm(txt):
    return re.sub(r'[^a-z0-9]+', '', txt.lower().replace('β','beta').replace('α','alpha').replace('δ','delta'))


def flatten(node):
    return ''.join(node.itertext()).strip() if node is not None else ''


def parse_articles(payload):
    out=[]
    root=ET.fromstring(payload)
    for record in root.findall('.//PubmedArticle'):
        cite=record.find('./MedlineCitation')
        if cite is None:continue
        pmid=flatten(cite.find('./PMID'))
        article=cite.find('./Article')
        if article is None:continue
        title=flatten(article.find('./ArticleTitle'))
        doi=''
        for item in record.findall('.//ArticleId'):
            if item.attrib.get('IdType')=='doi':doi=flatten(item)
        authors=[]
        for x in article.findall('./AuthorList/Author'):
            first=flatten(x.find('./ForeName'))
            last=flatten(x.find('./LastName'))
            if first or last:authors.append((first+' '+last).strip())
        journal=flatten(article.find('./Journal/Title'))
        out.append(dict(pmid=pmid,title=title,doi=doi,journal=journal,authors=authors))
    return out


def fetch_articles(ids):
    if not ids:return []
    results=[]
    for i in range(0,len(ids),50):
        part=ids[i:i+50]
        results+=parse_articles(api('efetch.fcgi',{'db':'pubmed','id':','.join(part),'retmode':'xml'}))
    return results


def search(query,max_hits=80):
    payload=api('esearch.fcgi',{'db':'pubmed','term':query,'retmode':'json','retmax':str(max_hits),'sort':'pub date'})
    return json.loads(payload)['esearchresult'].get('idlist',[])


def main():
    papers=json.loads(PAPERS.read_text(encoding='utf-8'))
    updated=0
    # Resolve any missing identifiers using exact-title PubMed searches.
    for paper in papers:
        if paper.get('pmid'):continue
        ids=search('"'+paper['title'].replace('"','')+'"[Title]',5)
        for rec in fetch_articles(ids):
            if norm(rec['title'])==norm(paper['title']) and any('zhao' in a.lower() for a in rec['authors']):
                paper['pmid']=rec['pmid'];paper['doi']=paper.get('doi') or rec['doi'];updated+=1
                break
    # Existing list: validate PMID-to-title to avoid accidental metadata corruption.
    known=fetch_articles([p['pmid'] for p in papers if p.get('pmid')])
    found={p['pmid']:p for p in known}
    for paper in papers:
        rec=found.get(paper.get('pmid'))
        if rec and norm(rec['title'])==norm(paper['title']):
            if not paper.get('doi') and rec.get('doi'):
                paper['doi']=rec['doi'];updated+=1
        elif rec:
            print('WARNING: PMID title mismatch; keeping curated record unchanged:',paper['title'],rec['title'])
    # Author discovery is intentionally conservative and excludes preprints in the query.
    query='("Zhao G"[Author] OR "Zhao Gan"[Author]) AND (lung OR pulmonary OR alveolar OR pneumonia OR lipid nanoparticle) NOT preprint[Publication Type]'
    ids=search(query,100)
    candidates=[]
    accepted={p.get('pmid') for p in papers if p.get('pmid')}
    for rec in fetch_articles(ids):
        if rec['pmid'] in accepted:continue
        # Even an exact name is not sufficient evidence of identity: review required.
        if not any(norm(a) in {'ganzhao','gzhao'} for a in rec['authors']):continue
        candidates.append(dict(pmid=rec['pmid'],title=rec['title'],journal=rec['journal'],doi=rec['doi'],pubmed_url='https://pubmed.ncbi.nlm.nih.gov/'+rec['pmid']+'/',review_status='pending'))
    candidates.sort(key=lambda x:x['title'].lower())
    PAPERS.write_text(json.dumps(papers,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    CANDIDATES.write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    STATUS.write_text(json.dumps({'last_checked':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'updated':updated,'candidates':len(candidates),'note':'Candidates require manual approval; no unreviewed records published.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Complete: {len(papers)} curated records, {updated} metadata updates, {len(candidates)} review candidates.')

if __name__=='__main__':main()
