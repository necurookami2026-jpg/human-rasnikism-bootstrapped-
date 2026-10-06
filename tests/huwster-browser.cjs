// Optional: Playwright + Chromium; start the local lab before this test.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),http=require('node:http');
(async()=>{
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'huwster-browser-'));
 const server=http.createServer((req,res)=>{const name=req.url==='/game.html'?'game.html':req.url==='/inert.html'?'inert.html':null;if(!name){res.writeHead(404);res.end();return;}res.setHeader('Content-Type','text/html;charset=utf-8');res.end(fs.readFileSync(path.join(directory,name)));});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const base='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.HUWSTER_URL||'http://127.0.0.1:8765/');
  await page.waitForFunction(()=>document.getElementById('huwster-category').options.length>0);
  await page.waitForFunction(()=>document.getElementById('connection').textContent==='Local session ready');
  if(await page.locator('#huwster').isHidden())throw Error('Default workspace hidden');
  await page.click('#huwster-run');await page.waitForFunction(()=>!document.getElementById('huwster-play').disabled);
  await page.click('#huwster-step');if(!(await page.locator('#huwster-progress').innerText()).includes('tick 1'))throw Error('Frame step failed');
  await page.click('#huwster-packet');await page.waitForFunction(()=>!document.getElementById('huwster-packet-export').disabled);
  let [download]=await Promise.all([page.waitForEvent('download'),page.click('#huwster-game-export')]);await download.saveAs(path.join(directory,'game.html'));
  const standalone=await browser.newPage();standalone.on('pageerror',e=>errors.push(e.message));await standalone.goto(base+'/game.html');
  await standalone.waitForFunction(()=>document.getElementById('status').textContent.includes('Tick 0'));
  await standalone.click('#step');if(!(await standalone.locator('#status').innerText()).includes('Tick 1'))throw Error('Exported replay failed');
  await standalone.keyboard.press('ArrowRight');if(await standalone.locator('#title').innerText()!=='Restoration Commons')throw Error('Exported title differs');
  await page.fill('#huwster-source','world "</script><script>window.injected=1</script>"\nactor demo 0 0 person\ntick 1');
  await page.click('#huwster-run');await page.waitForFunction(()=>!document.getElementById('huwster-game-export').disabled);
  [download]=await Promise.all([page.waitForEvent('download'),page.click('#huwster-game-export')]);await download.saveAs(path.join(directory,'inert.html'));
  await standalone.goto(base+'/inert.html');await standalone.waitForFunction(()=>document.getElementById('title').textContent.includes('</script>'));
  if(await standalone.evaluate(()=>window.injected))throw Error('User data executed');if(errors.length)throw Error(errors.join('; '));
  console.log('Browser checks passed: default workspace, game run/step, 49-document packet, playable export, replay and inert embedded data.');
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));fs.rmSync(directory,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
