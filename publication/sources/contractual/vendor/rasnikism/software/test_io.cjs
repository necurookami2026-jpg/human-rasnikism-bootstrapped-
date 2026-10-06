const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),context={TextDecoder};vm.createContext(context);
for(const file of ['catalogue.js','search.js','io.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
const api=context.RasnikiIO;
assert.equal(api.runes.length,26);assert.equal(new Set(api.runes).size,26);
assert.equal(api.decode(api.encode('ABCDEFGHIJKLMNOPQRSTUVWXYZ')),api.letters);
assert.equal(api.decode(api.encode('Return, 123!')), 'return, 123!');
assert.equal(api.encode('K 😀'), 'K 😀');
const record=api.unpack(api.pack('Hello 😀','english'));assert.equal(record.text,'Hello 😀');assert.equal(record.edition,'english');
for(const raw of ['{','null','[]','{}',JSON.stringify({format:'rasniki-io',version:2,edition:'english',text:'x'}),JSON.stringify({format:'rasniki-io',version:1,edition:'english',text:42})])assert.throws(()=>api.unpack(raw));
assert.throws(()=>api.encode('x'.repeat(100001)));assert.throws(()=>api.pack('x','unknown'));
assert(api.command('help').includes('Commands:'));assert(api.command('find solicitor').includes('solicitor'));
assert(api.command('show kerot').includes('Implemented'));assert.equal(api.command('math gcd 42 30'),'6');assert.equal(api.command('bitflip 0 7'),'128');
assert.equal(api.command('english '+api.command('runes RETURN')),'return');
for(const raw of ['eval process.exit()','show missing','math add 1','math divide 1 0','bitflip 256 0','x'.repeat(2001)])assert.throws(()=>api.command(raw));
function element(){return {value:'',files:[],textContent:'',events:{},children:[],addEventListener(k,f){this.events[k]=f},append(x){this.children.push(x)}};}
const ids=['text','edition','file','text-export','json-export','clear','io-status','encode','decode','alphabet','command','bot-output','run','copy-output'];
const els=Object.fromEntries(ids.map(id=>[id,element()]));els.edition.value='english';els.command.value='help';
context.document={getElementById:id=>els[id],createElement:element};vm.runInContext(fs.readFileSync(path.join(root,'io-ui.js'),'utf8'),context);
assert.equal(els.alphabet.children.length,26);els.text.value='CARE';els.encode.events.click();assert.equal(els.edition.value,'iau');els.decode.events.click();assert.equal(els.text.value,'care');
els.command.value='math add 5 7';els.run.events.click();els['copy-output'].events.click();assert.equal(els.text.value,'12');
els.command.value='bad';els.command.events.input();els['copy-output'].events.click();assert(els['io-status'].textContent.includes('successful command'));
async function imports(){
    const bytes=text=>new TextEncoder().encode(text).buffer;
    els.file.files=[{name:'draft.json',size:100,arrayBuffer:async()=>bytes(api.pack('Imported','iau'))}];await els.file.events.change();assert.equal(els.text.value,'Imported');assert.equal(els.edition.value,'iau');
    els.file.files=[{name:'bad.json',size:10,arrayBuffer:async()=>bytes('{')}];await els.file.events.change();assert.equal(els.text.value,'Imported');assert(els['io-status'].textContent.includes('failed'));
    els.file.files=[{name:'bad.txt',size:1,arrayBuffer:async()=>new Uint8Array([255]).buffer}];await els.file.events.change();assert(els['io-status'].textContent.includes('failed'));
    let resolve;els.file.files=[{name:'slow.txt',size:4,arrayBuffer:()=>new Promise(r=>resolve=r)}];const pending=els.file.events.change();els.clear.events.click();resolve(bytes('late'));await pending;assert.equal(els.text.value,'');
    console.log('I/O checks passed: rune mapping, records, commands, bounds, UI conversion, UTF-8 import, failed import preservation, and stale import cancellation.');
}
imports().catch(error=>{console.error(error);process.exitCode=1;});
