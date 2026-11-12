(()=>{
// Рендер кадров Нэйшн: window.SPEC = {type, ...}
const R={dev:'var(--role-dev)',qa:'var(--role-qa)',ba:'var(--role-ba)',pm:'var(--role-pm)',mkt:'var(--role-mkt)',lead:'var(--role-lead)'};
const RN={dev:'Разработка',qa:'Тестирование',ba:'Аналитика',pm:'Продукт',mkt:'Маркетинг и рост',lead:'Лиды и CTO'};
const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;');
const person=(src,role,size)=>`<div class="person" style="width:${size}px;height:${size}px">${src?`<img src="${src}">`:''}${role?`<i class="role" style="background:${R[role]}"></i>`:''}</div>`;
const T={
intro:s=>`<div class="paper"></div>
<div style="position:absolute;left:144px;top:120px" class="tag"><span class="num">${esc(s.num)}</span><span class="mono">Урок</span></div>
<div style="position:absolute;left:144px;top:300px;width:900px"><h1 style="font-size:150px">${esc(s.title)}</h1>
<div style="margin-top:44px;font-size:32px;color:var(--mut);line-height:1.4">${esc(s.sub)}</div></div>
<div id="ph" style="position:absolute;left:1120px;top:200px">${person(s.photo,s.role,400)}</div>
<div style="position:absolute;left:1120px;top:628px" class="rolelab"><i style="background:${R[s.role]}"></i>${RN[s.role]} · <span style="color:var(--mut)">${esc(s.lector)}</span></div>
${(s.skills||[]).map((k,i)=>`<div class="skill" data-link="ph" style="position:absolute;left:${[1640,1660,1640][i]}px;top:${[190,380,570][i]}px">${esc(k)}</div>`).join('')}
<svg class="edges" viewBox="0 0 1920 1080"></svg>
<div class="foot"><b>Нэйшн</b><span class="dash"></span><span>Технари новой формации</span></div>`,
screen:s=>`<div class="ink"></div>
<div style="position:absolute;left:32px;top:80px;width:1504px;height:846px;border-radius:16px;overflow:hidden;background:#000">${s.shot?`<img src="${s.shot}" style="width:100%;height:100%;object-fit:contain">`:''}</div>
<div style="position:absolute;left:1568px;top:80px">${person(s.photo,s.role,320)}</div>
<div style="position:absolute;left:1568px;top:420px;color:var(--paper);font-weight:700;font-size:30px;line-height:1.15;width:320px">${esc(s.lector)}</div>
<div style="position:absolute;left:1568px;top:498px;color:var(--paper)" class="rolelab"><i style="background:${R[s.role]}"></i>${RN[s.role]}</div>
<div style="position:absolute;left:1568px;top:668px;color:var(--paper)" class="tag"><span class="num y">${esc(s.ch)}</span><span class="mono" style="font-size:18px;color:#A8AAB0">глава</span></div>
<div style="position:absolute;left:1568px;top:724px;color:var(--paper);font-weight:700;font-size:30px;line-height:1.2;width:320px">${esc(s.chTitle)}</div>
<div style="position:absolute;left:1568px;top:${s.chTitle.length>18?838:808}px;width:320px;height:6px;border-radius:3px;background:#3A3C42"><div style="width:${Math.round((s.progress||0)*100)}%;height:100%;border-radius:3px;background:var(--yel)"></div></div>
<div style="position:absolute;left:32px;top:966px;right:32px;display:flex;align-items:center;gap:20px;color:#A8AAB0" class="mono"><b style="color:var(--paper)">Нэйшн</b> · Урок ${esc(s.num)} · ${esc(s.topic)}</div>`,
chapter:s=>`<div class="paper"></div>
<div style="position:absolute;left:144px;top:96px;right:144px;display:flex;gap:12px">${Array.from({length:s.total},(_,i)=>`<div style="flex:1;height:8px;border-radius:4px;background:${i<s.n?'var(--ink)':'var(--line)'}"></div>`).join('')}</div>
<div style="position:absolute;left:144px;top:330px;font-family:var(--fm);font-weight:700;font-size:200px;line-height:1">${String(s.n).padStart(2,'0')}</div>
<div style="position:absolute;left:144px;top:570px;width:1300px"><h1 style="font-size:104px">${esc(s.title)}</h1>
${s.sub?`<div style="margin-top:32px;font-size:32px;color:var(--mut);width:1100px">${esc(s.sub)}</div>`:''}</div>
<div style="position:absolute;right:144px;bottom:120px;width:200px;height:144px;border-radius:16px;background:var(--yel)"></div>`,
frame:s=>`<div class="ink"></div>
<div style="position:absolute;left:32px;top:80px;width:1504px;height:846px;border-radius:16px;background:#000"></div>
<div style="position:absolute;left:1568px;top:80px;width:320px;height:320px;border-radius:8px;background:#26282E"></div>
<div style="position:absolute;left:1568px;top:420px;width:320px;color:var(--paper)">
<div style="font-weight:700;font-size:30px;line-height:1.15">${esc(s.lector)}</div>
<div style="margin-top:14px" class="rolelab"><i style="background:${R[s.role]}"></i>${esc(s.org||RN[s.role])}</div></div>
<div style="position:absolute;left:1568px;top:560px;width:320px;height:330px;color:var(--paper);display:flex;flex-direction:column;gap:16px">
<div class="mono" style="font-size:17px;color:#A8AAB0">${esc(s.part)}</div>
<div class="tag"><span class="num y">${esc(s.ch)}</span><span class="mono" style="font-size:17px;color:#A8AAB0">глава</span></div>
<div style="font-weight:700;font-size:${s.chTitle.length>40?25:28}px;line-height:1.2;text-wrap:balance">${esc(s.chTitle)}</div></div>
<div style="position:absolute;left:1568px;top:906px;width:320px;height:6px;border-radius:3px;background:#3A3C42"><div style="width:${Math.round((s.progress||0)*100)}%;height:100%;border-radius:3px;background:var(--paper)"></div></div>
<div style="position:absolute;left:32px;top:966px;right:32px;display:flex;align-items:center;gap:14px;color:#A8AAB0" class="mono"><b style="color:var(--paper)">Нэйшн</b> · AI Bootcamp · 3 поток · Урок ${esc(s.num)} · ${esc(s.topic)}</div>`,
roletop:s=>`<i style="position:absolute;left:1568px;top:${80+320-56}px;width:56px;height:56px;background:${R[s.role]}"></i>`,
qside:s=>`<div style="position:absolute;left:1568px;top:80px;width:320px;height:320px;border-radius:8px;background:var(--warm);display:grid;place-items:center">
<svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="#15161A" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/><path d="M10 9.2a2 2 0 1 1 2.6 1.9c-.4.2-.6.5-.6.9v.4"/><path d="M12 14.2h.01"/></svg></div>
<div style="position:absolute;left:1568px;top:404px;width:320px;height:120px;background:var(--ink);color:var(--paper)">
<div style="margin-top:16px;font-weight:700;font-size:30px;line-height:1.15">${esc(s.label||'Вопрос из зала')}</div>
<div style="margin-top:14px;color:#A8AAB0;font-size:18px" class="mono">${esc(s.sub||'Участник потока')}</div></div>`,
side:s=>`<div style="position:absolute;left:1552px;top:548px;width:352px;height:384px;border-radius:16px;background:var(--paper);padding:24px 24px;display:flex;flex-direction:column;gap:14px">
<div class="tag"><span class="num">${esc(s.kind)}</span></div>
${s.term?`<div style="font-weight:800;font-size:32px;line-height:1.05;letter-spacing:-.02em">${esc(s.term)}</div>`:''}
<div style="font-weight:${s.term?500:700};font-size:${s.term?22:(s.text.length>90?24:27)}px;line-height:1.3;color:var(--ink)">${s.term?'':'«'}${esc(s.text)}${s.term?'':'»'}</div>
${s.who?`<div class="mono" style="font-size:16px;color:var(--mut);margin-top:auto">${esc(s.who)}</div>`:''}</div>`,
speaker:s=>`<div style="position:absolute;left:96px;bottom:96px;display:flex;align-items:stretch;background:var(--paper);border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.25)">
<div style="width:20px;background:${R[s.role]}"></div>
<div style="padding:26px 40px 28px 32px"><div style="font-weight:800;font-size:52px;letter-spacing:-.03em;line-height:1">${esc(s.lector)}</div>
<div style="margin-top:16px" class="rolelab"><i style="background:${R[s.role]}"></i>${esc(s.org||RN[s.role])}${s.sub?` · <span style="color:var(--mut)">${esc(s.sub)}</span>`:''}</div></div></div>`,
hw:s=>`<div class="paper"></div>
<div style="position:absolute;left:144px;top:110px" class="tag"><span class="num y">ДЗ</span><span class="mono">Домашнее задание · урок ${esc(s.num)}</span></div>
<div style="position:absolute;left:144px;top:220px;width:1100px"><h1 style="font-size:92px">${esc(s.title)}</h1>
<div style="margin-top:36px;font-size:32px;line-height:1.4;color:var(--ink)">${esc(s.text)}</div></div>
<div style="position:absolute;left:1340px;top:220px;width:440px;display:flex;flex-direction:column;gap:18px">
<div class="mono" style="color:var(--mut)">Держите в голове</div>
${(s.items||[]).map((k,i)=>`<div style="display:flex;gap:16px;align-items:flex-start;background:var(--white);border-radius:16px;padding:20px 22px"><span class="num">${String(i+1).padStart(2,'0')}</span><span style="font-size:24px;line-height:1.3;font-weight:600">${esc(k)}</span></div>`).join('')}</div>
<div class="foot"><b>Нэйшн</b><span class="dash"></span><span>${esc(s.foot)}</span></div>`,
end:s=>`<div class="ink"></div>
<div style="position:absolute;left:144px;top:330px;color:var(--paper)"><div class="mono" style="color:#A8AAB0">Урок ${esc(s.num)} · ${esc(s.topic)}</div>
<h1 style="font-size:150px;margin-top:30px">${esc(s.title)}</h1>
<div style="margin-top:40px;font-size:32px;color:#C9CBD0;width:1200px;line-height:1.4">${esc(s.text)}</div></div>
<div style="position:absolute;right:144px;bottom:120px;width:200px;height:144px;border-radius:16px;background:var(--yel)"></div>
<div class="foot" style="color:var(--paper)"><b>Нэйшн</b><span class="dash" style="border-color:var(--paper)"></span><span>Технари новой формации</span></div>`,
question:s=>`<div class="paper"></div>
<div style="position:absolute;left:144px;top:120px;display:flex;gap:16px;align-items:center" class="mono"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#15161A" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/></svg>${esc(s.src)}</div>
<div style="position:absolute;left:144px;top:270px">${s.photo?person(s.photo,s.role,240):`<div style="width:240px;height:240px;border-radius:8px;background:var(--warm);display:grid;place-items:center;font-weight:800;font-size:84px;color:var(--mut)">${esc(s.initials)}</div>`}</div>
<div style="position:absolute;left:440px;top:262px;width:1330px"><div style="font-weight:800;font-size:68px;line-height:1.08;letter-spacing:-.03em;text-wrap:balance">«${esc(s.q)}»</div>
<div style="margin-top:28px" class="rolelab">${s.role?`<i style="background:${R[s.role]}"></i>${RN[s.role]} · `:''}<span style="color:var(--mut)">${esc(s.who)}</span></div></div>
<div style="position:absolute;left:144px;bottom:120px;display:flex;gap:16px">${(s.skills||[]).map(k=>`<span class="skill">${esc(k)}</span>`).join('')}</div>`,
};
document.body.innerHTML=T[window.SPEC.type](window.SPEC);
const sv=document.querySelector('svg.edges');
if(sv)document.querySelectorAll('[data-link]').forEach(el=>{const a=document.getElementById(el.dataset.link).getBoundingClientRect(),b=el.getBoundingClientRect();
const bx=b.left+b.width/2,by=b.top+b.height/2;const ax=Math.min(Math.max(bx,a.left),a.right),ay=Math.min(Math.max(by,a.top),a.bottom);
const tx=bx<a.left?b.right:bx>a.right?b.left:bx,ty=by<a.top?b.bottom:by>a.bottom?b.top:by;
const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',`M${ax} ${ay} L${tx} ${ty}`);sv.appendChild(p);});

})();