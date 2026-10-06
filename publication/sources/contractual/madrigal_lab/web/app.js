'use strict';
const el=id=>document.getElementById(id), value=id=>el(id).value, number=id=>Number(value(id));
let token='',catalogue={};
const show=result=>{el('result').textContent=JSON.stringify(result,null,2);};
async function action(name,args={}){try{const response=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json','X-Lab-Token':token},body:JSON.stringify({action:name,args})});const data=await response.json();show(data);if(!response.ok)throw new Error(data.error);return data.result;}catch(error){show({error:error.message});return null;}}
const bind=(id,args,after)=>el(id).addEventListener('click',async()=>{const result=await action(id,args());if(result&&after)after(result);});
for(const button of document.querySelectorAll('[data-tab]'))button.addEventListener('click',()=>{for(const section of document.querySelectorAll('.workspace'))section.hidden=section.id!==button.dataset.tab;for(const b of document.querySelectorAll('[data-tab]'))b.classList.toggle('active',b===button);});
document.querySelector('[data-tab]').classList.add('active');
bind('run',()=>({source:value('source')}));
bind('assemble',()=>({source:value('source')}),r=>{el('bytecode').value=r.hex;});
bind('format',()=>({source:value('source')}),r=>{el('source').value=r.source;});
bind('disassemble',()=>({hex:value('bytecode')}),r=>{el('source').value=r.source;});
bind('compile',()=>({source:value('script')}),r=>{el('source').value=r.source;});
bind('boot',()=>({source:value('source'),mode:value('boot-mode')}));
bind('job',()=>({source:value('source')}));bind('tick',()=>({}));
bind('quilt',()=>({mode:value('mode'),values:value('bits').split(',').map(s=>s.trim()).filter(s=>s!=='').map(Number)}));
bind('write',()=>({path:value('file-path'),text:value('file-text')}));
bind('read',()=>({path:value('file-path')}),r=>{el('file-text').value=r.text;});
bind('scan',()=>({}));bind('baseline',()=>({trusted:el('trusted').checked}));bind('check',()=>({}));
bind('practice',()=>({purpose:value('purpose'),priority:value('priority')}));
bind('transition',()=>({id:number('practice-id'),state:value('state'),reason:value('reason')}));
bind('rule',()=>({title:value('rule-title'),content:value('rule-content')}));bind('adopt-rule',()=>({id:number('rule-id'),reviewer:value('reviewer')}));
bind('account',()=>({name:value('account-name')}));bind('mint',()=>({account:value('mint-account'),amount:number('mint-amount')}));
bind('transfer',()=>({from:value('from'),to:value('to'),amount:number('amount')}));bind('economy',()=>({}));
bind('domain',()=>({host:value('host'),document:value('document')}));bind('intranet-bot',()=>({host:value('host')}));bind('internet-bot',()=>({url:value('url')}));bind('game',()=>({guess:number('guess')}));
async function refresh(){try{const response=await fetch('/api/status');if(!response.ok)throw new Error('Status request failed');show(await response.json());}catch(error){show({error:error.message});}}
el('refresh').addEventListener('click',refresh);el('list').addEventListener('click',refresh);
function card(parent,title,description,footer){const div=document.createElement('article');div.className='card';const h=document.createElement('h4');h.textContent=title;const p=document.createElement('p');p.textContent=description;const small=document.createElement('small');small.textContent=footer;div.append(h,p,small);parent.append(div);}
async function start(){try{const response=await fetch('/api/session');if(!response.ok)throw new Error('Local session unavailable');token=(await response.json()).token;catalogue=await (await fetch('/api/catalogue')).json();for(const item of catalogue.glossary){card(el('glossary'),item.term,item.meaning||'Awaiting author definition.',item.status);if(item.status==='implemented-finite-mode'){const option=document.createElement('option');option.value=item.term;option.textContent=item.term;el('mode').append(option);}}for(const item of catalogue.curriculum)card(el('curriculum'),item.cycle,item.exercise,item.evidence);el('mode').addEventListener('change',()=>{const item=catalogue.glossary.find(g=>g.term===value('mode'));el('mode-fields').textContent=item.fields.join(', ');el('bits').value=item.fields.map(()=>1).join(',');});el('mode').dispatchEvent(new Event('change'));el('connection').textContent='Local session ready';await refresh();}catch(error){el('connection').textContent='Unavailable';show({error:error.message});}}
start();
