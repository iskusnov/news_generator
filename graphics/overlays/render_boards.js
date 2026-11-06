// node render_boards.js specs.json outDir — «живые слайды» уроков (type board, 16:9): моушн-панель на пустом месте слайда.
// Рендерятся только окна вокруг битов (spec.beats, секунды от начала плашки); между битами кадр стоит —
// пишется список concat (PNG + длительность) → ffmpeg собирает VP9-alpha размером с панель (+ поля под тень).
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const [,,specFile,outDir]=process.argv;const FPS=25,PAD=40;
const only=process.env.ONLY?process.env.ONLY.split(','):null;
(async()=>{
  const specs=JSON.parse(fs.readFileSync(specFile,'utf8')).filter(s=>s.type=='board'&&(!only||only.includes(s.id)));
  const b=await chromium.launch();
  for(const s of specs){
    const pg=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
    await pg.goto('file://'+path.resolve(__dirname,'bootcamp_short.html'));
    await pg.evaluate(()=>document.fonts.ready.then(()=>1));
    await pg.evaluate(sp=>{window.setup(Object.assign({wide:true},sp));return 1},s);
    await pg.evaluate(()=>document.fonts.ready.then(()=>1));
    const B=s.box,clip={x:B.x-PAD,y:B.y-PAD,width:B.w+2*PAD,height:B.h+2*PAD};
    const n=Math.round(s.dur*FPS);const need=new Uint8Array(n);
    const mark=(a,z)=>{for(let f=Math.max(0,Math.floor(a*FPS));f<=Math.min(n-1,Math.ceil(z*FPS));f++)need[f]=1};
    mark(0,.7);mark(s.dur-.5,s.dur);(s.beats||[]).forEach(t=>mark(t-.3,t+1.4));
    const dir=path.join(outDir,s.id);fs.mkdirSync(dir,{recursive:true});
    const list=[];let last=null,run=0,cnt=0;
    for(let f=0;f<n;f++){
      if(need[f]||last===null){
        if(last!==null)list.push([last,run]);
        await pg.evaluate(t=>{window.seek(t);return 1},f/FPS);
        last=path.join(dir,`f${String(f).padStart(6,'0')}.png`);await pg.screenshot({path:last,clip,omitBackground:true});cnt++;run=1;
      }else run++;
    }
    list.push([last,run]);
    fs.writeFileSync(path.join(dir,'list.txt'),list.map(([f,r])=>`file '${path.basename(f)}'\nduration ${(r/FPS).toFixed(4)}`).join('\n')+`\nfile '${path.basename(last)}'\n`);
    console.log('done',s.id,'кадров',n,'отрисовано',cnt);await pg.close();
  }
  await b.close();
})();
