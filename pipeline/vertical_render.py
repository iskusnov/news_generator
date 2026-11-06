#!/usr/bin/env python3
"""Сценарий рендера вертикального ролика (Reels/Shorts) на Mac.

vertical_render.py <edl.json> <spec.json> <исходник> <оверлей .webm> <папка b-roll> <выход .mp4> > render.sh
Три шага, чтобы не упираться в память VM (несколько декодеров 4K HEVC сразу VM убивает):
 1) каждый кусок отдельно, ровно N кадров и столько же звука (иначе звук уезжает на склейках): кроп 9:16 (1215×2160, центр X = CX) → 1080×1920, «панч» ×1.12 из edl.scale, фейды звука 15 мс;
 2) склейка кусков без перекодирования (concat demuxer);
 3) b-roll поверх (кроп 9:16, окна из spec.broll) + графика (VP9 с альфой) + громкость −14 LUFS.
LESSON=1 — урок буткемпа (Zoom): <исходник> = запись экрана 1920×1080, CAM = камера лектора (avo), AUD = звук .m4a; кадр —
    бумажный фон, камера 1080×608 (y 280), слайд 1080×608 (y 904) — под шаблон graphics/overlays/bootcamp_short.html.
Сценарий можно запускать частями: `bash render.sh 1`, `bash render.sh 2`, `bash render.sh 3` (каждая часть < 180 с).
"""
import sys, json, shlex, os
edl_p, spec_p, src, ov, broll_dir, out = sys.argv[1:7]
CX = 1920  # центр лица по горизонтали в кадре 3840
VERT = os.environ.get('VERT') == '1'; LESSON = os.environ.get('LESSON') == '1'; CAM, AUD = os.environ.get('CAM'), os.environ.get('AUD'); SRC2 = os.environ.get('SRC2'); SRC3 = os.environ.get('SRC3')  # VERT=1 — исходник уже вертикальный; SRC2 — второй файл (в edl его время = 1000 + t)
E = json.load(open(edl_p)); S = json.load(open(spec_p))
tag = os.path.splitext(os.path.basename(out))[0]; tmp = f'$HOME/vrtmp/{tag}'  # промежуточное — на локальном диске VM (быстрее, можно удалять)
q = shlex.quote
parts = []
L = ['#!/bin/bash', 'set -e', f'STEP=${{1:-all}}; mkdir -p {tmp}', 'if [ "$STEP" = all ] || [ "$STEP" = 1 ]; then']
for i, e in enumerate(E['edl']):
    d = e['src_out'] - e['src_in']; k = e.get('scale', 1.0)
    if VERT:  # вертикальный исходник (телефон, 2160×3840 после поворота): кроп не нужен, только «панч»
        w, h = int(2160 / k) // 2 * 2, int(3840 / k) // 2 * 2
        x = (2160 - w) // 2; y = 0 if k == 1.0 else int((3840 - h) * 0.35)
    else:
        w, h = int(1215 / k) // 2 * 2, int(2160 / k) // 2 * 2
        x = max(0, min(3840 - w, CX - w // 2)); y = 0 if k == 1.0 else int((2160 - h) * 0.35)
    s_in, s_src = (e['src_in'] - 2000, SRC3) if SRC3 and e['src_in'] >= 2000 else (e['src_in'] - 1000, SRC2) if SRC2 and e['src_in'] >= 1000 else (e['src_in'], src)  # 2-й файл = 1000+, 3-й = 2000+
    bw = ',hue=s=0,eq=contrast=1.12' if e.get('bw') else ''  # врезка «мысли за кадром» — ч/б
    nf = round(d * 25); part = f'{tmp}/p_{e["src_in"]:.2f}_{nf}_{k}{"_bw" if e.get("bw") else ""}.mov'  # имя по содержимому: после правки монтажа готовые куски переиспользуются
    parts.append(part)
    if LESSON:
        fc = ('color=c=0xFFFDF8:s=1080x1920:r=25[bg];[1:v]scale=1080:608,setsar=1,fps=25[c];[0:v]scale=1080:608,setsar=1,fps=25[s];'
              '[bg][c]overlay=0:280:shortest=1[a];[a][s]overlay=0:904,format=yuv420p[v];'
              f'[2:a]aresample=48000,afade=t=in:d=0.015,afade=t=out:st={max(0, nf/25 - 0.015):.3f}:d=0.015,apad[au]')
        t = f'{d + 0.5:.3f}'
        L.append(f'[ -s {part} ] || {{ ffmpeg -v error -y -ss {s_in:.3f} -t {t} -i {q(s_src)} -ss {s_in:.3f} -t {t} -i {q(CAM)} -ss {s_in:.3f} -t {t} -i {q(AUD)} '
                 f'-filter_complex {q(fc)} -map [v] -map [au] -frames:v {nf} -t {nf/25:.3f} -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p '
                 f'-c:a pcm_s16le -ar 48000 {tmp}/tmp.mov && mv {tmp}/tmp.mov {part}; }}')
        continue
    L.append(f'[ -s {part} ] || {{ ffmpeg -v error -y -ss {s_in:.3f} -i {q(s_src)} '
             f'-vf crop={w}:{h}:{x}:{y},scale=1080:1920,setsar=1,fps=25{bw} '
             f'-af afade=t=in:d=0.015,afade=t=out:st={max(0, nf/25 - 0.015):.3f}:d=0.015,apad '
             f'-t {nf/25:.3f} -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -c:a pcm_s16le -ar 48000 {tmp}/tmp.mov && mv {tmp}/tmp.mov {part}; }}')
L.append('fi')
L.append('if [ "$STEP" = all ] || [ "$STEP" = 2 ]; then')
L.append(f"printf '%s\\n' " + ' '.join(q("file '" + os.path.basename(p) + "'") for p in parts) + f' > {tmp}/list.txt')
L.append(f'ffmpeg -v error -y -f concat -safe 0 -i {tmp}/list.txt -c copy {tmp}/base.mov')
L.append('fi')
ins, fc, cur, j = ['-i', 'BASEMOV'], [], '0:v', 1
tail = S.get('tail', 0)
if tail:  # стоп-кадр последнего кадра под финальную карточку
    fc.append(f'[0:v]tpad=stop_mode=clone:stop_duration={tail:.2f}[v0]'); cur = 'v0'
for b in S.get('broll', []):
    Ln = b['rec_out'] - b['rec_in']
    ins += ['-ss', '1', '-t', f'{Ln:.2f}', '-i', f"{broll_dir}/{b['clip']}.mp4"]
    fc.append(f"[{j}:v]scale=-2:1920,crop=1080:1920,setsar=1,fps=25,setpts=PTS-STARTPTS+{b['rec_in']:.2f}/TB[b{j}]")
    fc.append(f"[{cur}][b{j}]overlay=0:0:eof_action=pass:enable='between(t,{b['rec_in']:.2f},{b['rec_out']:.2f})'[c{j}]")
    cur = f'c{j}'; j += 1
ins += ['-c:v', 'libvpx-vp9', '-i', ov]
fc.append(f'[{j}:v]format=yuva420p[ov];[{cur}][ov]overlay=0:0:format=auto[vout]')
fc.append('[0:a]loudnorm=I=-14:TP=-1:LRA=11' + (',apad' if tail else '') + '[aout]')
cmd = ['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
       '-movflags', '+faststart', '-t', f"{S['dur']:.2f}", out]
L.append('if [ "$STEP" = all ] || [ "$STEP" = 3 ]; then')
L.append(' '.join(q(c) for c in cmd).replace('BASEMOV', f'{tmp}/base.mov') + f' && echo OK {q(out)}')
L.append('fi')
print('\n'.join(L))
