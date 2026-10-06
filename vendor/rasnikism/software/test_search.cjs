const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),context={};vm.createContext(context);
for(const file of ['catalogue.js','search.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
const api=context.RasnikiSearch,entries=context.RasnikiCatalog.entries;
assert.equal(api.normalize(' ＫＥＲＯＴ '),'kerot');
assert.equal(api.distance('solicitr','solicitor'),1);
assert.equal(api.find(entries,' Solicitor ','exact')[0].id,'solicitor');
assert.equal(api.find(entries,'solicitr','fuzzy')[0].id,'solicitor');
assert.equal(api.find(entries,'primitive kerot','all').some(e=>e.id==='kerot'),true);
assert.equal(api.find(entries,'xyz-not-a-category','exact').length,0);
assert.equal(api.find(entries,'').length,entries.length);
assert.throws(()=>api.find(entries,'x'.repeat(201)));
assert.throws(()=>api.find(entries,'','unknown'));
assert.equal(api.calculate('9007199254740993','1','add'),'9007199254740994');
assert.equal(api.calculate('7','12','subtract'),'-5');
assert.equal(api.calculate('-3','7','multiply'),'-21');
assert.equal(api.calculate('-7','3','divide'),'-2 remainder -1');
assert.equal(api.calculate('-42','30','gcd'),'6');
assert.equal(api.calculate('0','0','gcd'),'0');
for(const args of [['1','0','divide'],['1.1','2','add'],['1','2','eval'],['1'.repeat(1001),'2','add']])assert.throws(()=>api.calculate(...args));

function element(){return {children:[],events:{},value:'',textContent:'',append(...a){this.children.push(...a)},replaceChildren(){this.children=[]},addEventListener(k,f){this.events[k]=f}};}
const els=Object.fromEntries(['query','mode','results','status','previous','next','calculate','a','b','op','answer'].map(id=>[id,element()]));els.mode.value='all';
context.document={getElementById:id=>els[id],createElement:element};
vm.runInContext(fs.readFileSync(path.join(root,'search-ui.js'),'utf8'),context);
assert.equal(els.results.children.length,6);els.query.value='solicitr';els.mode.value='fuzzy';els.query.events.input();assert.equal(els.results.children[0].children[0].textContent,'Solicitor');assert.equal(els.results.children[0].children[3].href,'catalogue.html#module=solicitor');
els.query.value='no-such-category';els.mode.value='exact';els.query.events.input();assert.equal(els.results.children.length,0);assert.equal(els.next.disabled,true);
els.a.value='7';els.b.value='0';els.op.value='divide';els.calculate.events.click();assert.equal(els.answer.textContent,'Division by zero');
console.log('Search checks passed: normalization, exact/fuzzy/all-term matching, ranking, limits, arithmetic, UI results, and summon links.');
