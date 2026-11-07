(() => {
'use strict';
const host=document.getElementById('lung-frontier-list'),status=document.getElementById('lung-frontier-status');if(!host)return;
let data=null,failed=false;const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const currentMonth=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit'}).format(new Date()).replace(/(\d{2})\/(\d{4})/,'$2-$1');
function size(){const cards=[...host.children];host.classList.toggle('is-scrollable',cards.length>5);if(cards.length>5){const fifth=cards[4];host.style.maxHeight=(fifth.offsetTop-host.firstElementChild.offsetTop+fifth.offsetHeight+8)+'px';host.tabIndex=0;}else{host.style.maxHeight='';host.removeAttribute('tabindex');}}
function render(){const zh=document.documentElement.lang.startsWith('zh');host.setAttribute('aria-label',zh?'本月肺研究文献':'This month’s lung research');if(failed){status.textContent=zh?'文献暂时无法加载，请稍后重试。':'Literature is temporarily unavailable. Please try again later.';return;}if(!data)return;
const month=currentMonth();const items=data.month===month?data.items:[];const checked=new Date(data.checked_at).toLocaleDateString(zh?'zh-CN':'en-GB',{timeZone:'Asia/Shanghai'});
status.textContent=zh?month+' · '+items.length+' 篇 · 最近核对：'+checked:month+' · '+items.length+' articles · Checked: '+checked;
host.innerHTML=items.length?items.map(i=>'<article class="frontier-card"><div class="frontier-meta">'+esc(i.journal)+' · '+esc(i.date)+'</div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/'+encodeURIComponent(i.pmid)+'/" target="_blank" rel="noopener noreferrer">'+esc(i.title)+'</a></h3><p>'+esc(zh?i.summary_zh:i.summary_en)+'</p><a class="meta" href="https://pubmed.ncbi.nlm.nih.gov/'+encodeURIComponent(i.pmid)+'/" target="_blank" rel="noopener noreferrer">PubMed ↗</a></article>').join(''):'<p class="news-empty">'+(zh?'本月暂未有已核对、符合筛选条件的文献。':'No verified articles meeting the selection criteria are available this month.')+'</p>';requestAnimationFrame(size);}
new MutationObserver(render).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});new ResizeObserver(size).observe(host);window.addEventListener('resize',size);
fetch('content/lung-frontier.json?v='+new Date().toISOString().slice(0,10),{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(v=>{if(!Array.isArray(v.items))throw Error('Invalid data');data=v;render()}).catch(()=>{failed=true;render()});
})();
