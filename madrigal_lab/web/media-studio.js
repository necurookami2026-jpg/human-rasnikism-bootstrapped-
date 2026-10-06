'use strict';
(() => {
  let selectedURL=null, originalImage=null, imageRevision=0, seedResult=null, seedRevision=0;
  let plan=null, planRevision=0, timer=null, recorder=null, recordingSession=null;
  const permitted=()=>el('media-owned').checked;
  const saveBlob=(blob,filename)=>{const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  const requirePermission=()=>{if(!permitted())throw new Error('Choose owned or authorized material and explicitly permit processing.');};
  function stopPreview(cancel=true){
    if(timer){clearInterval(timer);timer=null;}
    if(cancel&&recordingSession)recordingSession.cancelled=true;
    if(recorder&&recorder.state!=='inactive')recorder.stop();
  }
  function clearMedia(){
    imageRevision++;originalImage=null;
    for(const id of ['local-video','local-audio']){const player=el(id);player.pause();player.removeAttribute('src');player.load();player.hidden=true;}
    if(selectedURL)URL.revokeObjectURL(selectedURL);selectedURL=null;
    el('media-file').value='';el('image-export').disabled=true;
    el('image-canvas').getContext('2d').clearRect(0,0,el('image-canvas').width,el('image-canvas').height);
    el('media-info').textContent='No file selected.';
  }
  function drawImage(){
    if(!originalImage||!permitted())return;
    const canvas=el('image-canvas'),ctx=canvas.getContext('2d');
    const square=el('image-crop').checked;
    const width=originalImage.naturalWidth,height=originalImage.naturalHeight;
    const side=Math.min(width,height),sw=square?side:width,sh=square?side:height;
    const scale=Math.min(1,960/sw,540/sh);canvas.width=Math.max(1,Math.round(sw*scale));canvas.height=Math.max(1,Math.round(sh*scale));
    const brightness=Math.max(25,Math.min(200,number('image-brightness'))),contrast=Math.max(25,Math.min(200,number('image-contrast')));
    ctx.filter=`brightness(${brightness}%) contrast(${contrast}%)`;
    ctx.drawImage(originalImage,square?(width-side)/2:0,square?(height-side)/2:0,sw,sh,0,0,canvas.width,canvas.height);
    el('image-export').disabled=false;
  }
  el('media-file').addEventListener('change',()=>{
    const file=el('media-file').files[0];clearMedia();if(!file)return;
    try{
      requirePermission();
      const image=['image/png','image/jpeg','image/webp','image/gif'].includes(file.type);
      if(!image&&!file.type.startsWith('audio/')&&!file.type.startsWith('video/'))throw new Error('Select a supported raster image, audio or video file.');
      if(file.size>(image?20:64)*1024*1024)throw new Error('Local image limit is 20 MiB; audio/video limit is 64 MiB.');
      selectedURL=URL.createObjectURL(file);el('media-info').textContent=file.name+' · '+file.size+' bytes · stays in this browser';
      if(image){
        const revision=imageRevision,img=new Image();
        img.onload=()=>{if(revision!==imageRevision||!permitted())return;if(img.naturalWidth*img.naturalHeight>24000000){clearMedia();show({error:'Image exceeds the 24-million-pixel editor limit.'});return;}originalImage=img;drawImage();};
        img.onerror=()=>{if(revision===imageRevision){clearMedia();show({error:'The browser could not decode this owned image.'});}};img.src=selectedURL;
      }else{const player=el(file.type.startsWith('audio/')?'local-audio':'local-video');player.src=selectedURL;player.hidden=false;}
    }catch(error){clearMedia();show({error:error.message});}
  });
  for(const id of ['image-brightness','image-contrast','image-crop'])el(id).addEventListener('input',drawImage);
  el('image-export').addEventListener('click',()=>{const revision=imageRevision;if(!originalImage||!permitted())return;el('image-canvas').toBlob(blob=>{if(blob&&revision===imageRevision&&permitted())saveBlob(blob,'rasniki-owned-edit.png');},'image/png');});
  el('media-clear').addEventListener('click',clearMedia);

  function invalidateSeed(){seedRevision++;seedResult=null;el('seed-rendition').disabled=true;}
  function invalidatePlan(){planRevision++;plan=null;stopPreview();for(const id of ['series-download','series-preview','series-record'])el(id).disabled=true;el('series-progress').textContent='Plan needs a new review.';}
  for(const id of ['seed-name','seed-data'])el(id).addEventListener('input',invalidateSeed);
  for(const id of ['series-title','series-book','series-scenes','series-episodes'])el(id).addEventListener('input',invalidatePlan);
  el('media-owned').addEventListener('change',()=>{clearMedia();invalidateSeed();invalidatePlan();show({status:permitted()?'Owned-material processing selected.':'Processing permission withdrawn; local previews cleared.'});});
  el('data-seed').addEventListener('click',async()=>{
    invalidateSeed();const revision=seedRevision;
    try{requirePermission();const result=await action('data-seed',{record:{name:value('seed-name'),encoding:'utf8',data:value('seed-data'),owned:true,consent:true}},()=>revision===seedRevision&&permitted());if(result&&revision===seedRevision&&permitted()){seedResult=result;el('seed-rendition').disabled=false;}}catch(error){show({error:error.message});}
  });
  el('seed-rendition').addEventListener('click',async()=>{
    if(!seedResult||!permitted())return;const revision=seedRevision;
    await action('seed-rendition',{record:{seed:seedResult.seed,source_sha256:seedResult.source_sha256,source_name:value('seed-name'),count:4,owned:true,consent:true}},()=>revision===seedRevision&&permitted());
  });
  el('series-plan').addEventListener('click',async()=>{
    invalidatePlan();const revision=planRevision;
    try{requirePermission();const result=await action('series-plan',{record:{title:value('series-title'),book:value('series-book'),episodes:number('series-episodes'),scenes:number('series-scenes'),duration:2,owned:true,consent:true}},()=>revision===planRevision&&permitted());if(result&&revision===planRevision&&permitted()){plan=result;for(const id of ['series-download','series-preview','series-record'])el(id).disabled=false;el('series-progress').textContent=plan.scene_count+' scenes · '+plan.duration_seconds+' seconds · draft text-card plan';}}catch(error){show({error:error.message});}
  });
  el('series-download').addEventListener('click',()=>{if(plan&&permitted())saveBlob(new Blob([JSON.stringify(plan,null,2)+'\n'],{type:'application/json'}),'rasniki-series-plan.json');});
  function drawCard(scene){
    const canvas=el('series-canvas'),ctx=canvas.getContext('2d');
    ctx.fillStyle='#0f1722';ctx.fillRect(0,0,960,540);ctx.fillStyle='#98dfbd';ctx.font='28px sans-serif';ctx.fillText(plan.title.slice(0,55),48,64);
    ctx.fillStyle='#edf1f1';ctx.font='22px sans-serif';let line='',y=140;
    for(const word of scene.source_excerpt.split(/\s+/)){const next=line?line+' '+word:word;if(ctx.measureText(next).width>860&&line){ctx.fillText(line,48,y);line=word;y+=34;}else line=next;if(y>440)break;}
    if(y<=440)ctx.fillText(line.slice(0,120),48,y);ctx.fillStyle='#b1bfce';ctx.font='18px sans-serif';ctx.fillText('Scene '+scene.number+' · original-text draft animatic',48,500);
  }
  function preview(record=false){
    try{
      requirePermission();if(!plan)throw new Error('Form a production plan first.');stopPreview();
      const scenes=plan.episodes.flatMap(episode=>episode.scenes);let index=0;drawCard(scenes[0]);
      if(record){
        if(!window.MediaRecorder||!el('series-canvas').captureStream)throw new Error('This browser has no canvas recording support; download the plan instead.');
        const mime=['video/webm;codecs=vp8','video/webm'].find(type=>MediaRecorder.isTypeSupported(type));if(!mime)throw new Error('WebM recording is unavailable in this browser.');
        const stream=el('series-canvas').captureStream(24),chunks=[];let bytes=0;
        const active=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:1000000});recorder=active;
        const session={cancelled:false,revision:planRevision};recordingSession=session;
        active.ondataavailable=event=>{bytes+=event.data.size;if(bytes>16*1024*1024){session.cancelled=true;if(recorder===active){stopPreview();show({error:'Animatic reached its 16 MiB recording limit.'});}return;}if(event.data.size)chunks.push(event.data);};
        active.onstop=()=>{stream.getTracks().forEach(track=>track.stop());if(!session.cancelled&&session.revision===planRevision&&permitted()&&chunks.length)saveBlob(new Blob(chunks,{type:mime}),'rasniki-text-card-animatic.webm');if(recorder===active){recorder=null;recordingSession=null;}};
        active.onerror=()=>{stopPreview();show({error:'The browser could not record this animatic.'});};active.start(1000);
      }
      el('series-progress').textContent=(record?'Recording':'Previewing')+' scene 1 of '+scenes.length;
      const started=performance.now();
      timer=setInterval(()=>{
        const elapsed=performance.now()-started,next=Math.floor(elapsed/2000);
        if(next>=scenes.length){stopPreview(false);el('series-progress').textContent='Draft text-card sequence completed.';return;}
        if(next!==index){index=next;el('series-progress').textContent=(record?'Recording':'Previewing')+' scene '+(index+1)+' of '+scenes.length;}
        drawCard(scenes[index]);const ctx=el('series-canvas').getContext('2d');ctx.fillStyle='#98dfbd';ctx.fillRect(48,520,864*((elapsed%2000)/2000),4);
      },40);
    }catch(error){stopPreview();show({error:error.message});}
  }
  el('series-preview').addEventListener('click',()=>preview(false));el('series-record').addEventListener('click',()=>preview(true));
  el('series-stop').addEventListener('click',()=>{stopPreview();el('series-progress').textContent='Preview stopped; incomplete recording discarded.';});
  window.addEventListener('pagehide',()=>{stopPreview();clearMedia();});
})();
