#!/usr/bin/env python3
"""Задание финального рендера выпуска для службы на Mac (~/PokaTySpal/queue).

mac_final.py <edl.json> <specs.json> <crawl.json> <src.mov на Mac> <папка задания на Mac> <выход .mp4 на Mac> > job.sh
В папке задания лежат: intro.mp4 (4K, со звуком), gfx/<id>.webm (VP9 с альфой, 1920×1080), crawl.png + crawl_label.png (1x) или crawl_<i>.png окнами (pipeline/crawl.py),
sfx.wav (звук перехода между новостями), outro.wav (хвост трека под отбивку, 5 с).
Шаги (нативный ffmpeg, VideoToolbox):
 0) проверка места: меньше 30 ГБ свободно — задание сразу падает с LOW_DISK (Антону писать сразу, не ждать);
 1) каждый кусок исходника: ровно N кадров + столько же звука (PCM, apad, -t), кроп ×scale, ускорение ×speed
    (setpts + atempo, только куски с ведущим), HEVC 4K. Имя куска по содержимому, без номера:
    p_<src_in>_<кадры>_<scale>_x<speed>.mov — правка монтажа перерендеривает только изменённые куски;
    после рендера каждый кусок проверяется ffprobe, битый (без moov) рендерится заново;
 2) интро обрезано до gap, тем же кодеком; склейка concat без перекодирования;
 3) плашки поверх (масштаб ×2), бегущая строка, стоп-кадр под отбивку (5 с), звук перехода на каждой перебивке (kicker),
    хвост трека под отбивку (outro), шумоподавление (afftdn) → −14 LUFS (loudnorm + volume + limiter).
crawl.json: {"from": rec_с, "to": rec_с, "cycle": ширина цикла в px (1x), "speed": px/с (1x)}
OUT1080=1 — выход 1080p (12 Мбит/с) вместо 4K.
"""
import sys, json, shlex, os
edl_p, specs_p, crawl_p, SRC, JD, OUT = sys.argv[1:7]
E = json.load(open(edl_p)); S = json.load(open(specs_p)); C = json.load(open(crawl_p))
FPS = 25; TAIL = max(0.0, max(s['rec'] + s['dur'] for s in S) - E['total'])
q = shlex.quote
# запись из нескольких файлов: SRCn + OFFn (n=2..9), в edl время n-го файла = OFFn + t
SRCS = sorted([(float(os.environ.get(f'OFF{i}', {2: 1000, 3: 2000, 4: 5000}.get(i, 0))), os.environ[f'SRC{i}'])
               for i in range(2, 10) if os.environ.get(f'SRC{i}')], reverse=True)
def pick_src(t):
    for off, path in SRCS:
        if t >= off: return t - off, path
    return t, SRC
V = '-c:v hevc_videotoolbox -b:v 45M -tag:v hvc1 -pix_fmt yuv420p'
A = '-c:a pcm_s16le -ar 48000 -ac 2'
L = ['#!/bin/bash', 'set -e', 'export PATH=/opt/homebrew/bin:$PATH',
     'FREE=$(df -g "$HOME" | awk \'NR==2{print $4}\'); echo "free ${FREE}G"; [ "$FREE" -ge 30 ] || { echo "LOW_DISK ${FREE}G — нужно ≥30 ГБ"; exit 9; }',
     f'JD={q(JD)}; mkdir -p "$JD/parts" "$JD/gfx"; cd "$JD"', 'echo "start $(date +%T)"',
     'ok(){ ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" >/dev/null 2>&1; }']
parts = []
gap_done = False
for e in E['edl']:
    if E.get('gap_at') is not None and not gap_done and not e.get('clip') and e['rec'] >= E['gap_at'] - 1e-6:
        nf = round(E['gap'] * FPS)
        L.append(f'ok parts/intro.mov || ffmpeg -v error -y -i intro.mp4 -frames:v {nf} -vf fps=25,scale=3840:2160,format=yuv420p {V} '
                 f'-af apad -t {nf/FPS:.3f} {A} parts/intro.mov')
        parts.append('parts/intro.mov'); gap_done = True
    if e.get('clip'):  # врезка-ролик (inserts.py): вписать в 4K, вертикальный — поверх размытой копии, свой звук
        nf = round(e['dur'] * FPS); p = f"parts/c_{e['clip'].rsplit('.', 1)[0]}_{e['ss']:.2f}_{nf}.mov"; parts.append(p)
        fc_ = ("[0:v]fps=25,setsar=1,split[a][b];[a]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,boxblur=40:3,eq=brightness=-0.3[bg];"
               "[b]scale=3840:2160:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v];"
               f"[0:a]aresample=48000,volume={e.get('vol', 0.8)},afade=t=in:d=0.2,afade=t=out:st={max(0, nf / FPS - 0.3):.3f}:d=0.3,apad[au]")
        cmd = (f'ffmpeg -v error -y -ss {e["ss"]:.3f} -t {e["dur"] + 0.5:.3f} -i media/{q(e["clip"])} -filter_complex {q(fc_)} -map [v] -map [au] '
               f'-frames:v {nf} {V} -t {nf / FPS:.3f} {A} parts/tmp.mov && mv parts/tmp.mov {p}')
        L.append(f'ok {p} || {{ {cmd}; }}')
        continue
    sp = e.get('speed', 1.0)
    d = e['src_out'] - e['src_in']; nf = round(d / sp * FPS); k = e.get('scale', 1.0)
    w, h = int(3840 / k) // 2 * 2, int(2160 / k) // 2 * 2
    x, y = (3840 - w) // 2, 0 if k == 1.0 else int((2160 - h) * 0.35)
    p = f'parts/p_{e["src_in"]:.2f}_{nf}_{k}_x{sp}.mov'
    parts.append(p)
    vs = f',setpts=PTS/{sp}' if sp != 1.0 else ''
    at = f'atempo={sp},' if sp != 1.0 else ''
    s_in, s_src = pick_src(e['src_in'])
    cmd = (f'ffmpeg -v error -y -ss {s_in:.3f} -t {d + 0.5:.3f} -i {q(s_src)} -frames:v {nf} '
           f'-vf crop={w}:{h}:{x}:{y},scale=3840:2160{vs},fps=25,setsar=1,format=yuv420p {V} '
           f'-af {at}afade=t=in:d=0.015,afade=t=out:st={max(0, nf/FPS - 0.015):.3f}:d=0.015,apad -t {nf/FPS:.3f} {A} parts/tmp.mov && mv parts/tmp.mov {p}')
    L.append(f'ok {p} || {{ {cmd}; }}; ok {p} || {{ echo "BROKEN {p}, повтор"; rm -f {p}; {cmd}; }}')
L.append('for f in ' + ' '.join(parts) + '; do ok "$f" || { echo "MISSING $f"; exit 3; }; done; echo "parts $(date +%T)"')
L.append("printf '%s\\n' " + ' '.join(q(f"file '{p.split('/')[-1]}'") for p in parts) + ' > parts/list.txt')
L.append('ffmpeg -v error -xerror -y -f concat -safe 0 -i parts/list.txt -c copy base.mov')
L.append(f'B=$(ffprobe -v error -show_entries format=duration -of csv=p=0 base.mov); python3 -c "import sys; b=float(sys.argv[1]); sys.exit(0 if abs(b-{E["total"]:.2f})<0.5 else 4)" "$B" || {{ echo "BASE_LEN $B ≠ {E["total"]:.2f}"; exit 4; }}')
L.append('echo "base $(date +%T)"')
# бегущая строка: одно окно {from,to,cycle,speed} (crawl.png) или окна {speed, windows:[{from,to,png,label,cycle,lw}]} (pipeline/crawl.py)
WIN = C['windows'] if 'windows' in C else [dict(C, png='crawl.png', label='crawl_label.png', lw=0)]
ins = ['-i', 'base.mov']; fc = [f'[0:v]tpad=stop_mode=clone:stop_duration={TAIL:.2f}[v0]']; cur = 'v0'; j = 1
for k, w in enumerate(WIN):
    sp = w.get('speed', C.get('speed', 110)); en = f"between(t,{w['from']:.2f},{w['to']:.2f})"
    ins += ['-loop', '1', '-i', w['png'], '-loop', '1', '-i', w['label']]
    fc += [f'[{j}:v]scale=iw*2:ih*2,format=rgba[cr{k}]', f'[{j+1}:v]scale=iw*2:ih*2,format=rgba[lb{k}]',
           f"[{cur}][cr{k}]overlay=x='{w['lw']*2:.0f}-mod((t-{w['from']:.2f})*{sp*2}\\,{w['cycle']*2})':y=H-h:shortest=0:enable='{en}'[cv{k}]",
           f"[cv{k}][lb{k}]overlay=x=0:y=H-h:enable='{en}'[cl{k}]"]
    cur = f'cl{k}'; j += 2

for s in S:
    ins += ['-c:v', 'libvpx-vp9', '-i', f"gfx/{s['id']}.webm"]
    fc.append(f"[{j}:v]scale=3840:2160,format=yuva420p,setpts=PTS-STARTPTS+{s['rec']:.2f}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=0:0:eof_action=pass:enable='between(t,{s['rec']:.2f},{s['rec'] + s['dur']:.2f})'[w{j}]")
    cur = f'w{j}'; j += 1
# звук: шумоподавление и громкость речи, потом звук перехода и хвост трека
fc.append('[0:a]highpass=f=70,afftdn=nr=12:nf=-50:tn=1,apad,loudnorm=I=-14:TP=-1.5:LRA=11,volume=4dB,alimiter=limit=0.84[voice]')
mix = ['[voice]']
for s in S:
    if s['type'] == 'kicker':
        ins += ['-i', 'sfx.wav']; ms = int(max(0, s['rec'] - 0.15) * 1000)
        fc.append(f'[{j}:a]volume=0.5,adelay={ms}|{ms}[sx{j}]'); mix.append(f'[sx{j}]'); j += 1
    if s['type'] == 'outro':
        ins += ['-i', 'outro.wav']; ms = int(s['rec'] * 1000)
        fc.append(f'[{j}:a]volume=0.6,afade=t=in:d=0.4,adelay={ms}|{ms}[mo{j}]'); mix.append(f'[mo{j}]'); j += 1
fc.append(''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:duration=first[a]' if len(mix) > 1 else '[voice]anull[a]')
total = E['total'] + TAIL
vout = ['-c:v', 'hevc_videotoolbox', '-b:v', '30M']
if os.environ.get('OUT1080') == '1':
    fc.append(f'[{cur}]scale=1920:1080[vs]'); cur = 'vs'; vout = ['-c:v', 'hevc_videotoolbox', '-b:v', '12M']
cmd = ['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-map', '[a]'] + vout + \
      ['-tag:v', 'hvc1', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
       '-t', f'{total:.2f}', '-movflags', '+faststart', 'final_tmp.mp4']
L.append(' '.join(q(c) for c in cmd))
L.append(f'mv final_tmp.mp4 {q(OUT)} && ffprobe -v error -show_entries format=duration -of csv=p=0 {q(OUT)} && echo "DONE $(date +%T) {OUT}"')
print('\n'.join(L))
