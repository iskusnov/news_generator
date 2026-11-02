#!/usr/bin/env python3
"""Тишина по звуку: signals.py <аудио или видео> <out silence.json> [порог_дБ=-38] [мин_длина=0.3]
Пишет [[start,end],...] в секундах исходника. Нужен ffmpeg."""
import sys, json, re, subprocess
src, out = sys.argv[1], sys.argv[2]
db = sys.argv[3] if len(sys.argv) > 3 else '-38'
d = sys.argv[4] if len(sys.argv) > 4 else '0.3'
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-vn', '-af', f'silencedetect=n={db}dB:d={d}', '-f', 'null', '-'],
                   capture_output=True, text=True)
st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', r.stderr)]
en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', r.stderr)]
pairs = [[round(a, 3), round(b, 3)] for a, b in zip(st, en)]
json.dump(pairs, open(out, 'w'))
print('пауз', len(pairs), 'длиннее 0,9 с:', sum(1 for a, b in pairs if b - a > 0.9))
