#!/usr/bin/env python3
"""Ускорение речи (решение Антона 04.11): speed.py <edl.json> <words.json> [--speed X] → тот же edl.json с полем speed и пересчитанным rec.

Темп подбирается автоматически по слогам в секунду внутри взятых кусков: цель — темп выпуска 04.11 на ×1.15
(5,37 слога/с × 1,15 ≈ 6,17), результат зажат в 1,10–1,15 (выше — моргание выглядит дёргано).
Ускоряются только куски с ведущим (mac_final.py: setpts + atempo по куску); интро-пауза gap, плашки, бегущая строка
и отбивка накладываются уже на ускоренную склейку и идут с обычной скоростью. Время плашек считать от НОВОГО rec:
rec + (t_src − src_in) / speed (specs_build.s2r).
"""
import sys, json, re
REF, LO, HI = 5.37 * 1.15, 1.10, 1.15
p, wp = sys.argv[1], sys.argv[2]
E = json.load(open(p)); W = json.load(open(wp))['words']
V = re.compile('[аеёиоуыэюяaeiouy]', re.I)
syl = t = 0.0
for e in E['edl']:
    if e.get('src_in', 0) >= 1000: continue
    syl += sum(len(V.findall(w['word'])) for w in W if e['src_in'] <= w['start'] < e['src_out']); t += e['src_out'] - e['src_in']
rate = syl / t if t else REF / 1.15
s = float(sys.argv[sys.argv.index('--speed') + 1]) if '--speed' in sys.argv else round(min(HI, max(LO, REF / rate)), 2)
fr = lambda x: round(x * E.get('fps', 25)) / E.get('fps', 25)
rec, gap_done = 0.0, False
for e in E['edl']:
    if E.get('gap_at') is not None and not gap_done and e['rec'] >= E['gap_at'] - 1e-6:
        E['gap_at'] = fr(rec); rec += E['gap']; gap_done = True
    e['speed'] = s; e['rec'] = fr(rec)
    rec += round((e['src_out'] - e['src_in']) / s * E.get('fps', 25)) / E.get('fps', 25)
E['speed'] = s; E['total'] = fr(rec); E['rate_syl_s'] = round(rate, 2)
json.dump(E, open(p, 'w'), ensure_ascii=False, indent=1)
print(f'темп {rate:.2f} слога/с → ускорение ×{s}, длина {int(rec // 60)}:{rec % 60:04.1f}')
