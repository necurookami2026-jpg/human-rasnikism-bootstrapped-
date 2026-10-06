'use strict';
(() => {
  const optionalNumber = id => value(id).trim() ? number(id) : null;
  const consent = () => el('board-consent').checked;
  const alias = () => value('board-alias');
  const owner = () => el('recovery-owner').checked;
  const wire = (id, name, build = () => ({}), after) => {
    el(id).addEventListener('click', async () => {
      try {
        if (!token) throw new Error('Wait for the local session to be ready.');
        const result = await action(name, build());
        if (result && after) after(result);
      } catch (error) { show({error: error.message}); }
    });
  };
  const download = (text, filename, type) => {
    const url = URL.createObjectURL(new Blob([text], {type}));
    const link = document.createElement('a');
    link.href = url; link.download = filename; document.body.append(link);
    link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  wire('atlas-search', 'atlas-search', () => ({query:value('atlas-query'),limit:128}), result => {
    el('atlas-results').replaceChildren();
    for (const item of result.items) card(el('atlas-results'), item.label, item.scope, item.category + ' · ' + item.status);
  });
  wire('atlas-tree', 'atlas-tree', () => ({query:value('atlas-query'),depth:3,limit:256}));
  wire('document-types', 'document-types', () => ({limit:32}));
  wire('fandom-seed', 'fandom-seed', () => ({seed:value('fandom-seed-text'),count:4}));

  let paperRevision = 0, paperResult = null, mapRevision = 0, mapResult = null, backupRevision = 0;
  const invalidatePaper = () => {paperRevision++;paperResult=null;el('paper-download').disabled=true;};
  el('paper-form').addEventListener('input', invalidatePaper);
  el('paper-form').addEventListener('change', invalidatePaper);
  el('workpaper').addEventListener('click', async () => {
    invalidatePaper(); const revision = paperRevision;
    const result = await action('workpaper', {record:{format:value('paper-format'),title:value('paper-title'),purpose:value('paper-purpose'),body:value('paper-body')}}, () => revision===paperRevision);
    if (result && revision===paperRevision) {paperResult=result;el('paper-download').disabled=false;}
  });
  el('paper-download').addEventListener('click', () => {if(paperResult)download(paperResult.text,'rasniki-workpaper.md','text/markdown');});
  el('map-points').addEventListener('input', () => {mapRevision++;mapResult=null;el('map-download').disabled=true;});
  el('map-plot').addEventListener('click', async () => {
    const revision=++mapRevision;mapResult=null;el('map-download').disabled=true;
    try {
      const result=await action('map-plot',{points:JSON.parse(value('map-points'))},()=>revision===mapRevision);
      if(result && revision===mapRevision){mapResult=result;el('map-download').disabled=false;}
    }catch(error){if(revision===mapRevision)show({error:error.message});}
  });
  el('map-download').addEventListener('click',()=>{if(mapResult)download(mapResult.svg,'rasniki-supplied-coordinate-plot.svg','image/svg+xml');});

  wire('board-create','board-create',()=>{
    const kind=value('board-kind');
    const record={kind,title:value('board-title'),body:value('board-body'),consent:consent(),parent:optionalNumber('board-parent'),metadata:JSON.parse(value('board-details')),member_alias:alias()};
    if(kind==='survey')record.options=value('board-options').split('\n').map(s=>s.trim()).filter(Boolean);
    if(kind==='quest')record.points=number('board-points');
    return {record};
  },result=>{el('board-id').value=result.id;});
  wire('board-get','board-get',()=>({id:number('board-id')}));
  wire('board-list','board-list'); wire('board-tree','board-tree'); wire('leaderboard','leaderboard');
  wire('board-reply','board-reply',()=>({id:number('board-id'),body:value('board-reply-text'),consent:consent(),member_alias:alias()}));
  wire('board-vote','board-vote',()=>({id:number('board-id'),option:number('board-option'),consent:consent(),member_alias:alias()}));
  wire('board-transition','board-transition',()=>({id:number('board-id'),state:value('board-state'),reason:value('board-reason'),consent:consent()}));
  wire('board-delete','board-delete',()=>({id:number('board-id'),consent:consent()}));

  wire('economy-report','economy-report');
  wire('obligation','obligation',()=>({lender:value('debt-lender'),borrower:value('debt-borrower'),amount:number('debt-amount')}),result=>{el('debt-id').value=result.id;});
  wire('lend','lend',()=>({id:number('debt-id')}));
  wire('repay','repay',()=>({id:number('debt-id'),amount:number('debt-amount')}));
  wire('coupon','coupon',()=>({title:value('coupon-title'),amount:number('coupon-amount')}),result=>{el('coupon-id').value=result.id;});
  wire('redeem-coupon','redeem-coupon',()=>({id:number('coupon-id'),account:value('debt-borrower')}));
  wire('demo-contract','demo-contract',()=>({title:value('contract-title'),text:value('contract-text'),parent:optionalNumber('contract-parent')}),result=>{el('contract-id').value=result.id;});
  wire('review-contract','review-contract',()=>({id:number('contract-id'),reviewer:value('contract-reviewer'),consent:el('contract-consent').checked}));
  wire('finalise-contract','finalise-contract',()=>({id:number('contract-id'),author:value('contract-reviewer'),consent:el('contract-consent').checked}));
  wire('verify-contract','verify-contract',()=>({id:number('contract-id')}));
  wire('recovery-plan','recovery-plan',()=>{
    const record={case:value('recovery-case'),owner_asserted:owner()};
    if(value('recovery-provider').trim())record.provider=value('recovery-provider');
    if(value('recovery-url').trim())record.official_url=value('recovery-url');
    return {record};
  });
  const backupRecord=()=>({backup:value('backup-text'),encoding:value('backup-encoding'),owner_asserted:owner(),...(value('backup-sha').trim()?{expected_sha256:value('backup-sha')}:{})});
  for(const id of ['backup-form','recovery-owner'])el(id).addEventListener('input',()=>{backupRevision++;});
  el('backup-clear').addEventListener('click',()=>{backupRevision++;el('backup-text').value='';el('backup-sha').value='';el('backup-target').value='';el('recovery-owner').checked=false;show({status:'Backup form cleared; saved local files are unchanged.'});});
  el('backup-inspect').addEventListener('click',async()=>{const revision=++backupRevision;await action('backup-inspect',{record:backupRecord()},()=>revision===backupRevision);});
  wire('backup-restore','backup-restore',()=>({record:{...backupRecord(),target:value('backup-target')}}));

  async function startWorkbench(){
    const responses=await Promise.all([fetch('/api/boards'),fetch('/api/workpapers')]);
    if(responses.some(response=>!response.ok))throw new Error('Workbench form catalogue unavailable.');
    const [boards,papers]=await Promise.all(responses.map(response=>response.json()));
    for(const kind of boards.kinds){const option=document.createElement('option');option.value=kind;option.textContent=kind;el('board-kind').append(option);}
    el('board-kind').value='inquiry';
    el('board-kind').addEventListener('change',()=>{el('survey-fields').hidden=value('board-kind')!=='survey';el('quest-fields').hidden=value('board-kind')!=='quest';});
    for(const format of papers.formats){const option=document.createElement('option');option.value=format.id;option.textContent=format.id+' · '+format.name;el('paper-format').append(option);}
    el('board-create').disabled=false;el('workpaper').disabled=false;
  }
  startWorkbench().catch(error=>show({error:error.message}));
})();
