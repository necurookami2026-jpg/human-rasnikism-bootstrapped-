(function(root){
'use strict';
const pairs=[['this','request and response status'],['ahow / hot','method and actual operation'],['awho / tho','operator and responding component'],['awhat / that','result and capability'],['awhen / then','trigger and sequence'],['awhere / there','execution and evidence location'],['awhy / thy','reason, limits and next step']];
const commands=['help','find','runes','english','math','bitflip','show'];
function respond(raw){
 const valid=typeof raw==='string', input=valid?raw:'', size=input.length;
 const request=input.slice(0,2000), trimmed=request.trim(), first=trimmed.split(/\s+/)[0].toLowerCase();
 const alias=pairs.some(([label])=>label.split(' / ').includes(first));
 let status='completed',code='completed',result='',reason='',method='The local deterministic command interpreter was invoked once.';
 if(!valid){status='unable';code='invalid-input';reason='The supplied input is not a text string. Supply a command as text.';}
 else if(size>2000){status='unable';code='command-limit';reason='The command contains '+size+' UTF-16 code units, exceeding the declared 2000-unit command bound. The interpreter was not invoked. Shorten or split the command; each reply must be reviewed separately.';}
 else if(!trimmed){status='waiting';code='missing-input';reason='No command has been supplied. Enter help or a documented command; no calculation has been performed.';}
 else if(alias){method='The requested response heading was recognised; no factual answer was inferred from its name.';result='The headings organise request, method, actor, result, timing, location and reasons. Use help for executable commands.';}
 else if(!commands.includes(first)){status='unable';code='unsupported-command';reason='The first word does not identify an implemented command. Free-form questions, remote actions and specialist analyses are not implemented by this deterministic bot. Use help to select a supported operation or provide evidence to a qualified operator.';}
 else{try{result=String(root.RasnikiIO.command(input));if(first==='find'&&result==='No catalogue matches.'){status='no-match';code='no-catalogue-match';reason='The local catalogue search returned no matches. This does not establish that the subject does not exist. Try a different local search term.';}}
 catch(error){status='unable';code='operation-rejected';reason='The interpreter rejected this operation: '+String(error.message).slice(0,1000)+'. Correct the named input condition before trying again. No successful result is claimed.';}}
 const execution=['completed','no-match'].includes(status)&&!alias;
 if(!execution&&!alias)method='The operation was '+(code==='operation-rejected'?'attempted and rejected by its input or arithmetic checks.':'not executed because the request did not meet the documented interface conditions.');
 const limits='Commands accept at most 2000 UTF-16 code units; catalogue search returns at most ten records. Exact integer arithmetic uses the existing command tool; rune conversion folds letter case. This bot has no remote model, shell, network operation or background agent. Source text is data and is not evaluated as code.';
 const sections=[
 {label:'this',text:'The response status is '+status+' ('+code+'). '+(size>2000?'The request preview is truncated; the full input was not accepted.':'The request is recorded as supplied below.')},
 {label:'ahow / hot',text:method+' Supported operations are help, find, runes, english, math, bitflip and show.'},
 {label:'awho / tho',text:'The user or client supplies the input. The local Rasniki IObot deterministic interface produces this report. No independent expert review or personal identity verification is recorded.'},
 {label:'awhat / that',text:result?'The literal operation output follows in the result section. Its scope is the documented local command.':'No successful operation output is available. '+reason},
 {label:'awhen / then',text:'A reply is generated 350 milliseconds after the latest input change, after Enter, or after pressing Respond. The sequence is input, validation, bounded interpretation, report and optional export. No wall-clock timestamp or external event is inferred.'},
 {label:'awhere / there',text:'Interpretation and report generation occur in this browser or JavaScript host. Evidence consists of the supplied command and literal result or rejection. Downloaded paperwork is saved only by an explicit export action; drafts are not retained between page loads.'},
 {label:'awhy / thy',text:(reason||'The request matched a documented operation or response heading. The reported output is a finite software observation, not a measured natural-science result.')+' '+limits+' If a requested capability is absent, the client must choose a documented operation or obtain the required data and authorised implementation. Bypassing a bound is not performed.'}
 ];
 const record={format:'rasniki-iobot-response',version:1,status,code,request,request_units:size,request_truncated:size>2000,result,reason,sections,limits,scientific_scope:'Exact means finite documented command behaviour and literal evidence, not universal proof. Unknown facts, measurements, uncertainty and review remain unestablished unless supplied.'};
 record.paperwork='# Rasniki IObot scientific prose response\n\n'+sections.map(s=>'## '+s.label+'\n\n'+s.text).join('\n\n')+'\n\n## Supplied request\n\n'+request+'\n\n## Literal result\n\n'+(result||'No successful result.')+'\n\n## Evidence and review\n\n'+record.scientific_scope+' Record external evidence, calibration, uncertainty, reviewer and corrections separately when relevant. This generated paperwork contains no invented measurements or completed approvals.\n';
 return record;
}
root.RasnikiResponses={pairs,respond};
})(globalThis);
