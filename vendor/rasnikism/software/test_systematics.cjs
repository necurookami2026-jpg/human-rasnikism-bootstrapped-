const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),context={};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'systematics.js'),'utf8'),context);
const api=context.RasnikiSystematics,store=api.create();
const proposal=(members='A, B, C')=>api.propose(store,{system:'yorkie',title:'Care review',wording:'Revised care',reason:'Clearer boundaries',members});
let p=proposal();assert.equal(api.outcome(p).result,'pending');api.vote(p,'A','yes','Agreed');assert.equal(api.outcome(p).result,'pending');api.vote(p,'B','no');assert.equal(api.outcome(p).result,'tie');api.vote(p,'B','abstain');assert.equal(api.outcome(p).result,'accepted');assert.equal(p.votes.length,2);
api.amend(store,p,'Amended care','Respond to feedback');assert.equal(p.revision,2);assert.equal(p.votes.length,0);assert.equal(p.history[0].votes.length,2);assert.throws(()=>api.apply(store,p));
api.vote(p,'A','yes');api.vote(p,'B','yes');api.apply(store,p);assert.equal(store.systems[0].wording,'Amended care');assert.equal(p.state,'adopted');assert.throws(()=>api.vote(p,'C','yes'));
let first=proposal('A'),second=proposal('A');api.vote(first,'A','yes');api.vote(second,'A','yes');api.apply(store,first);assert.throws(()=>api.apply(store,second));api.amend(store,second,'Fresh review','Review current revision');assert.equal(second.votes.length,0);api.vote(second,'A','yes');api.apply(store,second);
const rejected=proposal();api.vote(rejected,'A','no');api.vote(rejected,'B','abstain');assert.equal(api.outcome(rejected).result,'rejected');assert.throws(()=>api.vote(rejected,'Unknown','yes'));assert.throws(()=>api.vote(rejected,'A','invalid'));
for(const members of ['', 'A,a',Array.from({length:51},(_,i)=>'P'+i).join(',')])assert.throws(()=>proposal(members));
assert.throws(()=>api.amend(store,rejected,'x'.repeat(5001),''));
const notes={observation:'Seen',interpretation:'Belief',claim:'Testable question',method:'Plan',uncertainty:'Unknown'};
const exported=JSON.parse(api.pack(store,notes));assert.equal(exported.inquiry.interpretation,'Belief');assert(exported.notice.includes('unverified'));assert.equal(exported.proposals[0].history.length,1);

function element(){return {value:'',children:[],textContent:'',events:{},disabled:false,addEventListener(k,f){this.events[k]=f},append(...nodes){for(const node of nodes){this.children.push(node);if(this.children.length===1&&node.value!==undefined)this.value=node.value;}},replaceChildren(){this.children=[];this.value=''}};}
const ids=['system','proposal','member','vote','amend','apply','proposal-details','amend-wording','amend-reason','definitions','propose','title','wording','reason','members','status','choice','vote-reason','export','clear','observation','interpretation','claim','method','uncertainty'];
const els=Object.fromEntries(ids.map(id=>[id,element()]));els.choice.value='yes';context.document={getElementById:id=>els[id],createElement:element};vm.runInContext(fs.readFileSync(path.join(root,'systematics-ui.js'),'utf8'),context);
assert.equal(els.definitions.children.length,7);assert.equal(els.vote.disabled,true);
els.title.value='Personal review';els.wording.value='New definition';els.reason.value='Clearer';els.members.value='Myself';els.propose.events.click();assert.equal(els.vote.disabled,false);assert.equal(els.apply.disabled,true);
els.vote.events.click();assert.equal(els.apply.disabled,false);els['amend-wording'].value='Changed definition';els.amend.events.click();assert.equal(els.apply.disabled,true);assert(els['proposal-details'].textContent.includes('Prior rounds: 1'));els.vote.events.click();els.apply.events.click();assert.equal(els.vote.disabled,true);assert(els.definitions.children[0].children[1].textContent.includes('Changed definition'));
els.clear.events.click();assert.equal(els.vote.disabled,true);assert.equal(els.proposal.children.length,0);
console.log('Systematics checks passed: quorum, ties, abstentions, replacement votes, amendment history/reset, adoption, stale proposals, validation, exports, and UI workflow.');
