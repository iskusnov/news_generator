// node render_list.js list.json — [{out, spec, alpha}] → PNG 1920×1080 (alpha: прозрачный фон)
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const css=fs.readFileSync(__dirname+'/fonts.css','utf8')+fs.readFileSync(__dirname+'/nation.css','utf8');const js=fs.readFileSync(__dirname+'/nation.js','utf8');
const L=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});p.on('pageerror',e=>console.log('ERR',e.message));
for(const it of L){await p.setContent(`<html><head><meta charset="utf-8"><style>${css}</style></head><body><script>window.SPEC=${JSON.stringify(it.spec)};${js}</script></body></html>`);
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(120);fs.mkdirSync(path.dirname(it.out),{recursive:true});
await p.screenshot({path:it.out,omitBackground:!!it.alpha});}
await b.close();console.log('rendered',L.length);})();
