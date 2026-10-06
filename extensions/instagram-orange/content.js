(()=>{
 let panel;
 const loaded=container=>OrangeCore.unique([...container.querySelectorAll('video,img')].filter(el=>{
  const box=el.getBoundingClientRect();return box.width>=160 && box.height>=160 && !el.closest('[data-orange-saver]');
 }).map(el=>({url:el.currentSrc||el.src,kind:el.tagName==='VIDEO'?'video':'image'})));
 function notify(text){panel.querySelector('output').textContent=text;}
 async function save(items){try{const result=await chrome.runtime.sendMessage({type:'download',items});notify(result.error||`Queued ${result.total} loaded item(s).`);}catch{notify('Reopen the extension to restore permission.');}}
 function button(arrows,label,action){const b=document.createElement('button');b.type='button';b.textContent=arrows;b.title=label;b.setAttribute('aria-label',label);b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();action();});return b;}
 function mount(){
  if(!document.body)return;
  if(!panel?.isConnected){panel=document.createElement('aside');panel.dataset.orangeSaver='panel';panel.append(button('↓','Download first visible loaded media',()=>save(loaded(document).slice(0,1))),button('↓↓↓','Download all loaded media (maximum 200)',()=>save(loaded(document))));const out=document.createElement('output');out.textContent='Open saver to confirm permission. Loaded media only.';panel.append(out);document.body.append(panel);}
  for(const article of document.querySelectorAll('article')){
   if(article.querySelector('[data-orange-saver="single"]')||!loaded(article).length)continue;
   const b=button('↓','Download current loaded post media',()=>save(loaded(article).slice(0,1)));b.dataset.orangeSaver='single';article.append(b);
  }
 }
 let timer;const observer=new MutationObserver(records=>{if(records.every(r=>r.target.closest?.('[data-orange-saver]')))return;clearTimeout(timer);timer=setTimeout(mount,600);});observer.observe(document.documentElement,{subtree:true,childList:true});mount();
 chrome.runtime.onMessage.addListener((msg,sender,reply)=>{if(sender.id!==chrome.runtime.id)return;if(msg.type==='save-visible'){save(loaded(document).slice(0,msg.bulk?200:1));reply({ok:true});}});
})();
