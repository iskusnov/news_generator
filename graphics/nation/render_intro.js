// node render_intro.js spec.json outdir — кадры заставки 1920×1080, 25 к/с
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const S=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const out=process.argv[3];fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+path.resolve(__dirname,process.env.TPL||'intro_motion.html'));await p.evaluate(()=>document.fonts.ready);
await p.evaluate(s=>window.setup(s),S);await p.waitForTimeout(200);const n=Math.round(S.dur*25);const only=process.env.FR?process.env.FR.split(',').map(Number):null;
for(let f=0;f<n;f++){if(only&&!only.includes(f))continue;await p.evaluate(t=>window.seek(t),f/25);await p.screenshot({path:`${out}/f${String(f).padStart(4,'0')}.png`});}
await b.close();console.log('frames',n);})();
