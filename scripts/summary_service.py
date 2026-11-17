"""Shared, source-grounded summary service. Credentials stay in Actions secrets."""
import json, os, re, time
from urllib.request import Request, urlopen

def configured():
    return bool(os.getenv('NEWS_AI_API_KEY'))

def summarize(payload, instruction):
    key=os.getenv('NEWS_AI_API_KEY')
    if not key: raise RuntimeError('NEWS_AI_API_KEY is not configured')
    body={'model':os.getenv('NEWS_AI_MODEL') or 'gpt-4.1-mini','messages':[
        {'role':'system','content':instruction+' Use only supplied evidence. Never invent results or numbers. Distinguish human from mouse, association from causation. Return JSON only.'},
        {'role':'user','content':json.dumps(payload,ensure_ascii=False)}], 'response_format':{'type':'json_object'}}
    endpoint=os.getenv('NEWS_AI_ENDPOINT') or 'https://api.openai.com/v1/chat/completions'
    for attempt in range(3):
        try:
            req=Request(endpoint,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
            with urlopen(req,timeout=90) as response: result=json.load(response)
            return json.loads(result['choices'][0]['message']['content'])
        except Exception:
            if attempt==2: raise
            time.sleep(2**attempt)

def valid_pair(value):
    return all(isinstance(value.get(k),str) and value[k].strip() for k in ['zh','en']) and bool(re.search(r'[\u3400-\u9fff]',value['zh']))
