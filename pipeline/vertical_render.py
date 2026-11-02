#!/usr/bin/env python3
"""Сценарий рендера вертикального ролика (Reels/Shorts) на Mac.

vertical_render.py <edl.json> <spec.json> <исходник> <оверлей .webm> <папка b-roll> <выход .mp4> > render.sh
Три шага, чтобы не упираться в память VM (несколько декодеров 4K HEVC сразу VM убивает):
 1) каждый кусок отдельно, ровно N кадров и столько же звука (иначе звук уезжает на склейках): кроп 9:16 (1215×2160, центр X = CX) → 1080×1920, «панч» ×1.12 из edl.scale, фейды звука 15 мс;
 2) склейка кусков без перекодирования (concat demuxer);
 3) b-roll поверх (кроп 9:16, окна из spec.broll) + графика (VP9 с альфой) + громкость −14 LUFS.
Сценарий можно запускать частями: `bash render.sh 1`, `bash render.sh 2`, `bash render.sh 3` (каждая часть < 180 с).
"""
import sys, json, shlex, os
edl_p, spec_p, src, ov, broll_dir, out = sys.argv[1:7]
CX = 1920  # центр лица по горизонтали в кадре 3840
E = json.load(open(edl_p)); S = json.load(open(spec_p))
tag = os.path.splitext(os.path.basename(out))[0]; tmp = f'$HOME/vrtmp/{tag}'  # промежуточное — на локальном диске VM (быстрее, можно удалять)
q = shlex.quote
L = ['#!/bin/bash', 'set -e', f'STEP=${{1:-all}}; mkdir -p {tmp}', 'if [ "$STEP" = all ] || [ "$STEP" = 1 ]; then']
for i, e in enumerate(E['edl']):
    d = e['src_out'] - e['src_in']; k = e.get('scale', 1.0)
    w, h = int(1215 / k) // 2 * 2, int(2160 / k) // 2 * 2
    x = max(0, min(3840 - w, CX - w // 2)); y = 0 if k == 1.0 else int((2160 - h) * 0.35)
    part = f'{tmp}/s{i:02d}.mov'; nf = round(d * 25)
    L.append(f'[ -s {part} ] || {{ ffmpeg -v error -y -ss {e["src_in"]:.3f} -i {q(src)} '
             f'-vf crop={w}:{h}:{x}:{y},scale=1080:1920,setsar=1,fps=25 '
             f'-af afade=t=in:d=0.015,afade=t=out:st={max(0, nf/25 - 0.015):.3f}:d=0.015,apad '
             f'-t {nf/25:.3f} -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 {tmp}/tmp_{i:02d}.mov && mv {tmp}/tmp_{i:02d}.mov {part}; }}')
L.append('fi')
L.append('if [ "$STEP" = all ] || [ "$STEP" = 2 ]; then')
L.append(f'( for f in {tmp}/s*.mov; do echo "file \'$(basename $f)\'"; done ) > {tmp}/list.txt')
L.append(f'ffmpeg -v error -y -f concat -safe 0 -i {tmp}/list.txt -c copy {tmp}/base.mov')
L.append('fi')
ins, fc, cur, j = ['-i', 'BASEMOV'], [], '0:v', 1
for b in S.get('broll', []):
    Ln = b['rec_out'] - b['rec_in']
    ins += ['-ss', '1', '-t', f'{Ln:.2f}', '-i', f"{broll_dir}/{b['clip']}.mp4"]
    fc.append(f"[{j}:v]scale=-2:1920,crop=1080:1920,setsar=1,fps=25,setpts=PTS-STARTPTS+{b['rec_in']:.2f}/TB[b{j}]")
    fc.append(f"[{cur}][b{j}]overlay=0:0:eof_action=pass:enable='between(t,{b['rec_in']:.2f},{b['rec_out']:.2f})'[c{j}]")
    cur = f'c{j}'; j += 1
ins += ['-c:v', 'libvpx-vp9', '-i', ov]
fc.append(f'[{j}:v]format=yuva420p[ov];[{cur}][ov]overlay=0:0:format=auto[vout]')
fc.append('[0:a]loudnorm=I=-14:TP=-1:LRA=11[aout]')
cmd = ['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
       '-movflags', '+faststart', '-t', f"{S['dur']:.2f}", out]
L.append('if [ "$STEP" = all ] || [ "$STEP" = 3 ]; then')
L.append(' '.join(q(c) for c in cmd).replace('BASEMOV', f'{tmp}/base.mov') + f' && echo OK {q(out)}')
L.append('fi')
print('\n'.join(L))
