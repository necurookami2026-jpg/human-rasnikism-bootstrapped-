(function(root){
'use strict';
const definitions=[
['yorkie','Archangel Yorkie','Attentive companionship, small acts of care, and clear boundaries.'],
['anticlaw','Archangel Anticlaw','Review unwanted pressure, coercive arrangements, and permission boundaries.'],
['blue-esteemer','Blue Esteemer Anticlaw','Respectful self-regard without coercion or humiliation.'],
['spiritual-sciences','Archangel Spiritual Sciences','Distinguish observation, interpretation, belief, testable claims, methods, and uncertainty.'],
['counter','Counterantonymmakkakah','Reconsider a reframing or release, preserving useful work and correcting mistaken reversals.'],
['rasniki-counter','Rasniki Counterantonymmakkakah','Apply reconsideration to the Rasniki collection.'],
['blue-counter','Blue-only Counterantonymmakkakah','Apply reconsideration within the chosen Blue framework without controlling others.']
];
function text(value,max=2000){if(typeof value!=='string'||value.length>max)throw Error('Text field exceeds its limit');return value.trim();}
function create(){return {format:'rasniki-systematics',version:1,systems:definitions.map(([id,name,wording])=>({id,name,wording,revision:1})),proposals:[]};}
function propose(store,fields){if(store.proposals.length>=50)throw Error('Proposal limit reached');const system=store.systems.find(s=>s.id===fields.system),wording=text(fields.wording,5000),reason=text(fields.reason),title=text(fields.title,200);if(!system||!wording||!title)throw Error('Choose a system and supply a title and wording');const members=text(fields.members,5000).split(',').map(s=>text(s,100)).filter(Boolean);if(!members.length||members.length>50||new Set(members.map(s=>s.toLowerCase())).size!==members.length)throw Error('Use 1–50 unique participant labels');const proposal={id:store.proposals.length+1,system:system.id,baseRevision:system.revision,title,wording,reason,members,votes:[],revision:1,history:[],state:'open'};store.proposals.push(proposal);return proposal;}
function outcome(proposal){const counts={yes:0,no:0,abstain:0};for(const vote of proposal.votes)counts[vote.choice]++;const cast=proposal.votes.length,quorum=Math.floor(proposal.members.length/2)+1;return {...counts,cast,quorum,result:cast<quorum?'pending':counts.yes>counts.no?'accepted':counts.no>counts.yes?'rejected':'tie'};}
function vote(proposal,member,choice,reason=''){if(proposal.state!=='open'||!proposal.members.includes(member)||!['yes','no','abstain'].includes(choice))throw Error('Invalid vote or closed proposal');const record={member,choice,reason:text(reason)};proposal.votes=proposal.votes.filter(v=>v.member!==member);proposal.votes.push(record);return outcome(proposal);}
function amend(store,proposal,wording,reason){const next=text(wording,5000),why=text(reason);if(proposal.state!=='open'||!next||proposal.revision>=50)throw Error('Cannot amend this proposal');const system=store.systems.find(s=>s.id===proposal.system);proposal.history.push({revision:proposal.revision,baseRevision:proposal.baseRevision,wording:proposal.wording,reason:proposal.reason,votes:proposal.votes.map(v=>({...v}))});proposal.wording=next;proposal.reason=why;proposal.revision++;proposal.baseRevision=system.revision;proposal.votes=[];}
function apply(store,proposal){const system=store.systems.find(s=>s.id===proposal.system);if(proposal.state!=='open'||outcome(proposal).result!=='accepted')throw Error('Only an open accepted proposal can be applied');if(system.revision!==proposal.baseRevision)throw Error('System changed; review and amend this proposal before applying');system.wording=proposal.wording;system.revision++;proposal.state='adopted';}
function inquiry(fields){const result={};for(const key of ['observation','interpretation','claim','method','uncertainty'])result[key]=text(fields[key]);return result;}
function pack(store,notes){return JSON.stringify({...store,notice:'Local, unverified participant records; no authenticated election or scientific certification.',inquiry:inquiry(notes)},null,2);}
root.RasnikiSystematics={create,propose,outcome,vote,amend,apply,inquiry,pack};
})(globalThis);
