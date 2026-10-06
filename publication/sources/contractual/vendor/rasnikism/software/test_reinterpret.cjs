const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),context={Uint8Array,Uint16Array,DataView};vm.createContext(context);for(const file of ['jerry-pop.js','reinterpret.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
const Session=context.JerryPopReinterpretation.Session,a='mark r0 65\nsignal r0 0 1\nsignal r0 2 1',b=a.replace('65','66');
const s=new Session(a,[12],['queue']);s.machine.run();assert.equal(s.machine.output[0],65);s.machine.ports.transfer(16,1,7,0);s.reinterpret(b);assert.equal(s.machine.steps,0);assert.equal(s.machine.ports.devices.get(16).queue.length,0);assert.equal(s.current().input[0],12);s.machine.run();assert.equal(s.machine.output[0],66);s.replay(1);s.machine.run();assert.equal(s.machine.output[0],65);
const valid=s.machine,count=s.revisions.length;assert.throws(()=>s.reinterpret('unknown'));assert.equal(s.machine,valid);assert.equal(s.revisions.length,count);assert.throws(()=>s.replay(999));
for(let i=0;i<15;i++)s.reinterpret(b);assert.equal(s.revisions.length,10);assert.throws(()=>s.replay(1));
const large=';'+ 'x'.repeat(700000)+'\n'+a;for(let i=0;i<3;i++)s.reinterpret(large);assert(s.revisions.reduce((n,r)=>n+r.source.length,0)<=2000000);assert(s.current());
const exported=JSON.parse(s.export());assert.equal(exported.format,'jerry-pop-reinterpretation');assert.equal(exported.activeRevision,s.activeVersion);assert.equal(exported.revisions.length,s.revisions.length);assert(!Object.hasOwn(exported,'memory'));
console.log('Reinterpretation checks passed: edited execution, captured inputs, fresh driver state, replay, failed-compile preservation, history limits, and source export.');

const restored=Session.import(s.export());assert.equal(restored.activeVersion,s.activeVersion);assert.equal(restored.machine.steps,0);restored.machine.run();assert.equal(restored.machine.output[0],65);restored.revise(a,[90],['latch']);assert.equal(restored.current().input[0],90);assert.equal(restored.current().drivers[0],'latch');assert(restored.current().version>exported.revisions.at(-1).version);
const archive=JSON.parse(new Session(a,[65],[]).export());
for(const mutate of [d=>d.version=2,d=>d.activeRevision=999,d=>d.revisions[0].input=[256],d=>d.revisions[0].input=[-1],d=>d.revisions[0].input=[1.5],d=>d.revisions[0].drivers=['unknown'],d=>d.revisions[0].drivers=['queue','queue'],d=>d.revisions[0].source='unknown',d=>d.revisions[0].source='x'.repeat(1000001),d=>d.revisions.push(d.revisions[0]),d=>d.revisions[0].version=Number.MAX_SAFE_INTEGER]){const bad=JSON.parse(JSON.stringify(archive));mutate(bad);assert.throws(()=>Session.import(JSON.stringify(bad)));}
assert.throws(()=>Session.import('null'));assert.throws(()=>Session.import('{'));assert.throws(()=>new Session(a,[NaN]));assert.throws(()=>new Session(a,[],['invalid']));
vm.runInContext(fs.readFileSync(path.join(root,'language/quilt-program.js'),'utf8'),context);
for(const mode of context.OstarQuiltProgram.manifest.modes){
for(let mask=0;mask<2**mode.payload.length;mask++){
const payload=mode.payload.map((_,i)=>(mask>>i)&1),input=[(mode.code>>2)&1,(mode.code>>1)&1,mode.code&1,...payload];
const session=new Session(context.OstarQuiltProgram.source,input,[]);assert.equal(session.machine.run(10000),'halted');const output=Buffer.from(session.machine.output).toString();
session.reinterpret('; revised source\n'+context.OstarQuiltProgram.source);assert.equal(session.machine.run(10000),'halted');assert.equal(Buffer.from(session.machine.output).toString(),output);
const imported=Session.import(session.export());assert.equal(imported.machine.steps,0);assert.equal(imported.machine.run(10000),'halted');assert.equal(Buffer.from(imported.machine.output).toString(),output);imported.replay(1);assert.equal(imported.machine.run(10000),'halted');assert.equal(Buffer.from(imported.machine.output).toString(),output);
}}
console.log('Archive checks passed: validation, fresh machines, changed inputs/drivers, and reinterpret/import/replay for every Boolean payload in all eight quilt modes.');
