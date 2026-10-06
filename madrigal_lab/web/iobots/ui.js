'use strict';
const node=id=>document.getElementById(id);let latest=null,timer=null;
function respond(){clearTimeout(timer);latest=globalThis.RasnikiResponses.respond(node('command').value);node('paperwork').textContent=latest.paperwork;node('status').textContent='Response status: '+latest.status;}
node('command').addEventListener('input',()=>{clearTimeout(timer);latest=null;node('paperwork').textContent='';node('status').textContent='Input changed; previous evidence discarded.';if(node('automatic').checked)timer=setTimeout(respond,350);});
node('automatic').addEventListener('change',()=>{clearTimeout(timer);if(node('automatic').checked)respond();});
node('command').addEventListener('keydown',e=>{if(e.key==='Enter')respond();});node('respond').addEventListener('click',respond);
function download(kind){if(!latest)respond();const url=URL.createObjectURL(new Blob([kind==='json'?JSON.stringify(latest,null,2):latest.paperwork],{type:kind==='json'?'application/json':'text/plain;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download='iobot-response.'+(kind==='json'?'json':'md');link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
node('text-export').addEventListener('click',()=>download('text'));node('json-export').addEventListener('click',()=>download('json'));node('print').addEventListener('click',()=>{if(!latest)respond();window.print();});respond();
