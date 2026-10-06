const assert=require('node:assert/strict');
require('../madrigal_lab/web/iobots/catalogue.js');require('../madrigal_lab/web/iobots/search.js');require('../madrigal_lab/web/iobots/legacy-io.js');require('../madrigal_lab/web/iobots/responses.js');
const respond=globalThis.RasnikiResponses.respond;
const ok=respond('math gcd 42 30');assert.equal(ok.status,'completed');assert.equal(ok.result,'6');assert.equal(ok.sections.length,7);
for(const term of ['this','ahow','hot','awho','tho','awhat','that','awhen','then','awhere','there','awhy','thy'])assert.equal(respond(term).status,'completed',term);
for(const command of ['math divide 1 0','math add nope 2','bitflip 0 9','show missing']){const r=respond(command);assert.equal(r.status,'unable');assert.equal(r.code,'operation-rejected');assert(r.reason.length>40);assert.equal(r.result,'');assert(r.paperwork.includes('## awhy / thy'));}
assert.equal(respond('send a message').code,'unsupported-command');assert.equal(respond('').status,'waiting');assert.equal(respond(null).code,'invalid-input');
let called=false;const original=globalThis.RasnikiIO.command;globalThis.RasnikiIO.command=()=>{called=true;throw Error('unexpected');};const long=respond('x'.repeat(2001));assert.equal(called,false);assert.equal(long.code,'command-limit');assert.equal(long.request.length,2000);assert(long.request_truncated);globalThis.RasnikiIO.command=original;
assert.equal(respond('find no-such-zzzz-term').status,'no-match');assert(respond('runes <script>no</script>').paperwork.includes('## Literal result'));
console.log('IObot response checks passed: aliases, exact results, inability, bounds and paperwork.');
// UI contract: automatic response, cancellation and stale evidence prevention.
const fs=require('node:fs'),vm=require('node:vm');
const nodes=Object.fromEntries(['command','automatic','paperwork','status','respond','text-export','json-export','print'].map(id=>[id,{value:id==='command'?'help':'',checked:true,textContent:'',listeners:{},addEventListener(event,fn){this.listeners[event]=fn;}}]));
let pending=null,reported=[];
const context={document:{getElementById:id=>nodes[id]},globalThis:{RasnikiResponses:{respond:input=>{reported.push(input);return respond(input);}}},setTimeout:fn=>{pending=fn;return 1;},clearTimeout:()=>{pending=null;},window:{print(){}},URL:{},Blob:class{}};
vm.runInNewContext(fs.readFileSync(require.resolve('../madrigal_lab/web/iobots/ui.js'),'utf8'),context);
assert.equal(reported.at(-1),'help');nodes.command.value='math gcd 42 30';nodes.command.listeners.input();assert.equal(nodes.paperwork.textContent,'');assert(pending);pending();assert(nodes.paperwork.textContent.includes('\n\n6\n'));
nodes.command.value='math divide 1 0';nodes.command.listeners.input();nodes.automatic.checked=false;nodes.automatic.listeners.change();assert.equal(pending,null);nodes.respond.listeners.click();assert(nodes.paperwork.textContent.includes('Division by zero'));
nodes.command.value='math divide 7 2';nodes.command.listeners.input();assert.equal(pending,null);nodes.command.listeners.keydown({key:'Enter'});assert(nodes.paperwork.textContent.includes('3 remainder 1'));
console.log('IObot automatic UI checks passed.');
