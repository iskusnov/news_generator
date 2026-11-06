#!/usr/bin/env python3
"""Монтажный лист урока буткемпа: паузы (код) + смысловые вырезки (решение Claude) → edl.json + CSV для людей.

lesson_edl.py <silence_cut.json> <words.json> <semantic.json> <длительность_с> <out edl.json> <out montazh.csv>
silence_cut.json — signals.py audio.m4a silence_cut.json -35 1.2 (тишина > 1,2 с при −35 дБ).
semantic.json — [{"from": с, "to": с, "why": "причина"}] — ожидание, перерывы, тех. заминки, прощания (содержание не режем).
Пауза сокращается до KEEP=0,5 с (по 0,25 с остаётся с каждой стороны). Склейки только внутри тишины (по звуку) — посреди слова не режем:
если в вырезаемый кусок целиком попадает слово из words.json (кроме галлюцинаций Whisper), пауза пропускается.
edl.json: {"edl": [{"src_in", "src_out", "rec"}], "total", "src_total", "cuts": [...]} — rec = время в итоговом ролике.

lesson_edl.py tc <edl.json> <пре-ролл_с> <in.md> <out.md> — пересчитать таймкоды «▶ ЧЧ:ММ:СС» и «`ЧЧ:ММ:СС`» из времени
исходной записи во время итогового видео (пре-ролл + склейки). Время внутри вырезанного куска → начало следующего куска.
"""
import sys, json, csv, re, bisect

def s2r(E, t, pre=0.0):
    ins = [e['src_in'] for e in E]; i = bisect.bisect_right(ins, t) - 1
    if i < 0: return pre
    e = E[i]
    sp = e.get('speed', 1.0)  # после pipeline/speed.py
    if t <= e['src_out']: return pre + e['rec'] + (t - e['src_in']) / sp
    return pre + (E[i + 1]['rec'] if i + 1 < len(E) else e['rec'] + (e['src_out'] - e['src_in']) / sp)

if sys.argv[1] == 'tc':
    E = json.load(open(sys.argv[2]))['edl']; pre = float(sys.argv[3]); s = open(sys.argv[4], encoding='utf-8').read()
    def f(m):
        r = int(round(s2r(E, int(m[2]) * 3600 + int(m[3]) * 60 + int(m[4]), pre)))
        return f'{m[1]}{r // 3600:02d}:{r % 3600 // 60:02d}:{r % 60:02d}'
    out = re.sub(r'(▶ |`)(\d\d):(\d\d):(\d\d)', f, s)
    open(sys.argv[5], 'w', encoding='utf-8').write(out); print('таймкодов', len(re.findall(r'▶ \d\d:', out))); sys.exit()
sil_p, words_p, sem_p, dur, edl_p, csv_p = sys.argv[1:7]
dur = float(dur); KEEP = 0.5
W = json.load(open(words_p))['words']; SEM = json.load(open(sem_p)); SIL = json.load(open(sil_p))
hms = lambda t: f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:04.1f}'
BAD = ('Продолжение', 'следует', 'Субтитры', 'Спасибо за просмотр')
# края слов Whisper «размазывает» на тишину — режем по звуку; пропускаем паузу, только если слово целиком внутри (не галлюцинация)
def words_in(a, b): return [w for w in W if w['start'] >= a and w['end'] <= b and not any(x in w['word'] for x in BAD)]
def before(t, n=8): return ' '.join([w['word'] for w in W if w['end'] <= t + 0.05][-n:])
def after(t, n=8): return ' '.join([w['word'] for w in W if w['start'] >= t - 0.05][:n])
cuts = [dict(a=s['from'], b=s['to'], kind='Смысловой', why=s['why']) for s in SEM]
inside = lambda a, b: any(c['a'] - 0.01 <= a and b <= c['b'] + 0.01 for c in cuts)
skipped = 0
for x, y in SIL:
    a, b = x + KEEP / 2, y - KEEP / 2
    if b - a < 0.3 or inside(a, b): continue
    if words_in(a, b): skipped += 1; continue
    cuts.append(dict(a=a, b=b, kind='Пауза', why=f'Тишина {y - x:.1f} с, оставлено 0,5 с'.replace('.', ',', 1)))
cuts.sort(key=lambda c: c['a'])
merged = []
for c in cuts:  # пауза, задевающая смысловой кусок, сливается с ним
    if merged and c['a'] <= merged[-1]['b'] + 0.05:
        m = merged[-1]; m['b'] = max(m['b'], c['b'])
        if c['kind'] == 'Смысловой': m['kind'], m['why'] = 'Смысловой', c['why']
    else: merged.append(dict(c))
edl, t, rec = [], 0.0, 0.0
for c in merged:
    if c['a'] - t > 0.04: edl.append(dict(src_in=round(t, 3), src_out=round(c['a'], 3), rec=round(rec, 3))); rec += c['a'] - t
    t = max(t, c['b'])
if dur - t > 0.04: edl.append(dict(src_in=round(t, 3), src_out=round(dur, 3), rec=round(rec, 3))); rec += dur - t
json.dump(dict(edl=edl, total=round(rec, 3), src_total=dur, cuts=merged), open(edl_p, 'w'), ensure_ascii=False, indent=0)
with open(csv_p, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['№', 'Тип', 'Вырезать с', 'Вырезать по', 'Сек', 'До склейки (конец фразы)', 'После склейки (начало фразы)', 'Причина'])
    for i, c in enumerate(merged, 1):
        w.writerow([i, c['kind'], hms(c['a']), hms(min(c['b'], dur)), f"{min(c['b'], dur) - c['a']:.1f}", before(c['a']), after(c['b']), c['why']])
n = lambda k: [c for c in merged if c['kind'] == k]
print(f"пауз {len(n('Пауза'))} ({sum(c['b'] - c['a'] for c in n('Пауза')) / 60:.1f} мин), смысловых {len(n('Смысловой'))} "
      f"({sum(min(c['b'], dur) - c['a'] for c in n('Смысловой')) / 60:.1f} мин), пропущено пауз со словами {skipped}; "
      f"{hms(dur)} → {hms(rec)}, кусков {len(edl)}")
