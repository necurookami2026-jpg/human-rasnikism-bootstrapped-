const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),context={TextDecoder};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'game.js'),'utf8'),context);
const api=context.RasnikiGame,initial=api.fresh();let state=api.action(initial,'move','workroom');assert.equal(initial.room,'threshold');assert.equal(state.room,'workroom');
state=api.action(state,'quest');assert.equal(state.resources,5);assert.equal(state.quests.length,1);assert.throws(()=>api.action(state,'quest'));
state=api.action(state,'care');assert.equal(state.care,1);assert.equal(state.resources,4);state=api.action(state,'repair');assert.equal(state.repair,1);
let empty={...api.fresh(),resources:0};assert.throws(()=>api.action(empty,'care'));assert.throws(()=>api.action(empty,'repair'));empty=api.action(empty,'rest');assert.equal(empty.resources,1);
assert.equal(api.action(state,'mode','quiet').mode,'quiet');assert.throws(()=>api.action(state,'move','missing'));assert.throws(()=>api.action(state,'unknown'));
assert.equal(api.unpack(api.pack(state)).room,state.room);assert.throws(()=>api.unpack('{'));
for(const patch of [{version:2},{resources:-1},{care:1.5},{room:'missing'},{quests:['threshold','threshold']},{journal:['x'.repeat(501)]},{mode:'unsafe'}])assert.throws(()=>api.validate({...api.fresh(),...patch}));
assert.throws(()=>api.action({...api.fresh(),turns:1000000},'rest'));assert.equal(api.action({...api.fresh(),resources:1000000},'rest').resources,1000000);
let complete=api.fresh();for(const room of api.rooms){complete=api.action(complete,'move',room.id);complete=api.action(complete,'quest');}assert.equal(complete.quests.length,8);
for(let n=0;n<110;n++)complete=api.action(complete,'rest');assert.equal(complete.journal.length,100);

function element(){return {value:'',children:[],events:{},files:[],attrs:{},textContent:'',addEventListener(k,f){this.events[k]=f},append(x){this.children.push(x)},replaceChildren(){this.children=[]},setAttribute(k,v){this.attrs[k]=v}};}
const ids=['room-name','description','counters','completion','quest','care','repair','rest','journal','mode','map','status','save','load','new'];const els=Object.fromEntries(ids.map(id=>[id,element()]));let quiet=false;
context.document={getElementById:id=>els[id],createElement:element,body:{classList:{toggle(k,v){quiet=v}}}};
vm.runInContext(fs.readFileSync(path.join(root,'game-ui.js'),'utf8'),context);
assert.equal(els.map.children.length,8);els.quest.events.click();assert.equal(els.quest.disabled,true);assert(els.completion.textContent.startsWith('1 of 8'));
els.map.children[2].events.click();assert.equal(els['room-name'].textContent,'Makkakah workroom');assert.equal(els.quest.disabled,false);els.mode.value='quiet';els.mode.events.change();assert.equal(quiet,true);
els.new.events.click();assert(els.completion.textContent.startsWith('0 of 8'));assert.equal(quiet,false);
async function imports(){
    const bytes=text=>new TextEncoder().encode(text).buffer;
    els.load.files=[{size:100,name:'save.json',arrayBuffer:async()=>bytes(api.pack(state))}];await els.load.events.change();assert.equal(els['room-name'].textContent,'Makkakah workroom');
    els.load.files=[{size:1,name:'bad.json',arrayBuffer:async()=>bytes('{')}];await els.load.events.change();assert.equal(els['room-name'].textContent,'Makkakah workroom');assert(els.status.textContent.includes('failed'));
    let resolve;els.load.files=[{size:100,arrayBuffer:()=>new Promise(r=>resolve=r)}];const pending=els.load.events.change();els.new.events.click();resolve(bytes(api.pack(state)));await pending;assert.equal(els['room-name'].textContent,'Threshold');
    console.log('Game checks passed: mechanics, immutable actions, save validation, bounds, circuit completion, UI controls, failed load preservation, and stale load cancellation.');
}
imports().catch(e=>{console.error(e);process.exitCode=1;});
