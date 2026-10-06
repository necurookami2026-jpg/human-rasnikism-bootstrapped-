(function(root){
'use strict';
function validate(source,input,drivers){
if(typeof source!=='string'||source.length>1000000)throw Error('Source must contain at most one million characters');
if(!Array.isArray(input)||input.length>100000||input.some(n=>!Number.isInteger(n)||n<0||n>255))throw Error('Input must contain at most 100000 bytes');
if(!Array.isArray(drivers)||drivers.length>4||new Set(drivers).size!==drivers.length||drivers.some(name=>!Object.hasOwn(root.JerryPop.driverIds,name)))throw Error('Invalid driver selection');
}
class Session{
constructor(source,input=[],drivers=[]){this.revisions=[];this.nextVersion=1;this.machine=null;this.activeVersion=null;this.commit(source,input,drivers);}
commit(source,input,drivers){if(!Number.isSafeInteger(this.nextVersion)||this.nextVersion>=Number.MAX_SAFE_INTEGER)throw Error('Revision number limit reached');validate(source,input,drivers);const api=root.JerryPop,binary=api.assemble(source),machine=new api.Machine(binary,input,new api.PortBus(drivers));const revision={version:this.nextVersion,source,input:Array.from(input),drivers:[...drivers]};this.nextVersion++;this.revisions.push(revision);while(this.revisions.length>10||this.revisions.reduce((n,r)=>n+r.source.length,0)>2000000)this.revisions.shift();this.machine=machine;this.binary=binary;this.activeVersion=revision.version;return machine;}
current(){return this.revisions.find(r=>r.version===this.activeVersion);}
reinterpret(source){const previous=this.current();if(!previous)throw Error('No active revision');return this.commit(source,previous.input,previous.drivers);}
revise(source,input,drivers){return this.commit(source,input,drivers);}
static import(text){
if(typeof text!=='string'||text.length>15000000)throw Error('Revision JSON exceeds import limit');
const data=JSON.parse(text);
if(!data||data.format!=='jerry-pop-reinterpretation'||data.version!==1||!Array.isArray(data.revisions)||data.revisions.length<1||data.revisions.length>10)throw Error('Unsupported revision archive');
let previous=0,total=0;const revisions=[];
for(const r of data.revisions){
if(!r||!Number.isSafeInteger(r.version)||r.version<=previous||r.version>=Number.MAX_SAFE_INTEGER)throw Error('Revision numbers must increase');
validate(r.source,r.input,r.drivers);total+=r.source.length;if(total>2000000)throw Error('Revision source limit exceeded');
const api=root.JerryPop;new api.Machine(api.assemble(r.source),r.input,new api.PortBus(r.drivers));
revisions.push({version:r.version,source:r.source,input:[...r.input],drivers:[...r.drivers]});previous=r.version;
}
if(!Number.isSafeInteger(data.activeRevision)||!revisions.some(r=>r.version===data.activeRevision))throw Error('Active revision is not retained');
const session=Object.create(Session.prototype);session.revisions=revisions;session.nextVersion=previous+1;session.replay(data.activeRevision);return session;
}
replay(version){const revision=this.revisions.find(r=>r.version===Number(version));if(!revision)throw Error('Revision is not retained');const api=root.JerryPop,binary=api.assemble(revision.source),machine=new api.Machine(binary,revision.input,new api.PortBus(revision.drivers));this.machine=machine;this.binary=binary;this.activeVersion=revision.version;return machine;}
export(){return JSON.stringify({format:'jerry-pop-reinterpretation',version:1,activeRevision:this.activeVersion,notice:'Source/input revisions, not live memory snapshots. Replay starts a fresh machine.',revisions:this.revisions.map(r=>({version:r.version,source:r.source,input:[...r.input],drivers:[...r.drivers]}))},null,2);}
}
root.JerryPopReinterpretation={Session};
})(globalThis);
