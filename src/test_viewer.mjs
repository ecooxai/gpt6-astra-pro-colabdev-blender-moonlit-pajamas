import {chromium} from 'playwright';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/home/dev/.local/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const report=[],errors=[];
try{
for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
 const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(name+': '+e.message));
 page.on('console',m=>{if(m.type()==='error')errors.push(name+': '+m.text());});
 await page.goto(process.env.PREVIEW_URL||'http://127.0.0.1:8791/',{waitUntil:'networkidle',timeout:90000});
 await page.waitForFunction(()=>window.__modelReady===true,null,{timeout:90000});
 await page.waitForTimeout(1000);
 await page.screenshot({path:'renders/review/ui-'+name+'-top.png'});
 const a=await page.evaluate(()=>window.__renderFrames);await page.waitForTimeout(1200);const b=await page.evaluate(()=>window.__renderFrames);
 for(const view of ['quarter','side','left','back','face','front']){await page.locator('[data-view="'+view+'"]').click();await page.waitForTimeout(100);}
 await page.locator('#shading').click();await page.waitForTimeout(200);await page.locator('#shading').click();
 if(name==='desktop'){await page.locator('[data-view="face"]').click();await page.waitForTimeout(300);await page.locator('#stage').screenshot({path:'renders/review/ui-face.png'});await page.locator('[data-view="front"]').click();}
 await page.locator('#moderender').click();await page.waitForTimeout(100);await page.locator('#mode3d').click();
 await page.evaluate(async()=>{for(const image of document.querySelectorAll('#renders img')){image.loading='eager';try{await image.decode();}catch{}}});
 await page.evaluate(()=>scrollTo(0,document.body.scrollHeight));await page.waitForTimeout(500);const c=await page.evaluate(()=>window.__renderFrames);await page.waitForTimeout(1000);const d=await page.evaluate(()=>window.__renderFrames);
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'renders/review/ui-'+name+'.png',fullPage:true});
 const state=await page.evaluate(()=>({ready:window.__modelReady,triangles:window.__modelTriangles,drawCalls:window.__drawCalls,geometryCount:window.__geometryCount,revision:document.querySelector('#revision').textContent,overflow:document.documentElement.scrollWidth>innerWidth,galleryImages:[...document.querySelectorAll('#renders img')].filter(i=>i.naturalWidth>0).length,artifactLinks:document.querySelectorAll('#downloads a').length}));
 const result={device:name,...state,idleFrameDelta:b-a,offscreenFrameDelta:d-c,result:state.ready&&!state.overflow&&d-c===0&&state.galleryImages===11&&state.drawCalls<=48?'PASS':'FAIL'};report.push(result);console.log(JSON.stringify(result));await page.close();
}
}finally{await browser.close();}
const out={testedAt:new Date().toISOString(),report,errors,result:errors.length||report.some(r=>r.result==='FAIL')?'FAIL':'PASS'};
await fs.writeFile('preview/assets/browser_validation.json',JSON.stringify(out,null,2));await fs.writeFile('logs/browser-errors.json',JSON.stringify(errors,null,2));if(out.result!=='PASS'){console.error(errors);process.exitCode=1;}
