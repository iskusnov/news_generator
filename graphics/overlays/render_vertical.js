// node render.js specs.json outdir [--preview]  (preview: few frames over bg.jpg at 1x)
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const [,,specFile,outDir,flag]=process.argv;const preview=flag==='--preview';const FPS=25;
const only=process.env.ONLY?process.env.ONLY.split(','):null;
(async()=>{
  const specs=JSON.parse(fs.readFileSync(specFile,'utf8')).filter(s=>!only||only.includes(s.id));
  const b=await chromium.launch();
  const pg=await b.newPage({viewport:(process.env.TPL?{width:1080,height:1920}:{width:1920,height:1080}),deviceScaleFactor:preview?0.5:(process.env.TPL?1:2)});
  await pg.goto('file://'+path.resolve(__dirname,''+(process.env.TPL||'template.html')+''));
  await pg.evaluate(()=>document.fonts.ready.then(()=>1));
  if(preview)await pg.evaluate(()=>document.body.classList.add('bg'));
  for(const s of specs){
    await pg.evaluate(sp=>{window.setup(sp);return 1},s);await pg.evaluate(()=>document.fonts.ready.then(()=>1));
    const dir=path.join(outDir,s.id);fs.mkdirSync(dir,{recursive:true});
    const n=Math.round(s.dur*FPS);
    const frames=preview?(s.pv||[0.3,0.5,0.75].map(f=>f*s.dur)).map(t=>Math.round(t*FPS)):[...Array(n).keys()];
    for(const f of frames){
      await pg.evaluate(t=>{window.seek(t);return 1},f/FPS);
      await pg.screenshot({path:path.join(dir,`f${String(f).padStart(4,'0')}.${preview?'jpg':'png'}`),omitBackground:!preview,...(preview?{type:'jpeg',quality:80}:{})});
    }
    console.log('done',s.id,frames.length);
  }
  await b.close();
})();
