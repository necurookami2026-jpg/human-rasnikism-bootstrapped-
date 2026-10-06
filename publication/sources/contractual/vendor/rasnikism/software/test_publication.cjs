const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.join(__dirname,'..'),context={TextEncoder,TextDecoder,atob,crypto:crypto.webcrypto};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'publication.js'),'utf8'),context);
async function checks(){
    const api=context.OstarPublication;
    for(const name of ['makkakah','aantonymmakkakah','jurisdiction']){
        const script=fs.readFileSync(path.join(root,'encoded','ostar-'+name+'.io'),'utf8'),decoded=await api.decode(script);assert.equal(decoded.edition.name,name);assert(decoded.records.length>50);
        for(const record of decoded.records){const bytes=fs.readFileSync(path.join(root,record.path));assert.equal(record.text,bytes.toString('utf8'));assert.equal(record.sha256,crypto.createHash('sha256').update(bytes).digest('hex'));}
        assert(decoded.records.some(r=>r.path==='LICENSE'));assert(decoded.records.some(r=>r.path==='software/kerot.py'));assert(decoded.records.some(r=>r.path==='IO_PUBLICATION.md'));
    }
    const original=fs.readFileSync(path.join(root,'encoded/ostar-makkakah.io'),'utf8'),lines=original.trimEnd().split('\n');
    await assert.rejects(api.decode(original.replace('OSTAR_IO 1','OSTAR_IO 2')));
    await assert.rejects(api.decode(original.replace('END\n','EXEC\n')));
    const mutated=lines.slice(),r=JSON.parse(mutated[2].slice(4));r.sha256='0'.repeat(64);mutated[2]='PUT '+JSON.stringify(r);await assert.rejects(api.decode(mutated.join('\n')));
    r.path='../outside';mutated[2]='PUT '+JSON.stringify(r);await assert.rejects(api.decode(mutated.join('\n')));
    const duplicate=lines.slice();duplicate.splice(3,0,duplicate[2]);await assert.rejects(api.decode(duplicate.join('\n')));
    const before=fs.readFileSync(path.join(root,'publication-data.js'),'utf8');const built=cp.spawnSync('python3',[path.join(root,'software/build_io_publication.py')]);assert.equal(built.status,0,built.stderr.toString());assert.equal(fs.readFileSync(path.join(root,'publication-data.js'),'utf8'),before);
    for(const name of fs.readdirSync(root).filter(n=>n.endsWith('.html'))){const html=fs.readFileSync(path.join(root,name),'utf8');for(const match of html.matchAll(/href="([^"]+)"/g))assert(!new URL(match[1].replaceAll('&amp;','&'),'http://local/').pathname.endsWith('.md'),name);}
    function element(){return {value:'',children:[],textContent:'',disabled:true,events:{},files:[],replaceChildren(){this.children=[];this.value=''},append(node){this.children.push(node);if(this.children.length===1)this.value=node.value},addEventListener(k,f){this.events[k]=f}};}
    const els=Object.fromEntries(['records','filter','content','record-name','record','bundle','status','import'].map(id=>[id,element()]));
    context.URLSearchParams=URLSearchParams;context.window={location:{search:'?edition=jurisdiction&document=LICENSE'}};context.document={getElementById:id=>els[id],createElement:element};context.OstarEncodedEditions={};
    for(const name of ['makkakah','aantonymmakkakah','jurisdiction'])context.OstarEncodedEditions[name]=fs.readFileSync(path.join(root,'encoded','ostar-'+name+'.io'),'utf8');
    vm.runInContext(fs.readFileSync(path.join(root,'publication-ui.js'),'utf8'),context);await vm.runInContext('load(OstarEncodedEditions.jurisdiction)',context);
    assert.equal(els['record-name'].textContent,'LICENSE');assert.equal(els.content.textContent,fs.readFileSync(path.join(root,'LICENSE'),'utf8'));assert(els.status.textContent.includes('UNREVIEWED'));
    els.filter.value='not-a-record';els.filter.events.input();assert.equal(els.record.disabled,true);els.filter.value='';els.filter.events.input();assert.equal(els.record.disabled,false);
    const prior=els.content.textContent;await vm.runInContext('load("invalid")',context);assert.equal(els.content.textContent,prior);assert(els.status.textContent.includes('failed'));
    console.log('Encoded publication checks passed: all editions, exact source bytes, integrity, rejected scripts, reproducible builds, document routing, filtering, and failed-load preservation.');
}
checks().catch(e=>{console.error(e);process.exitCode=1;});
