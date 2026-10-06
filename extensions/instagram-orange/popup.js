const status=document.querySelector('#status');let tab;
async function message(value){const r=await chrome.runtime.sendMessage(value);if(r.error)throw Error(r.error);return r;}
async function save(bulk){try{if(!document.querySelector('#permission').checked)throw Error('Confirm follower access and permission first.');await message({type:'grant',tabId:tab.id,allowed:true});await chrome.tabs.sendMessage(tab.id,{type:'save-visible',bulk});status.textContent='Requested loaded media. See the orange page panel for results.';}catch(e){status.textContent=e.message;}}
chrome.tabs.query({active:true,currentWindow:true}).then(tabs=>{tab=tabs[0];});
document.querySelector('#permission').addEventListener('change',async e=>{if(!e.target.checked&&tab)await message({type:'grant',tabId:tab.id,allowed:false});});
document.querySelector('#single').onclick=()=>save(false);document.querySelector('#bulk').onclick=()=>save(true);document.querySelector('#cancel').onclick=async()=>{await message({type:'cancel'});status.textContent='Cancellation requested.';};
setInterval(async()=>{try{const s=await message({type:'status'});if(s.total)status.textContent=`${s.complete} completed; ${s.accepted} accepted; ${s.failed} failed / ${s.total} items${s.cancelled?' — cancelled':''}.`;}catch{}},1000);
