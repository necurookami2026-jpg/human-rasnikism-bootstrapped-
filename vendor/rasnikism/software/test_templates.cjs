const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),context={Uint8Array,Uint16Array,DataView};vm.createContext(context);for(const file of ['jerry-pop.js','templates.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
const templates=context.JerryPopTemplates,api=context.JerryPop,expected={greeting:'A',echo:'A',choice:'1',latch:'A'};
for(const template of templates.templates){const copy=templates.instantiate(template.id),m=new api.Machine(api.assemble(copy.source),copy.input,new api.PortBus(copy.drivers));assert.equal(m.run(),'halted');assert.equal(Buffer.from(m.output).toString(),expected[copy.id]);copy.input.push(99);copy.drivers.push('eventlog');assert.notEqual(copy.input.length,template.input.length);assert.notEqual(copy.drivers.length,template.drivers.length);}
assert.throws(()=>templates.instantiate('unknown'));
const choice=templates.instantiate('choice'),zero=new api.Machine(api.assemble(choice.source),[0]);zero.run();assert.equal(Buffer.from(zero.output).toString(),'0');
console.log('Template checks passed: four executable programs, both choice branches, isolated copies, and unknown identifiers.');
