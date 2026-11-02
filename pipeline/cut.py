#!/usr/bin/env python3
"""Монтажный лист: выбранные дубли → точные куски без пауз и взгляда мимо камеры.

cut.py <takes.json> <words.json> <silence.json> <gaze.json|-> <out edl.json>

takes.json — решение редактора (Claude или человек), какие куски исходника берём и в каком порядке:
  {"fps":25, "tc_start":23776, "opener_after": 0 | null, "opener_gap": 4.0,
   "segments":[{"in":595.0,"out":605.45,"tag":"cold"}, {"in":22.1,"out":28.7,"tag":"main"}, ...]}
words.json — Groq verbose_json с words; silence.json — [[start,end],...] тишина по звуку (signals.py);
gaze.json — выход gaze.py (или «-», если проверки взгляда нет).

Правила (docs/STANDARD.md):
- паузы между словами > 0,35 с ужимаются до ~0,2 с; тишина по звуку > 0,9 с вырезается всегда;
- взгляд мимо камеры ≥ 0,5 с: если в это время нет речи — вырезаем; если речь есть — кусок остаётся,
  но попадает в "covers": его обязательно закрыть визуалом (вырезка, B-roll, графика), иначе проверка не пройдёт;
- кусок короче 0,5 с выбрасывается; на каждой склейке план чередуется 1.0 / 1.12 (кроп), кроме коротких кусков.
"""
import sys, json
takes, words_p, sil_p, gaze_p, out = sys.argv[1:6]
T = json.load(open(takes)); FPS = T.get('fps', 25)
W = json.load(open(words_p))['words']
SIL = json.load(open(sil_p))
AWAY = json.load(open(gaze_p))['away'] if gaze_p != '-' else []
fr = lambda t: round(t * FPS) / FPS

def speech_in(a, b):
    return [w for w in W if w['start'] < b and w['end'] > a]

def split(a, b):
    ws = [w for w in W if a - 0.05 <= w['start'] < b]
    cuts = []
    for x, y in zip(ws, ws[1:]):                       # паузы по словам
        if y['start'] - x['end'] > 0.35:
            cuts.append((x['end'] + 0.1, y['start'] - 0.1))
    for sa, sb in SIL:                                  # тишина по звуку
        lo, hi = max(sa, a), min(sb, b)
        if hi - lo > 0.9: cuts.append((lo + 0.2, hi - 0.12))
    for ga, gb in AWAY:                                 # взгляд мимо без речи
        lo, hi = max(ga, a), min(gb, b)
        if hi - lo >= 0.5 and not speech_in(lo, hi): cuts.append((lo, hi))
    cuts = sorted(c for c in cuts if c[1] - c[0] > 0.05)
    merged = []
    for c in cuts:
        if merged and c[0] <= merged[-1][1]: merged[-1] = (merged[-1][0], max(merged[-1][1], c[1]))
        else: merged.append(c)
    res, cur = [], a
    for c0, c1 in merged:
        if c0 > cur: res.append((cur, c0))
        cur = max(cur, c1)
    res.append((cur, b))
    return [(fr(p), fr(q)) for p, q in res if q - p >= 0.5]

edl, covers, rec = [], [], 0.0
gap_at = None
for i, s in enumerate(T['segments']):
    if T.get('opener_after') is not None and i == T['opener_after'] and gap_at is None:
        gap_at = fr(rec); rec += T.get('opener_gap', 4.0)
    for p, q in split(s['in'], s['out']):
        edl.append({'src_in': p, 'src_out': q, 'rec': fr(rec), 'tag': s.get('tag', 'main')})
        for ga, gb in AWAY:
            lo, hi = max(ga, p), min(gb, q)
            if hi - lo >= 0.5 and speech_in(lo, hi):
                covers.append({'rec_in': fr(rec + lo - p), 'rec_out': fr(rec + hi - p), 'src_in': lo, 'src_out': hi})
        rec += q - p
if T.get('opener_after') == len(T['segments']) and gap_at is None:
    gap_at = fr(rec); rec += T.get('opener_gap', 4.0)
for i, e in enumerate(edl):
    e['scale'] = 1.0 if i % 2 == 0 or e['src_out'] - e['src_in'] < 2 else 1.12
src_len = sum(s['out'] - s['in'] for s in T['segments'])
json.dump({'fps': FPS, 'tc_start': T.get('tc_start', 0), 'total': fr(rec), 'gap_at': gap_at,
           'gap': T.get('opener_gap', 4.0) if gap_at is not None else 0, 'edl': edl, 'covers': covers},
          open(out, 'w'), ensure_ascii=False, indent=1)
print(f'кусков {len(edl)}, длина {int(rec//60)}:{rec%60:04.1f}, вырезано {100*(1-(rec-(T.get("opener_gap",4) if gap_at is not None else 0))/src_len):.0f}% от выбранного, закрыть визуалом: {len(covers)}')
for c in covers: print(f"  закрыть {c['rec_in']:.1f}–{c['rec_out']:.1f} (взгляд мимо камеры во время речи)")
