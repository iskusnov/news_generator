const {chromium}=require('playwright');const fs=require('fs');
const css=fs.readFileSync('fonts.css','utf8')+fs.readFileSync('nation.css','utf8');const js=fs.readFileSync('nation.js','utf8');
const D='/tmp/claude-0/-home-claude/c00eaf8f-bd8a-5781-af8b-f820204561eb/scratchpad/ds/';
const b64=f=>'data:image/jpeg;base64,'+fs.readFileSync(D+f).toString('base64');
const S=[
{type:'intro',num:'08',title:'Мульти­агентные системы',sub:'Буткемп AI-Driven разработки · 3 поток · 10.11.2026',lector:'Николай Барышников',role:'dev',photo:b64('nik.jpg'),skills:['Оркестратор','Handoff','Иерархия']},
{type:'screen',num:'08',topic:'Мультиагентные системы',lector:'Николай Барышников',role:'dev',photo:b64('nik.jpg'),shot:b64('scr_full.jpg'),ch:'02',chTitle:'Когда граница оправдана',progress:.35},
{type:'chapter',n:2,total:6,title:'Когда граница оправдана',sub:'Отдельный контекст, разные полномочия, независимая проверка'},
{type:'question',src:'Вопрос из чата',q:'А проверка разрешения на операцию — это разве не guard rule?',who:'Янош Фенвеши · участник 3-го потока',initials:'ЯФ',skills:['Guard rule','Оркестратор']},
];
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});p.on('pageerror',e=>console.log('ERR',e.message));
for(const [i,s] of S.entries()){await p.setContent(`<html><head><meta charset="utf-8"><style>${css}</style></head><body><script>window.SPEC=${JSON.stringify(s)};${js}</script></body></html>`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);await p.screenshot({path:`${D}sample_${i+1}_${s.type}.png`});}
await b.close();})();
