const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1100,height:400},deviceScaleFactor:2});
const J=require(process.argv[2]);for(const [n,P] of Object.entries(J)){await p.goto('file://'+__dirname+'/post.html?n='+n+'#'+encodeURIComponent(JSON.stringify(P)));await p.evaluate(()=>document.fonts.ready.then(()=>1));await p.waitForTimeout(300);
await p.locator('#c').screenshot({path:`/home/claude/news_generator/graphics/shots/1106_${n}.png`});console.log(n);}await b.close();})();
