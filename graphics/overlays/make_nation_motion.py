# Собирает nation_motion.html из bootcamp_short.html: тот же движок сцен (stage, kinetic, steps, chat…), тема Нэйшн v1.
import os
D = os.path.dirname(os.path.abspath(__file__))
s = open(D + '/bootcamp_short.html', encoding='utf-8').read()
s = s.replace('<script src="icons_boot.js"></script>', '<script src="icons_boot.js"></script>\n<link rel="stylesheet" href="../nation/fonts.css">', 1)
CSS = r'''
/* ===== ТЕМА НЭЙШН v1 (11.11.2026): бумага/тушь, один жёлтый акцент, плоско, пунктир = связь ===== */
:root{--paper:#F6F5F1;--warm:#E7E4DC;--line:#D8D6CF;--ink:#15161A;--body:#15161A;--muted:#5E6168;--a3:#F2CB3A;--a5:#F2CB3A;--a7:#15161A;--sans:'Onest',sans-serif;--mono:'JetBrains Mono',monospace;--grn:#1F8F50;--dev:#3446D3}
html,body{font-family:var(--sans)}
.top{top:44px}.logo{font-weight:800;font-size:32px;letter-spacing:-.02em;display:flex;align-items:baseline;gap:14px}.logo .st{font-family:var(--mono);font-weight:500;font-size:22px;letter-spacing:.02em;color:var(--muted)}
.pill{background:var(--ink);color:var(--paper);border-radius:6px;font-weight:700}
.title{font-size:56px;letter-spacing:-.045em;line-height:1.02}.title b{color:var(--ink);box-shadow:inset 0 -.12em 0 var(--ink)}
.fr .br{display:none}
.nm{left:0;bottom:0;border-left:0;border-radius:0 8px 0 0;box-shadow:none;display:flex;align-items:center;gap:12px;padding:12px 20px}
.nm::before{content:'';width:14px;height:14px;background:var(--dev)}
.cover span{color:var(--muted)}
.pn{background:var(--paper)}.bgd{display:none}
.pg{background:var(--ink);height:4px}
.wp{background:var(--a5)}.wp i{background:var(--ink)}
.ac .bx{border:2.8px solid var(--ink);border-radius:16px;box-shadow:none;background:#fff}
.ac.a-ic.a .bx{background:var(--a5);border-color:var(--ink)}
.ac.r .bx{background:var(--ink);border-color:var(--ink);color:var(--paper)}.ac.g .bx{background:var(--grn);border-color:var(--grn)}
.ac.a-tx.a .in{color:var(--ink);box-shadow:inset 0 -.18em 0 var(--a5)}.ac.a-tx.r .in{color:var(--ink);text-decoration:line-through;text-decoration-thickness:.08em}.ac.a-tx.g .in{color:var(--grn)}
.ac.a-pill .in{border-radius:999px}.ac.a-pill.r .in{background:var(--ink);color:var(--paper)}.ac.a-pill.g .in{background:var(--grn)}.ac.a-pill.w .in{border:2.8px solid var(--line);background:#fff}
.ac.a-ln .in{height:0;background:none;border-top:2.8px dashed var(--ink)}
.ac.a-ln.no .in{border-top:2.8px dashed var(--muted);background:none}
.ac.a-ln.a .in{height:8px;border-top:0;background:var(--a5);border-radius:4px}
.ac.a-mk .in{background:var(--ink);color:var(--paper)}.ac.a-mk.ok .in{background:var(--grn)}
.ac.a-dt.a .in{box-shadow:0 0 0 10px rgba(242,203,58,.3)}.ac.a-dt.r .in{background:var(--ink)}
.ac.a-ring .in{border-color:var(--ink);border-style:dashed}
.ac.a-card .in{border:2.8px solid var(--line);border-radius:16px;box-shadow:none;background:#fff}
.ac.a-card .in .ic{color:var(--ink)}.ac.a-card.a .in{border-color:var(--ink);box-shadow:inset 12px 0 0 var(--a5)}.ac.a-card.r .in{border-color:var(--ink)}
.ac.a-fr .in{border:2.8px dashed var(--ink);border-radius:16px;background:none}.ac.a-fr .in span{background:var(--ink);color:var(--paper);border-radius:999px}
.it{border:2.8px solid var(--line);border-radius:16px;box-shadow:none;background:#fff}
.it .bx{border-radius:8px}
.msg.bot{background:#fff;border:2.8px solid var(--line)}
.kin .ln .hl{color:var(--ink);box-shadow:inset 0 -.18em 0 var(--a5)}.kin .ln .stk i{background:var(--ink)}
.kin .kic{background:var(--a5);border-radius:16px}
.dash{position:absolute;left:48px;right:48px;top:1520px;border-top:2.8px dashed var(--line)}
.cap{font-family:var(--sans);font-size:64px;letter-spacing:-.025em;top:1548px;line-height:1.16}
.cap .w{margin:0 .06em;padding:0 .1em;border-radius:10px;color:var(--ink)}.cap .w.on{background:var(--a5);color:var(--ink)}
.end{background:var(--paper);align-items:flex-start;padding:0 90px;gap:28px}
.end .nb{font-weight:800;font-size:170px;letter-spacing:-.055em;line-height:.9}
.end .slog{font-weight:700;font-size:64px;letter-spacing:-.03em;line-height:1.05}
.end .ln2{width:240px;border-top:2.8px dashed var(--ink);margin-top:20px}
.end .site{font-size:44px;line-height:1.25;letter-spacing:-.01em;color:var(--muted);max-width:820px}.end .site b{color:var(--ink);font-weight:700;box-shadow:inset 0 -.18em 0 var(--a5)}
.hk{position:absolute;inset:0;background:var(--ink);color:var(--paper);display:flex;flex-direction:column;justify-content:center;padding:0 80px;z-index:60}
.hk .hl2{font-weight:800;font-size:118px;letter-spacing:-.045em;line-height:1.02}.hk .hl2.s2{font-size:100px}.hk .hl2.s3{font-size:76px}
.hk .hw{display:inline-block;transform-origin:50% 70%}.hk .hw.on{color:var(--a5)}
.hk .bar{position:absolute;left:80px;top:420px;width:180px;height:18px;background:var(--a5);transform-origin:left}
.hk .kick{margin-top:48px;font-family:var(--mono);font-size:30px;letter-spacing:.06em;text-transform:uppercase;color:var(--a5)}
.end .ysq{position:absolute;right:90px;bottom:240px;width:200px;height:144px;border-radius:16px;background:var(--a5)}
'''
s = s.replace('</style></head>', CSS + '</style></head>', 1)
lines = s.split('\n')
a = next(i for i, l in enumerate(lines) if l.startswith('  st.innerHTML=`<div class="top">'))
b = next(i for i in range(a, len(lines)) if lines[i].startswith('  TL=gsap.timeline({paused:true});'))
NEW = '''  st.innerHTML=`<div class="top"><span class="logo">Нэйшн<span class="st">ai-nation.ru</span></span><span class="pill">${esc(p.tag||'Мультиагенты')}</span></div>
   <div class="title"><div>${safe(p.title)}</div></div>
   <div class="fr cam"><div class="nm">${esc(p.lector||'Николай Барышников')}${p.org?`<small>${esc(p.org)}</small>`:''}</div></div>
   <div class="fr sld"></div>
   <div class="cover"><span>слайд урока</span></div>
   <div class="pn"></div>
   <div class="dash"></div>
   <div class="cap"></div>
   <div class="end"><div class="nb">Нэйшн</div><div class="slog">Технари новой формации</div><div class="ln2"></div><div class="site">Больше у нас в <b>Telegram-канале</b> — ссылка в профиле</div><div class="ysq"></div></div>`;
  st.style.setProperty('--camy',p.scenes?'260px':'280px');'''
lines[a:b] = NEW.split('\n')
s = '\n'.join(lines)
def rep(old, new):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new, 1)
rep(".from('.nm',{x:-40,opacity:0,duration:.45,ease:'power3.out'},.5);", ".from('.nm',{x:-40,opacity:0,duration:.45,ease:'power3.out'},.21);")
rep("E.querySelectorAll('.s,.h,.b')", "E.querySelectorAll('.nb,.slog,.ln2,.site,.ysq')")
rep("cap.innerHTML=c.words.map(w=>`<span class=\"w ${t>=w.s?'on':''}\">${esc(w.t)}</span>`).join('');",
    "let cur=-1;c.words.forEach((w,i)=>{if(t>=w.s)cur=i});cap.innerHTML=c.words.map((w,i)=>`<span class=\"w ${i===cur?'on':''}\">${esc(w.t)}</span>`).join(' ');")
rep("  window._chunks=p.chunks;TL.seek(0);", """  if(p.hookcard){const h=p.hookcard,d=document.createElement('div');d.className='hk';  // хук-карточка на весь кадр: слова по одному (под звук «поп»), уезжает вверх
    d.innerHTML='<div class="bar"></div>'+h.lines.map(l=>`<div class="hl2 ${l.size?'s'+l.size:''}">${l.words.map(w=>`<span class="hw ${w.hl?'on':''}">${esc(w.t)}</span>`).join(' ')}</div>`).join('')+(h.kick?`<div class="kick">${esc(h.kick.t)}</div>`:'');st.appendChild(d);
    const flat=h.lines.flatMap(l=>l.words);const ws=[...d.querySelectorAll('.hw')];TL.set(ws,{autoAlpha:0},0);
    ws.forEach((x,i)=>TL.fromTo(x,{scale:2,autoAlpha:0,rotation:-7},{scale:1,autoAlpha:1,rotation:0,duration:.22,ease:'back.out(2.4)',immediateRender:false},flat[i].at));
    TL.fromTo(d.querySelector('.bar'),{scaleX:0},{scaleX:1,duration:.3,ease:'power3.out'},flat[0].at);
    if(h.kick){TL.set(d.querySelector('.kick'),{autoAlpha:0},0).to(d.querySelector('.kick'),{autoAlpha:1,duration:.2},h.kick.at)}
    TL.set(d,{yPercent:0},0).to(d,{yPercent:-100,duration:.28,ease:'power3.in'},h.out-.28);}
  window._chunks=p.chunks;TL.seek(0);""")
open(D + '/nation_motion.html', 'w', encoding='utf-8').write(s)
print('ok', len(s))
