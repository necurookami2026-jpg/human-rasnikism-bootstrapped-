const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),context={};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'archangel.js'),'utf8'),context);
const api=context.RasnikiArchangel,store=api.createStore();
assert.equal(api.systems.length,22);
assert.equal(api.profile({name:' Person ',bio:'Writer',boundary:'Voluntary'}).name,'Person');
assert.throws(()=>api.account({service:'',alias:'x',note:''}));
api.add(store,'accounts',{service:'Example',alias:'Writer',note:'Authorized metadata'});
assert.equal(store.accounts.length,1);
assert.throws(()=>api.add(store,'publications',{title:'Work',status:'published',reference:'',rights:'',review:''}));
api.add(store,'publications',{title:'Work',status:'published',reference:'User supplied reference',rights:'Needs review',review:'Unverified'});
assert.throws(()=>api.publication({title:'Work',status:'certified',reference:'x',rights:'',review:''}));
assert.throws(()=>api.profile({name:'x'.repeat(201),bio:'',boundary:''}));
const exported=JSON.parse(api.exportRecords(store));assert.equal(exported.publications[0].status,'published');assert(!Object.hasOwn(exported,'support'));
api.remove(store,'accounts',0);assert.equal(store.accounts.length,0);assert.throws(()=>api.remove(store,'accounts',0));
for(let i=0;i<100;i++)api.add(store,'accounts',{service:'s',alias:'a',note:''});assert.throws(()=>api.add(store,'accounts',{service:'s',alias:'a',note:''}));

function element(){return {value:'',textContent:'',hidden:true,children:[],events:{},attrs:{},addEventListener(k,f){this.events[k]=f},append(...nodes){this.children.push(...nodes)},replaceChildren(){this.children=[]},setAttribute(k,v){this.attrs[k]=v},focus(){this.focused=true}};}
const ids=['status','accounts','publications','save-profile','name','bio','boundary','profile-status','add-account','service','alias','account-note','add-publication','title','state','reference','rights','review','export','clear','support','panic','panic-button','close-panic','clear-support','systems'];
const els=Object.fromEntries(ids.map(id=>[id,element()]));els.state.value='draft';context.document={getElementById:id=>els[id],createElement:element};
vm.runInContext(fs.readFileSync(path.join(root,'archangel-ui.js'),'utf8'),context);
assert.equal(els.systems.children.length,22);els.service.value='Service';els.alias.value='Alias';els['add-account'].events.click();assert.equal(els.accounts.children.length,1);assert.equal(els.service.value,'');
els.accounts.children[0].children[1].events.click();assert.equal(els.accounts.children.length,0);
els.title.value='Work';els.state.value='published';els['add-publication'].events.click();assert.equal(els.publications.children.length,0);assert(els.status.textContent.includes('reference'));
els.reference.value='Unverified link';els['add-publication'].events.click();assert.equal(els.publications.children.length,1);
els['panic-button'].events.click();assert.equal(els.panic.hidden,false);assert.equal(els['panic-button'].attrs['aria-expanded'],'true');assert.equal(els.panic.focused,true);
els['close-panic'].events.click();assert.equal(els.panic.hidden,true);els.support.value='Private note';els.clear.events.click();assert.equal(els.support.value,'');assert.equal(els.publications.children.length,0);
console.log('Archangel checks passed: definitions, validation, record limits, export, deletion, publication assertions, panel controls, and session clearing.');
