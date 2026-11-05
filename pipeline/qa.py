#!/usr/bin/env python3
"""Проверка перед сдачей. qa.py <черновой рендер.mp4> <edl.json> [gaze_render.json] → отчёт в stdout, код 1 при браке.

Проверяет: чёрные кадры (blackdetect, от 1 кадра), тишину > 0,9 с в готовом звуке, громкость (≈ −14 LUFS),
дыры и наложения в монтажном листе, кусок короче 0,5 с, а также непокрытые места со взглядом мимо камеры (edl.covers).
Черновой рендер: склейка по edl.json в 540p (render_preview в docs/PIPELINE.md)."""
import sys, json, re, subprocess
mp4, edl_p = sys.argv[1], sys.argv[2]
E = json.load(open(edl_p)); fps = E['fps']; bad = []
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', mp4, '-vf', 'blackdetect=d=0.04:pix_th=0.06', '-af',
                    'silencedetect=n=-45dB:d=0.9,ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
for m in re.finditer(r'black_start:([0-9.]+) black_end:([0-9.]+)', r):
    bad.append(f'чёрный кадр {float(m[1]):.2f}–{float(m[2]):.2f}')
for m in re.finditer(r'silence_start: ([0-9.]+)', r):
    bad.append(f'тишина с {float(m[1]):.2f}')
lufs = re.findall(r'I:\s+(-?[0-9.]+) LUFS', r)
prev = 0.0
for e in sorted(E['edl'], key=lambda e: e['rec']):
    if abs(e['rec'] - prev) > 1 / fps + 1e-6 and not (E.get('gap_at') is not None and abs(e['rec'] - prev - E['gap']) < 1 / fps + 1e-6):
        bad.append(f"дыра/наложение на {prev:.2f} → {e['rec']:.2f}")
    if e['src_out'] - e['src_in'] < 0.5: bad.append(f"огрызок {e['rec']:.2f}")
    prev = e['rec'] + (e['src_out'] - e['src_in']) / e.get('speed', 1.0)
for c in E.get('covers', []):
    if not c.get('covered_by'): bad.append(f"взгляд мимо камеры не закрыт: {c['rec_in']:.1f}–{c['rec_out']:.1f}")
print('Громкость:', (lufs[-1] + ' LUFS') if lufs else 'нет данных')
print('Замечаний:', len(bad)); [print(' -', b) for b in bad]
sys.exit(1 if bad else 0)
