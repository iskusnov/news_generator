#!/usr/bin/env python3
"""Задание финального рендера выпуска для службы на Mac (~/PokaTySpal/queue).

mac_final.py <edl.json> <specs.json> <crawl.json> <src.mov на Mac> <папка задания на Mac> <выход .mp4 на Mac> > job.sh
В папке задания лежат: intro.mp4 (4K, со звуком), gfx/<id>.webm (VP9 с альфой, 1920×1080), crawl.png + crawl_label.png (1x).
Шаги (нативный ffmpeg, VideoToolbox):
 1) каждый кусок исходника: ровно N кадров + столько же звука (PCM, apad, -t), кроп ×scale, HEVC 4K;
 2) интро обрезано до gap, тем же кодеком; склейка concat без перекодирования;
 3) плашки поверх (масштаб ×2), бегущая строка, стоп-кадр под финальную карточку, громкость −14 LUFS.
crawl.json: {"from": rec_с, "to": rec_с, "cycle": ширина цикла в px (1x), "speed": px/с (1x)}
"""
import sys, json, shlex
edl_p, specs_p, crawl_p, SRC, JD, OUT = sys.argv[1:7]
E = json.load(open(edl_p)); S = json.load(open(specs_p)); C = json.load(open(crawl_p))
FPS = 25; TAIL = max(0.0, max(s['rec'] + s['dur'] for s in S) - E['total'])
q = shlex.quote
V = '-c:v hevc_videotoolbox -b:v 45M -tag:v hvc1 -pix_fmt yuv420p'
A = '-c:a pcm_s16le -ar 48000 -ac 2'
L = ['#!/bin/bash', 'set -e', 'export PATH=/opt/homebrew/bin:$PATH', f'JD={q(JD)}; mkdir -p "$JD/parts" "$JD/gfx"; cd "$JD"',
     'echo "start $(date +%T)"']
parts = []
gap_done = False
for i, e in enumerate(E['edl']):
    if E.get('gap_at') is not None and not gap_done and e['rec'] >= E['gap_at'] - 1e-6:
        nf = round(E['gap'] * FPS)
        L.append(f'[ -s parts/intro.mov ] || ffmpeg -v error -y -i intro.mp4 -frames:v {nf} -vf fps=25,scale=3840:2160,format=yuv420p {V} '
                 f'-af apad -t {nf/FPS:.3f} {A} parts/intro.mov')
        parts.append('parts/intro.mov'); gap_done = True
    d = e['src_out'] - e['src_in']; nf = round(d * FPS); k = e.get('scale', 1.0)
    w, h = int(3840 / k) // 2 * 2, int(2160 / k) // 2 * 2
    x, y = (3840 - w) // 2, 0 if k == 1.0 else int((2160 - h) * 0.35)
    p = f'parts/p{i:03d}_{e["src_in"]:.2f}_{nf}_{k}.mov'
    parts.append(p)
    L.append(f'[ -s {p} ] || ffmpeg -v error -y -ss {e["src_in"]:.3f} -i {q(SRC)} -frames:v {nf} '
             f'-vf crop={w}:{h}:{x}:{y},scale=3840:2160,fps=25,setsar=1,format=yuv420p {V} '
             f'-af afade=t=in:d=0.015,afade=t=out:st={max(0, nf/FPS - 0.015):.3f}:d=0.015,apad -t {nf/FPS:.3f} {A} {p}')
L.append('echo "parts $(date +%T)"')
L.append("printf '%s\\n' " + ' '.join(q(f"file '{p.split('/')[-1]}'") for p in parts) + ' > parts/list.txt')
L.append('ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy base.mov')
L.append('echo "base $(date +%T)"')
ins = ['-i', 'base.mov', '-loop', '1', '-i', 'crawl.png', '-loop', '1', '-i', 'crawl_label.png']
fc = [f'[0:v]tpad=stop_mode=clone:stop_duration={TAIL:.2f}[v0]',
      '[1:v]scale=iw*2:ih*2,format=rgba[cr]', '[2:v]scale=iw*2:ih*2,format=rgba[lb]',
      f"[v0][cr]overlay=x='-mod(t*{C['speed']*2}\\,{C['cycle']*2})':y=H-h:shortest=0:enable='between(t,{C['from']:.2f},{C['to']:.2f})'[v1]",
      f"[v1][lb]overlay=x=0:y=H-h:enable='between(t,{C['from']:.2f},{C['to']:.2f})'[v2]"]
cur = 'v2'
for j, s in enumerate(S, 3):
    ins += ['-c:v', 'libvpx-vp9', '-i', f"gfx/{s['id']}.webm"]
    fc.append(f"[{j}:v]scale=3840:2160,format=yuva420p,setpts=PTS-STARTPTS+{s['rec']:.2f}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass:enable='between(t,{s['rec']:.2f},{s['rec'] + s['dur']:.2f})'[w{j}]")
    cur = f'w{j}'
fc.append('[0:a]apad,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
total = E['total'] + TAIL
cmd = ['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-map', '[a]',
       '-c:v', 'hevc_videotoolbox', '-b:v', '30M', '-tag:v', 'hvc1', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
       '-t', f'{total:.2f}', '-movflags', '+faststart', 'final_tmp.mp4']
L.append(' '.join(q(c) for c in cmd))
L.append(f'mv final_tmp.mp4 {q(OUT)} && echo "DONE $(date +%T) {OUT}"')
print('\n'.join(L))
