const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),cp=require('node:child_process');
const root=path.join(__dirname,'..'),script=fs.readFileSync(path.join(root,'ostar.js'),'utf8');
function link(href,edition){return {attrs:{href,...(edition?{'data-ostar-edition':edition}:{})},getAttribute(k){return this.attrs[k]??null},setAttribute(k,v){this.attrs[k]=v}};}
for(const choice of ['makkakah','aantonymmakkakah','jurisdiction','unknown']){
    const name={},guidance={},links=[link('catalogue.html#module=kerot'),link('?edition=jurisdiction','jurisdiction'),link('https://example.com/tool.html'),link('OSTAR.md'),link('#content')];
    const context={URL,URLSearchParams,window:{location:{search:'?edition='+choice,href:'http://localhost/rasnikism/index.html?edition='+choice,origin:'http://localhost'}},document:{querySelectorAll(selector){return selector==='[data-ostar-name]'?[name]:selector==='[data-ostar-guidance]'?[guidance]:links;}}};
    vm.createContext(context);vm.runInContext(script,context);
    const expected=choice==='unknown'?'makkakah':choice;
    assert.equal(new URL(links[0].attrs.href).searchParams.get('edition'),expected);assert.equal(new URL(links[0].attrs.href).hash,'#module=kerot');
    assert.equal(new URL(links[1].attrs.href).searchParams.get('edition'),'jurisdiction');assert.equal(links[2].attrs.href,'https://example.com/tool.html');assert.equal(links[3].attrs.href,'OSTAR.md');assert.equal(links[4].attrs.href,'#content');
    if(choice==='jurisdiction'){assert(name.textContent.includes('UNREVIEWED'));assert(guidance.textContent.includes('does not certify'));}
}
const names=['OSTAR-MAKKAKAH.md','OSTAR-AANTONYMMAKKAKAH.md','OSTAR-JURISDICTION-REVIEW.md'],before=names.map(name=>fs.readFileSync(path.join(root,'editions',name),'utf8'));
const run=cp.spawnSync('python3',[path.join(root,'software/build_editions.py')]);assert.equal(run.status,0,run.stderr.toString());
const sources=fs.readdirSync(root).filter(name=>name.endsWith('.md'));
for(let i=0;i<names.length;i++){const text=fs.readFileSync(path.join(root,'editions',names[i]),'utf8');assert.equal(text,before[i]);for(const source of sources)assert(text.includes('## Source: '+source));assert(text.includes('../LICENSE'));}
for(const name of fs.readdirSync(root).filter(name=>name.endsWith('.html'))){const html=fs.readFileSync(path.join(root,name),'utf8');assert.equal((html.match(/class="ostar-shell"/g)||[]).length,1);assert.equal((html.match(/src="ostar.js"/g)||[]).length,1);}
console.log('Ostar checks passed: all edition contexts, URL propagation, fragment preservation, legal-status wording, full source coverage, repeatable compilation, and one shared shell per page.');
