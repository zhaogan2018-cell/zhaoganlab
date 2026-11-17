(()=>{'use strict';
const host=document.getElementById('visitor-map');if(!host)return;
const status=document.getElementById('visitor-status'),total=document.getElementById('visitor-total'),regions=document.getElementById('visitor-regions');
let geo,stats,state='loading';const colors=['#e2eaf3','#a8d8e8','#54adce','#2479ba','#16468d'];
const zh=()=>document.documentElement.lang.startsWith('zh');
const level=n=>n===0?0:n<10?1:n<100?2:n<1000?3:4;
const name=code=>{try{return code==='ZZ'?(zh()?'未知地区':'Unknown'):new Intl.DisplayNames([zh()?'zh-CN':'en'],{type:'region'}).of(code)}catch{return code}};
const ns='http://www.w3.org/2000/svg';function el(tag,attrs={},text){const node=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))node.setAttribute(k,v);if(text!==undefined)node.textContent=text;return node;}
const point=([x,y])=>[(x+180)*2.5,(90-y)*2.5];
function render(){
 const active=zh();status.textContent=state==='unconfigured'?(active?'访客统计服务待接入':'Visitor statistics awaiting activation'):state==='error'?(active?'访客统计暂时无法连接':'Visitor statistics temporarily unavailable'):state==='loading'?(active?'正在加载访问统计…':'Loading visitor statistics…'):(stats.started_at?(active?'统计起始日期：':'Counting since ')+stats.started_at.slice(0,10):'');
 if(stats)total.textContent=new Intl.NumberFormat(active?'zh-CN':'en').format(stats.total);
 if(!geo)return;host.replaceChildren();regions.replaceChildren();
 const counts=new Map((stats?.countries||[]).map(r=>[r.country,r.count]));
 const svg=el('svg',{viewBox:'0 0 900 420',role:'img','aria-label':active?'全球访问量分布地图':'World visitor distribution map'});
 for(const feature of geo.features){const code=feature.properties.code,n=counts.get(code)||0;const polygons=feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates;
 const d=polygons.map(poly=>poly.map(ring=>ring.map((p,i)=>(i?'L':'M')+point(p).join(',')).join(' ')+'Z').join(' ')).join(' ');
 const path=el('path',{d,fill:colors[level(n)]});path.append(el('title',{},name(code)+': '+n));svg.append(path);
 }
 for(const feature of geo.features){const n=counts.get(feature.properties.code)||0;if(!n)continue;const [x,y]=point([feature.properties.x,feature.properties.y]);if(Number.isFinite(x)&&Number.isFinite(y))svg.append(el('text',{x,y,'text-anchor':'middle'},n.toLocaleString()));}
 host.append(svg);const legend=document.createElement('div');legend.className='visitor-legend';['0','1–9','10–99','100–999','1,000+'].forEach((label,i)=>{const span=document.createElement('span'),dot=document.createElement('i');dot.style.background=colors[i];span.append(dot,document.createTextNode(label));legend.append(span)});host.append(legend);
 for(const row of stats?.countries||[]){const span=document.createElement('span');span.textContent=name(row.country)+' · '+row.count.toLocaleString();regions.append(span)}
}
new MutationObserver(render).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});render();
fetch('content/world-countries.geojson').then(r=>{if(!r.ok)throw Error();return r.json()}).then(d=>{geo=d;render()}).catch(()=>{host.textContent=zh()?'地图暂时无法加载':'Map temporarily unavailable'});
fetch('content/visitor-config.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json()}).then(async config=>{
 if(!config.endpoint){state='unconfigured';render();return;}
 const endpoint=config.endpoint.replace(/\/$/,'');if(!endpoint.startsWith('https://'))throw Error('HTTPS required');
 const response=await fetch(endpoint+'/visit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:crypto.randomUUID()}),signal:AbortSignal.timeout(12000)});if(!response.ok)throw Error();
 const value=await response.json();if(!Number.isSafeInteger(value.total)||value.total<0||!Array.isArray(value.countries)||value.countries.some(r=>!Number.isSafeInteger(r.count)||r.count<0||!/^[A-Z]{2}$/.test(r.country)))throw Error('Invalid statistics');stats=value;state='ready';render();
}).catch(()=>{state='error';render()});
})();
