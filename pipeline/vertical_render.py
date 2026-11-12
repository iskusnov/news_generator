#!/usr/bin/env python3
"""Сценарий рендера вертикального ролика (Reels/Shorts) на Mac.

vertical_render.py <edl.json> <spec.json> <исходник> <оверлей .webm> <папка b-roll> <выход .mp4> > render.sh
Три шага, чтобы не упираться в память VM (несколько декодеров 4K HEVC сразу VM убивает):
 1) каждый кусок отдельно, ровно N кадров и столько же звука (иначе звук уезжает на склейках): кроп 9:16 (1215×2160, центр X = CX) → 1080×1920, «панч» ×1.12 из edl.scale, фейды звука 15 мс;
 2) склейка кусков без перекодирования (concat demuxer);
 3) b-roll поверх (кроп 9:16, окна из spec.broll) + графика (VP9 с альфой) + громкость −14 LUFS.
LESSON=1 — урок буткемпа (Zoom): <исходник> = запись экрана 1920×1080, CAM = камера лектора (avo), AUD = звук .m4a; кадр —
    бумажный фон, камера 1080×608 (y CAMY=280), слайд 1080×608 (y 904) — под шаблон graphics/overlays/bootcamp_short.html;
    MOTION=1 — без слайда: низ кадра занимает моушн-графика оверлея (сцены spec.extras, шаблон bootcamp_short.html).
Сценарий можно запускать частями: `bash render.sh 1`, `bash render.sh 2`, `bash render.sh 3` (каждая часть < 180 с).
"""
import sys, json, shlex, os
edl_p, spec_p, src, ov, broll_dir, out = sys.argv[1:7]
CX = 1920  # центр лица по горизонтали в кадре 3840
VERT = os.environ.get('VERT') == '1'; LESSON = os.environ.get('LESSON') == '1'; MOTION = os.environ.get('MOTION') == '1'; CAMY = int(os.environ.get('CAMY', 280)); CAM, AUD = os.environ.get('CAM'), os.environ.get('AUD'); SRC2 = os.environ.get('SRC2'); SRC3 = os.environ.get('SRC3')  # VERT=1 — исходник уже вертикальный; SRC2 — второй файл (в edl его время = 1000 + t)
OFF2, OFF3 = float(os.environ.get('OFF2', 1000)), float(os.environ.get('OFF3', 2000)); SRC4, OFF4 = os.environ.get('SRC4'), float(os.environ.get('OFF4', 5000))  # 4-й файл (вставка) = OFF4 + t  # если 1-й файл длиннее 1000 с — сдвинуть (например 3000/4000)
E = json.load(open(edl_p)); S = json.load(open(spec_p))
SRCS = sorted([(float(os.environ.get(f'OFF{i}', {2: 1000, 3: 2000, 4: 5000}.get(i, 0))), os.environ[f'SRC{i}']) for i in range(2, 10) if os.environ.get(f'SRC{i}')], reverse=True)
def pick_src(t):  # запись из нескольких файлов: время в edl = OFFn + t для n-го файла
    for off, path in SRCS:
        if t >= off: return t - off, path
    return t, src
tag = os.path.splitext(os.path.basename(out))[0]; tmp = f'$HOME/vrtmp/{tag}'  # промежуточное — на локальном диске VM (быстрее, можно удалять)
q = shlex.quote
parts = []
L = ['#!/bin/bash', 'set -e', f'STEP=${{1:-all}}; mkdir -p {tmp}', 'if [ "$STEP" = all ] || [ "$STEP" = 1 ]; then']
for i, e in enumerate(E['edl']):
    d = e['src_out'] - e['src_in']; k = e.get('scale', 1.0); sp = e.get('speed', 1.0)  # speed.py: setpts + atempo по куску
    if VERT:  # вертикальный исходник (телефон, 2160×3840 после поворота): кроп не нужен, только «панч»
        w, h = int(2160 / k) // 2 * 2, int(3840 / k) // 2 * 2
        x = (2160 - w) // 2; y = 0 if k == 1.0 else int((3840 - h) * 0.35)
    else:
        w, h = int(1215 / k) // 2 * 2, int(2160 / k) // 2 * 2
        x = max(0, min(3840 - w, CX - w // 2)); y = 0 if k == 1.0 else int((2160 - h) * 0.35)
    s_in, s_src = pick_src(e['src_in'])  # файл по смещению: SRC2..SRC9 / OFF2..OFF9
    bw = ',hue=s=0,eq=contrast=1.12' if e.get('bw') else ''  # врезка «мысли за кадром» — ч/б
    cs = e.get('cam_ss', 0.0)  # сдвиг камеры (с): закрыть кадры, где Zoom показал не лектора (звук остаётся на месте)
    nf = round(d / sp * 25); part = f'{tmp}/p_{e["src_in"]:.2f}_{nf}_{k}{"_bw" if e.get("bw") else ""}{f"_x{sp}" if sp != 1.0 else ""}{f"_c{cs}" if cs else ""}.mov'  # имя по содержимому: после правки монтажа готовые куски переиспользуются
    parts.append(part)
    if LESSON:
        cw, ch = int(1080 / k) // 2 * 2, int(608 / k) // 2 * 2  # «панч» камеры ×scale из edl (чередуется на склейках)
        st_ = f',setpts=PTS/{sp}' if sp != 1.0 else ''; at_ = f'atempo={sp},' if sp != 1.0 else ''
        cam = f'[1:v]scale=1080:608,crop={cw}:{ch}:{(1080 - cw) // 2}:{int((608 - ch) * 0.3)},scale=1080:608,setsar=1{st_},fps=25[c];'
        sld = f'[0:v]scale=1080:608,setsar=1{st_},fps=25[s];[a][s]overlay=0:904,format=yuv420p[v];' if not MOTION else '[a]format=yuv420p[v];'
        fc = (f'color=c={os.environ.get("BGC", "0xFFFDF8")}:s=1080x1920:r=25[bg];{cam}'
              f'[bg][c]overlay=0:{CAMY}:shortest=1[a];{sld}'
              f'[2:a]aresample=48000,{at_}afade=t=in:d=0.015,afade=t=out:st={max(0, nf/25 - 0.015):.3f}:d=0.015,apad[au]')
        t = f'{d + 0.5:.3f}'
        L.append(f'[ -s {part} ] || {{ ffmpeg -v error -y -ss {s_in:.3f} -t {t} -i {q(s_src)} -ss {s_in + cs:.3f} -t {t} -i {q(CAM)} -ss {s_in:.3f} -t {t} -i {q(AUD)} '
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
    ins += ['-ss', f"{b.get('ss', 1):.2f}", '-t', f'{Ln:.2f}', '-i', f"{broll_dir}/{b['clip']}.mp4"]
    if b.get('fit'):  # горизонтальный ролик целиком по центру поверх размытой копии (врезка-пример)
        fc.append(f"[{j}:v]fps=25,setsar=1,split[bf{j}][bg{j}];[bg{j}]scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.25[bb{j}];"
                  f"[bf{j}]scale=1080:-2[bt{j}];[bb{j}][bt{j}]overlay=0:(H-h)/2-{b.get('up', 120)},setpts=PTS-STARTPTS+{b['rec_in']:.2f}/TB[b{j}]")
    else:
        fc.append(f"[{j}:v]scale=-2:1920,crop=1080:1920,setsar=1,fps=25,setpts=PTS-STARTPTS+{b['rec_in']:.2f}/TB[b{j}]")
    fc.append(f"[{cur}][b{j}]overlay=0:0:eof_action=pass:enable='between(t,{b['rec_in']:.2f},{b['rec_out']:.2f})'[c{j}]")
    cur = f'c{j}'; j += 1
ins += ['-c:v', 'libvpx-vp9', '-i', ov]
fc.append(f'[{j}:v]format=yuva420p[ov];[{cur}][ov]overlay=0:0:format=auto[vout]')
fc.append('[0:a]loudnorm=I=-14:TP=-1:LRA=11' + (',apad' if tail else '') + '[av]')
mix = ['[av]']
for k, x in enumerate(S.get('sfx', [])):  # звуки (отбивка): файл в папке b-roll/задания, at — секунды ролика
    j += 1; ins += ['-i', f"{broll_dir}/{x['file']}"]; ms = int(x['at'] * 1000)
    fc.append(f"[{j}:a]aresample=48000,volume={x.get('vol', 0.5)},adelay={ms}|{ms}[sx{k}]"); mix.append(f'[sx{k}]')
fc.append(''.join(mix) + (f'amix=inputs={len(mix)}:normalize=0:duration=first[aout]' if len(mix) > 1 else 'anull[aout]'))
cmd = ['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
       '-movflags', '+faststart', '-t', f"{S['dur']:.2f}", out]
L.append('if [ "$STEP" = all ] || [ "$STEP" = 3 ]; then')
L.append(' '.join(q(c) for c in cmd).replace('BASEMOV', f'{tmp}/base.mov') + f' && echo OK {q(out)}')
L.append('fi')
print('\n'.join(L))
