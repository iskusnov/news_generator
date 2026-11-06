#!/usr/bin/env python3
"""Распознавание длинной записи по словам (Groq whisper-large-v3), куски по тишине 15–35 с, параллельно.

groq_words.py <аудио.m4a> <silence.json> <смещение_с> <out words.json> --key <файл ключа>
silence.json — из signals.py. Смещение — для записи из нескольких файлов (2-й файл = 1000, 3-й = 2000 …).
Галлюцинации Whisper на тишине («Продолжение следует…», «Субтитры сделал…», «Спасибо за просмотр») выкидываются.
Короткие куски дают точные таймкоды слов (на кусках по 30 мин Whisper «размазывает» слова и прячет оговорки).
"""
import json, subprocess, sys, os, tempfile, argparse
from concurrent.futures import ThreadPoolExecutor
ap = argparse.ArgumentParser(); ap.add_argument('audio'); ap.add_argument('sil'); ap.add_argument('off', type=float); ap.add_argument('out'); ap.add_argument('--key', required=True)
a = ap.parse_args(); key = open(a.key).read().strip(); tmp = tempfile.mkdtemp()
sil = json.load(open(a.sil))
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.audio], capture_output=True, text=True).stdout)
cuts = [0.0]
for x, y in sil:
    m = (x + y) / 2
    if y - x >= 0.4 and m - cuts[-1] >= 15: cuts.append(m)
if dur - cuts[-1] < 5: cuts.pop()
cuts.append(dur)
BAD = ('Продолжение следует', 'Субтитры', 'DimaTorzok', 'Спасибо за просмотр')
def job(i):
    s, e = cuts[i], cuts[i + 1]; f = os.path.join(tmp, f'c{i:04d}.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s), '-t', str(e - s), '-i', a.audio, '-c:a', 'aac', '-b:a', '48k', f], check=True)
    d = {}
    for _ in range(4):
        r = subprocess.run(['curl', '-sS', '--max-time', '300', 'https://api.groq.com/openai/v1/audio/transcriptions', '-H', f'Authorization: Bearer {key}',
                            '-F', f'file=@{f}', '-F', 'model=whisper-large-v3', '-F', 'language=ru', '-F', 'response_format=verbose_json',
                            '-F', 'timestamp_granularities[]=word', '-F', 'timestamp_granularities[]=segment', '-F', 'temperature=0'], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            if 'words' in d: break
        except Exception: pass
    # галлюцинации — фразы из нескольких слов («Продолжение следует...»): выкидываем слова внутри таких сегментов
    bad = [(g['start'], g['end']) for g in d.get('segments', []) if any(b in g.get('text', '') for b in BAD)]
    return [{'word': w['word'], 'start': round(w['start'] + s + a.off, 3), 'end': round(w['end'] + s + a.off, 3)} for w in d.get('words', [])
            if not any(b in w['word'] for b in BAD) and not any(x - 0.05 <= w['start'] and w['end'] <= y + 0.05 for x, y in bad)]
W = []
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(job, range(len(cuts) - 1)): W += r
json.dump({'words': W}, open(a.out, 'w'), ensure_ascii=False)
print(a.out, len(cuts) - 1, 'кусков', len(W), 'слов', round(dur, 1), 'с')
