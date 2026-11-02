// node render.js outdir — PNG оформления канала
const {chromium}=require('playwright');const path=require('path');const out=process.argv[2]||'.';
const J=[['banner',2560,1440,1,false],['banner#safe',2560,1440,1,false],['avatar',800,800,1,false],['avatar2',800,800,1,false],['wm',150,150,1,true],['wm',150,150,4,true]];
(async()=>{const b=await chromium.launch();
 for(const [m,w,h,d,tr] of J){const pg=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:d});
  await pg.goto('file://'+path.resolve(__dirname,'channel.html')+'?m='+m.replace('#safe','')+(m.includes('#')?'#safe':''));
  await pg.evaluate(()=>document.fonts.ready.then(()=>1));await pg.waitForTimeout(300);
  const name=m.replace('#safe','_safezone')+(d>1?`@${d}x`:'');
  await pg.screenshot({path:path.join(out,`yt_${name}.png`),omitBackground:tr});await pg.close();console.log(name)}
 await b.close()})();
