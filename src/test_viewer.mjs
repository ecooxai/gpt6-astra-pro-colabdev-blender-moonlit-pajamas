import {chromium} from 'playwright';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/home/dev/.local/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const errors=[];
for(const [name,width,height] of [['desktop',1440,1100],['mobile',390,844]]){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(name+': '+e.message));
  await page.goto('http://127.0.0.1:8791/',{waitUntil:'networkidle',timeout:90000});
  await page.waitForFunction(()=>window.__modelReady===true,{timeout:90000});
  await page.waitForTimeout(1500);
  await page.screenshot({path:'renders/review/ui-'+name+'.png',fullPage:true});
  const result=await page.evaluate(()=>({ready:window.__modelReady,triangles:window.__modelTriangles,overflow:document.documentElement.scrollWidth>innerWidth}));
  console.log(name,JSON.stringify(result));await page.close();
}
await browser.close();await fs.writeFile('logs/browser-errors.json',JSON.stringify(errors,null,2));
if(errors.length){console.error(errors);process.exitCode=1;}
