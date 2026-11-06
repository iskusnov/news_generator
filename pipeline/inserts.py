#!/usr/bin/env python3
"""Врезки-ролики в монтаж «с паузой» (спецвыпуск 06.11): ведущий замолкает, на весь кадр идёт ролик со своим звуком.

inserts.py <edl.json> <inserts.json>  → тот же edl.json с элементами {"clip": файл, "ss", "dur", "rec"} и сдвинутым rec.
Запускать ПОСЛЕ speed.py (ролики не ускоряются). inserts.json: [{"after": t_src, "clip": "meta_muse.mp4", "ss": 3.0, "dur": 8.0,
  "vol": 0.8, "label": "AI at Meta · X"}] — ролик встаёт сразу после куска, в который попадает t_src (конец куска).
mac_final.py рендерит такой кусок из папки media/ задания: вписать в 4K (вертикальный — поверх размытой копии), звук ролика.
specs_build.s2r куски с clip пропускает (src_in = -1)."""
import sys, json
p, ip = sys.argv[1:3]
E = json.load(open(p)); I = sorted(json.load(open(ip)), key=lambda x: x['after']); FPS = E.get('fps', 25)
fr = lambda x: round(x * FPS) / FPS
E['edl'] = [e for e in E['edl'] if not e.get('clip')]
out = []
for e in E['edl']:
    out.append(e)
    for x in I:
        if e['src_in'] - 0.05 <= x['after'] <= e['src_out'] + 0.05 and not x.get('_done'):
            out.append(dict(clip=x['clip'], ss=x.get('ss', 0), dur=x['dur'], vol=x.get('vol', 0.8), label=x.get('label', ''),
                            src_in=-1, src_out=-1, fit=x.get('fit', 'auto'))); x['_done'] = True
miss = [x['after'] for x in I if not x.get('_done')]
assert not miss, f'нет куска для врезок {miss}'
rec, shift, gap_done = 0.0, 0.0, False
for e in out:
    if E.get('gap_at') is not None and not gap_done and e is not out[0] and e.get('rec', 0) >= E['gap_at'] - 1e-6 and not e.get('clip'):
        pass
    e['rec'] = fr(rec) if e.get('clip') else fr(e['rec'] + shift)
    if e.get('clip'): shift += fr(e['dur'])
    rec = e['rec'] + (fr(e['dur']) if e.get('clip') else round((e['src_out'] - e['src_in']) / e.get('speed', 1.0) * FPS) / FPS)
E['edl'] = out; E['total'] = fr(E['total'] + shift)
json.dump(E, open(p, 'w'), ensure_ascii=False, indent=1)
print(f'врезок {len(I)}, +{shift:.1f} с, итог {int(E["total"] // 60)}:{E["total"] % 60:04.1f}')
