const allowed = new Set(['https://www.zhaoganlab.cn','https://zhaoganlab.cn']);
export default {
 async fetch(request,env) {
  const origin=request.headers.get('Origin');
  const headers={'Content-Type':'application/json','Cache-Control':'no-store','Vary':'Origin'};
  if(allowed.has(origin)) Object.assign(headers,{'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'GET,POST,OPTIONS','Access-Control-Allow-Headers':'Content-Type'});
  const respond=(data,status=200)=>new Response(JSON.stringify(data),{status,headers});
  if(!allowed.has(origin)) return respond({error:'Origin not allowed'},403);
  if(request.method==='OPTIONS') return new Response(null,{status:204,headers});
  const path=new URL(request.url).pathname;
  try {
   if(path==='/visit' && request.method==='POST') {
    if(Number(request.headers.get('Content-Length'))>512)return respond({error:'Too large'},413);
    const raw=await request.text();if(raw.length>512)return respond({error:'Too large'},413);
    const {id}=JSON.parse(raw);if(!/^[a-f0-9-]{36}$/i.test(id||''))return respond({error:'Invalid event'},400);
    const country=/^[A-Z]{2}$/.test(request.cf?.country||'')?request.cf.country:'ZZ';
    await env.DB.prepare('INSERT OR IGNORE INTO visits(id,country,created) VALUES (?,?,?)').bind(id,country,new Date().toISOString()).run();
   } else if(!(path==='/stats' && request.method==='GET')) return respond({error:'Not found'},404);
   const rows=await env.DB.prepare('SELECT country,count FROM countries ORDER BY count DESC').all();
   const started=await env.DB.prepare("SELECT value FROM metadata WHERE key='started_at'").first();
   return respond({total:rows.results.reduce((n,r)=>n+r.count,0),countries:rows.results,started_at:started?.value||null});
  } catch {return respond({error:'Statistics unavailable'},503);}
 },
 async scheduled(event,env){await env.DB.prepare("DELETE FROM visits WHERE created < ?").bind(new Date(Date.now()-7*86400000).toISOString()).run();}
};
