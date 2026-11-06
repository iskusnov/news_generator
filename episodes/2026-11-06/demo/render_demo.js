const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+__dirname+'/demo.html');await p.evaluate(()=>document.fonts.ready.then(()=>1));await p.waitForTimeout(500);
const dur=await p.evaluate(()=>DUR);const sfx=await p.evaluate(()=>SFX);fs.writeFileSync(__dirname+'/sfx.json',JSON.stringify({dur,sfx}));
fs.mkdirSync(__dirname+'/f',{recursive:true});const n=Math.round(dur*25);
for(let i=0;i<n;i++){await p.evaluate(t=>{seek(t);return 1},i/25);await p.screenshot({path:`${__dirname}/f/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close();console.log('frames',n);})();
