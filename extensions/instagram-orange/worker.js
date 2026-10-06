importScripts('core.js');
let job=null;
const grants=new Set();
const popup=sender=>sender.id===chrome.runtime.id && sender.url===chrome.runtime.getURL('popup.html');
const content=sender=>sender.id===chrome.runtime.id && sender.tab && OrangeCore.instagram(sender.tab.url);
async function cancel(){if(job){job.cancelled=true; for(const id of job.active)try{await chrome.downloads.cancel(id);}catch{} }}
async function run(current){
 for(let i=0;i<current.items.length;i++){
  if(current.cancelled)break;
  try{const id=await chrome.downloads.download({url:current.items[i].url,filename:OrangeCore.filename(current.items[i],i),conflictAction:'uniquify',saveAs:false});
   current.active.add(id);current.accepted++;
   if(current.cancelled)try{await chrome.downloads.cancel(id);}catch{}
   // A browser-managed download survives service-worker shutdown.
  }catch{current.failed++;}
  await new Promise(r=>setTimeout(r,400));
 }
 current.finished=true;
}
chrome.downloads.onChanged.addListener(delta=>{if(!job?.active.has(delta.id))return;if(delta.state?.current==='complete'){job.complete++;job.active.delete(delta.id);}if(delta.state?.current==='interrupted'){job.failed++;job.active.delete(delta.id);}});
chrome.runtime.onMessage.addListener((message,sender,reply)=>{
 (async()=>{
  if(popup(sender)){
   if(message.type==='grant'){const tab=await chrome.tabs.get(message.tabId);if(!OrangeCore.instagram(tab.url))throw Error('Open Instagram first.');if(message.allowed===true)grants.add(tab.id);else{grants.delete(tab.id);await cancel();}return {ok:true};}
   if(message.type==='status')return job?{accepted:job.accepted,complete:job.complete,failed:job.failed,total:job.items.length,finished:job.finished,cancelled:job.cancelled}:{total:0};
   if(message.type==='cancel'){await cancel();return {ok:true};}
  }
  if(content(sender)&&message.type==='download'){
   if(!grants.has(sender.tab.id))throw Error('Open the extension and confirm follower access and permission first.');
   if(job && (!job.finished || job.active.size))throw Error('Wait for the current downloads or cancel them.');
   const items=OrangeCore.unique(Array.isArray(message.items)?message.items:[]);
   if(!items.length)throw Error('No supported loaded media found. Open the post, carousel item, reel or story first.');
   job={items,accepted:0,complete:0,failed:0,active:new Set(),finished:false,cancelled:false};void run(job);return {ok:true,total:items.length};
  }
  throw Error('Request not authorized.');
 })().then(reply).catch(error=>reply({error:error.message}));return true;
});
chrome.tabs.onRemoved.addListener(id=>grants.delete(id));
