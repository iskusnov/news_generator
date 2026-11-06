#!/usr/bin/env python3
"""Задание сборки урока буткемпа для службы на Mac (~/PokaTySpal/queue), по образцу mac_final.py.

mac_lesson.py base  <edl.json> <экран.mp4> <камера avo.mp4> <звук.m4a> <папка задания на Mac> [noshare.json]  > job.sh
mac_lesson.py final <edl.json> <specs.json> <папка задания на Mac> <выход .mp4 на Mac>                       > job.sh
Все пути — macOS (абсолютные). Файлы одной Zoom-записи (экран, avo, m4a) имеют общий таймлайн.
base: каждый кусок edl → экран 1920×1080 + камера лектора (avo) 384×216 справа сверху, поверх окна камеры Zoom,
      с янтарной кромкой; звук из .m4a; ровно N кадров и столько же звука (PCM, apad, -t). Имя куска по содержимому
      (p_<src_in>_<кадры>.mov) — правка монтажа перерендеривает только изменённые куски; битые (без moov) — заново.
      noshare.json — [[с, по], …] секунды исходника без демонстрации экрана (Zoom пишет камеру на весь кадр):
      там PiP не нужен (ищется по прокси: корреляция кадра экрана и avo > 0,6).
      Склейка concat → base.mov, проверка длительности = сумма кусков.
final: [пре-ролл] + base.mov + [хвост под карту ДЗ] + плашки gfx/<id>.webm (VP9 с альфой, 1920×1080, rec — время итогового
      видео, см. bootcamp/build_specs.py) + звук: highpass, шумоподавление afftdn,
      loudnorm −16 LUFS → H.264 1080p (для LMS), AAC 192k, faststart.
Проверка места: меньше 30 ГБ — задание падает с LOW_DISK.
"""
import sys, json, shlex
q = shlex.quote; FPS = 25
HEAD = ['#!/bin/bash', 'set -e', 'export PATH=/opt/homebrew/bin:$PATH',
        'FREE=$(df -g "$HOME" | awk \'NR==2{print $4}\'); echo "free ${FREE}G"; [ "$FREE" -ge 30 ] || { echo "LOW_DISK ${FREE}G — нужно ≥30 ГБ"; exit 9; }',
        'ok(){ ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" >/dev/null 2>&1; }']
CAM_W, CAM_H, EDGE = 384, 216, 3
import os
# экран не 16:9 (урок 23.10: 2644×1394) — SCRFIT=1 вписывает с полями, без растяжения
SFIT = 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2' if os.environ.get('SCRFIT') else 'scale=1920:1080'
V = '-c:v h264_videotoolbox -b:v 10M -pix_fmt yuv420p'; A = '-c:a pcm_s16le -ar 48000 -ac 2'

def base(edl_p, SCR, CAM, AUD, JD, ns_p=None):
    # speed (edl после pipeline/speed.py) — setpts/atempo по куску; FREEZE=файл [[a,b,t_src]] — на [a,b] исходника вместо
    # экрана стоп-кадр экрана в момент t_src (чёрные плитки участников без камеры в записи Zoom, урок 23.10)
    NS = json.load(open(ns_p)) if ns_p else []
    FZ = json.load(open(os.environ['FREEZE'])) if os.environ.get('FREEZE') else []
    E = json.load(open(edl_p)); L = HEAD + [f'JD={q(JD)}; mkdir -p "$JD/parts" "$JD/frz"; cd "$JD"', 'echo "start $(date +%T)"']
    for a, b, ts in FZ:
        L.append(f'[ -s frz/f_{ts:.1f}.png ] || ffmpeg -v error -y -ss {ts:.2f} -i {q(SCR)} -frames:v 1 -vf {q(SFIT)} frz/f_{ts:.1f}.png')
    parts, frames = [], 0
    for e in E['edl']:
        sp = e.get('speed', 1.0)
        d = e['src_out'] - e['src_in']; nf = round(d / sp * FPS); frames += nf
        if nf < 1: continue
        p = f'parts/p_{e["src_in"]:.2f}_{nf}' + (f'_x{sp}' if sp != 1 else '') + '.mov'; parts.append(p); s = f'{e["src_in"]:.3f}'; t = f'{d + 0.5:.3f}'
        r = lambda x: max(0, x - e['src_in']) / sp
        off = [(r(a), r(b)) for a, b in NS if b > e['src_in'] and a < e['src_out']]
        en = (":enable='not(" + '+'.join(f'between(t,{a:.2f},{b:.2f})' for a, b in off) + ")'") if off else ''
        fz = [(r(a), r(b), ts) for a, b, ts in FZ if b > e['src_in'] and a < e['src_out']]
        st_ = f'setpts=(PTS-STARTPTS)/{sp},' if sp != 1 else ''
        ins = f'-ss {s} -t {t} -i {q(SCR)} -ss {s} -t {t} -i {q(CAM)} -ss {s} -t {t} -i {q(AUD)} '
        fzf = ''
        for k, (fa, fb, ts) in enumerate(fz):
            ins += f'-loop 1 -t {nf / FPS + 1:.2f} -i frz/f_{ts:.1f}.png '
            fzf += f'[{3 + k}:v]fps={FPS},setsar=1[z{k}];[s{k}][z{k}]overlay=0:0:enable=\'between(t,{fa:.2f},{fb:.2f})\'[s{k + 1}];'
        fc = (f'[1:v]{st_}fps={FPS},scale={CAM_W - EDGE}:{CAM_H - EDGE},pad={CAM_W}:{CAM_H}:{EDGE}:0:color=0xF5A623[c];'
              f'[0:v]{st_}fps={FPS},{SFIT},setsar=1[s0];{fzf}[s{len(fz)}][c]overlay={1920 - CAM_W}:0{en},format=yuv420p[v];'
              f'[2:a]aresample=48000' + (f',atempo={sp}' if sp != 1 else '') + f',afade=t=in:d=0.015,afade=t=out:st={max(0, nf / FPS - 0.015):.3f}:d=0.015,apad[a]')
        cmd = (f'ffmpeg -v error -y {ins}'
               f'-filter_complex {q(fc)} -map [v] -map [a] -frames:v {nf} {V} -t {nf / FPS:.3f} {A} parts/tmp.mov && mv parts/tmp.mov {p}')
        L.append(f'ok {p} || {{ {cmd}; }}; ok {p} || {{ echo "BROKEN {p}, повтор"; rm -f {p}; {cmd}; }}')
    L.append('for f in ' + ' '.join(parts) + '; do ok "$f" || { echo "MISSING $f"; exit 3; }; done; echo "parts $(date +%T)"')
    L.append("printf '%s\\n' " + ' '.join(q(f"file '{p.split('/')[-1]}'") for p in parts) + ' > parts/list.txt')
    L.append('ffmpeg -v error -xerror -y -f concat -safe 0 -i parts/list.txt -c copy base.mov')
    tot = frames / FPS
    L.append(f'B=$(ffprobe -v error -show_entries format=duration -of csv=p=0 base.mov); python3 -c "import sys; b=float(sys.argv[1]); sys.exit(0 if abs(b-{tot:.2f})<1.0 else 4)" "$B" || {{ echo "BASE_LEN $B ≠ {tot:.2f}"; exit 4; }}')
    L.append(f'echo "BASE_OK $B (ожидалось {tot:.2f}) $(date +%T)"')
    return L

def final(edl_p, specs_p, JD, OUT):
    E = json.load(open(edl_p)); S = json.load(open(specs_p)) if specs_p != '-' else []
    L = HEAD + [f'JD={q(JD)}; cd "$JD"', 'ok base.mov || { echo "NO base.mov"; exit 3; }', 'echo "start $(date +%T)"']
    # пре-ролл (type preroll, rec 0) ставится ПЕРЕД уроком на бумажном фоне с тишиной; карта ДЗ (type hw) — после конца,
    # на стоп-кадре. rec всех плашек — во времени итогового видео (bootcamp/build_specs.py).
    PRE = sum(s['dur'] for s in S if s['type'] == 'preroll')
    base_len = sum(round((e['src_out'] - e['src_in']) / e.get('speed', 1.0) * FPS) for e in E['edl']) / FPS
    TAIL = max([0.0] + [s['rec'] + s['dur'] - PRE - base_len for s in S])
    total = PRE + base_len + TAIL
    ins = ['-i', 'base.mov']; fc = []; j = 1
    if PRE:
        fc += [f'color=c=0xFFFDF8:s=1920x1080:r={FPS}:d={PRE:.2f},format=yuv420p,setsar=1[pc]',
               f'anullsrc=r=48000:cl=stereo,atrim=0:{PRE:.2f}[pa]',
               '[0:v]format=yuv420p,setsar=1[bv];[0:a]aresample=48000[ba]', '[pc][pa][bv][ba]concat=n=2:v=1:a=1[cv][ca]']
    else: fc += ['[0:v]null[cv]', '[0:a]anull[ca]']
    fc.append(f'[cv]tpad=stop_mode=clone:stop_duration={TAIL:.2f}[v0]'); cur = 'v0'
    for s in S:
        ins += ['-c:v', 'libvpx-vp9', '-i', f"gfx/{s['id']}.webm"]
        fc.append(f"[{j}:v]format=yuva420p,setpts=PTS-STARTPTS+{s['rec']:.2f}/TB[o{j}]")
        fc.append(f"[{cur}][o{j}]overlay={s.get('ox', 0)}:{s.get('oy', 0)}:eof_action=pass:enable='between(t,{s['rec']:.2f},{s['rec'] + s['dur']:.2f})'[w{j}]")
        cur = f'w{j}'; j += 1
    fc.append(f'[{cur}]format=yuv420p[v]')
    fc.append('[ca]highpass=f=70,afftdn=nr=12:nf=-50:tn=1,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.89,apad[a]')
    cmd = ['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
           '-c:v', 'h264_videotoolbox', '-b:v', '8M', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{total:.2f}', '-movflags', '+faststart', 'final_tmp.mp4']
    L.append(f'echo "итог {total:.2f} с: пре-ролл {PRE:.2f} + урок {base_len:.2f} + хвост {TAIL:.2f}"')
    L.append(' '.join(q(c) for c in cmd))
    L.append(f'mv final_tmp.mp4 {q(OUT)} && ffprobe -v error -show_entries format=duration -of csv=p=0 {q(OUT)} && echo "DONE $(date +%T) {OUT}"')
    return L

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'base' and len(a) in (6, 7): print('\n'.join(base(*a[1:])))
    elif a and a[0] == 'final' and len(a) == 5: print('\n'.join(final(*a[1:])))
    else: sys.exit(__doc__)
