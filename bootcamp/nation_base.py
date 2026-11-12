#!/usr/bin/env python3
"""Сборка урока в раскладке «Демонстрация экрана» дизайн-системы Нэйшн v1 (урок 08, 10.11.2026) — задание для службы на Mac.

nation_base.py base  <edl.json> <gfx.json> <экран.mp4> <avo.mp4> <звук.m4a> <папка задания> > job.sh
nation_base.py final <edl.json> <gfx.json> <папка задания> <выход.mp4> [пре-ролл_с] [ДЗ_с] [конец_с] > job.sh

base: каждый кусок edl → кадр 1920×1080: фон-раскладка главы (gfx/fr_*.png: тёмное поле, справа колонка с именем,
      ролью, главой и прогрессом) + экран 1504×846 (32,80; окно камеры Zoom 320×180 справа сверху закрыто цветом фона) +
      живая камера лектора (avo, квадрат 320, 1568,80) + метка роли; во время реплик участников камеру закрывает
      «Вопрос из зала» (gfx/qside.png); плашки gfx.json cards (время исходника): overlay — с появлением/исчезанием 0,45 с;
      chapter — жёлтая шторка 1,1 с + карточка части. noshare — камера Zoom на весь кадр (экран без раскладки).
      Все выражения — во времени исходника (t + src_in), поэтому плашка, пересекающая вырезку, просто укорачивается.
final: пре-ролл (gfx intro, тишина) + base.mov + ДЗ + конечная (стоп-кадры, тишина) → highpass, afftdn, loudnorm −16 LUFS,
      H.264 1080p 8 Мбит/с, AAC 192k.
"""
import sys, json, shlex, os, hashlib
q = shlex.quote; FPS = 25
HEAD = ['#!/bin/bash', 'set -e', 'export PATH=/opt/homebrew/bin:$PATH',
        'FREE=$(df -g "$HOME" | awk \'NR==2{print $4}\'); echo "free ${FREE}G"; [ "$FREE" -ge ${MINFREE:-30} ] || { echo "LOW_DISK ${FREE}G"; exit 9; }',
        'ok(){ ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" >/dev/null 2>&1; }']
V = os.environ.get('VENC', '-c:v h264_videotoolbox -b:v 10M -pix_fmt yuv420p'); A = '-c:a pcm_s16le -ar 48000 -ac 2'
SX, SY, SW, SH = 32, 80, 1504, 846; CX, CY, CS = 1568, 80, 320
YEL = '0xF2CB3A'

def ov(a, b, S, nf):  # пересечение [a,b] (исходник) с куском [S, S+nf/FPS]
    return b > S and a < S + nf / FPS

def base(edl_p, g_p, SCR, CAM, AUD, JD):
    E = json.load(open(edl_p))['edl']; G = json.load(open(g_p))
    L = HEAD + [f'JD={q(JD)}; mkdir -p "$JD/parts"; cd "$JD"', 'echo "start $(date +%T)"']
    parts = []
    for e in E:
        S = e['src_in']; d = e['src_out'] - S; nf = round(d * FPS)
        if nf < 1: continue
        T = f'(t+{S:.3f})'
        def btw(a, b): return f'between({T},{a:.2f},{b:.2f})'
        ins = [f'-ss {S:.3f} -t {d + 0.5:.3f} -i {q(SCR)}', f'-ss {S:.3f} -t {d + 0.5:.3f} -i {q(CAM)}', f'-ss {S:.3f} -t {d + 0.5:.3f} -i {q(AUD)}']
        k = 3
        def img(p):
            nonlocal k
            ins.append(f'-loop 1 -framerate {FPS} -t {nf / FPS + 0.2:.2f} -i {q("gfx/" + p.split("/")[-1])}'); k += 1; return k - 1
        fr = [f for f in G['frames'] if ov(f[0], f[1], S, nf)]
        fc = []
        i0 = img(fr[0][2]); fc.append(f'[{i0}:v]setsar=1,format=yuv420p[b0]'); cur = 'b0'
        for j, (a, b, p) in enumerate(fr[1:]):
            ii = img(p); fc.append(f"[{cur}][{ii}:v]overlay=0:0:enable='gte({T},{a:.2f})'[b{j + 1}]"); cur = f'b{j + 1}'
        dark = [x for x in G.get('dark', []) if ov(x[0], x[1], S, nf)]
        boxes = f"drawbox=x=1600:y=0:w=320:h=180:color=0x15161A:t=fill"
        fc.append(f'[0:v]fps={FPS},scale=1920:1080,setsar=1,split[sf][sx];[sx]{boxes},scale={SW}:{SH}[sc]')
        fc.append(f'[{cur}][sc]overlay={SX}:{SY}[l1]')
        fc.append(f'[1:v]fps={FPS},crop=ih:ih:(iw-ih)/2:0,scale={CS}:{CS},setsar=1[cm]')
        fc.append(f'[l1][cm]overlay={CX}:{CY}[l2]'); cur = 'l2'
        co = [x for x in G.get('camoff', []) if ov(x[0], x[1], S, nf)]   # лектор выключил камеру — его фото вместо чёрной плитки Zoom
        if co:
            ic = img(G['camoff_png']); fc.append(f"[{cur}][{ic}:v]overlay=0:0:enable='{'+'.join(btw(a, b) for a, b in co)}'[l2c]"); cur = 'l2c'
        ir = img(G['roletop']); fc.append(f'[{cur}][{ir}:v]overlay=0:0[l3]'); cur = 'l3'
        qs = [x for x in G['qside'] if ov(x[0], x[1], S, nf)]
        if qs:
            iq = img(G['qside_png']); fc.append(f"[{cur}][{iq}:v]overlay=0:0:enable='{'+'.join(btw(a, b) for a, b in qs)}'[l4]"); cur = 'l4'
        for c in G['cards']:
            if c['id'] == 'speaker' or not ov(c['from'], c['to'], S, nf): continue
            a, b = c['from'], c['to']; ic = img(c['png']); n = len(fc)
            if c['kind'] == 'chapter':
                fc.append(f"[{ic}:v]format=rgba,fade=t=out:st={b - S - 0.45:.3f}:d=0.45:alpha=1[c{n}]")
                fc.append(f"[{cur}][c{n}]overlay=0:0:enable='{btw(a + 0.55, b)}'[m{n}]")
                fc.append(f"color=c={YEL}:s=1920x1080:r={FPS}:d={nf / FPS + 0.2:.2f}[y{n}]")
                fc.append(f"[m{n}][y{n}]overlay=x='if(lt({T},{a + 0.55:.2f}),-1920+1920*({T}-{a:.2f})/0.55,1920*({T}-{a + 0.55:.2f})/0.55)':y=0:enable='{btw(a, a + 1.1)}'[n{n}]")
                cur = f'n{n}'
            else:
                fc.append(f"[{ic}:v]format=rgba," + (f"fade=t=in:st={a - S:.3f}:d=0.45:alpha=1," if a >= S else "") + f"fade=t=out:st={b - S - 0.45:.3f}:d=0.45:alpha=1[c{n}]")
                fc.append(f"[{cur}][c{n}]overlay=0:0:enable='{btw(a, b)}'[n{n}]"); cur = f'n{n}'
        ns = [x for x in G['noshare'] if ov(x[0], x[1], S, nf)]
        if ns:
            fc.append(f"[{cur}][sf]overlay=0:0:enable='{'+'.join(btw(a, b) for a, b in ns)}'[o0]"); cur = 'o0'
            sp = [c for c in G['cards'] if c['id'] == 'speaker' and ov(c['from'], c['to'], S, nf)]
            for c in sp:  # титр поверх полноэкранной камеры
                ic = img(c['png']); a, b = c['from'], c['to']
                fc.append(f"[{ic}:v]format=rgba," + (f"fade=t=in:st={a - S:.3f}:d=0.45:alpha=1," if a >= S else "") + f"fade=t=out:st={b - S - 0.45:.3f}:d=0.45:alpha=1[sp]")
                fc.append(f"[{cur}][sp]overlay=0:0:enable='{btw(a, b)}'[o1]"); cur = 'o1'
        else:
            fc.append('[sf]nullsink')
        fc.append(f'[{cur}]format=yuv420p[v]')
        fc.append(f'[2:a]aresample=48000,afade=t=in:d=0.015,afade=t=out:st={max(0, nf / FPS - 0.015):.3f}:d=0.015,apad[a]')
        sig = hashlib.md5(json.dumps([fc, ins[3:]]).encode()).hexdigest()[:8]
        p = f'parts/p_{S:.2f}_{nf}_{sig}.mov'; parts.append(p)
        TO = int(60 + nf / FPS * 2)   # тайм-аут куска (VideoToolbox иногда зависает): perl alarm, повтор на libx264
        def mk(venc): return (f"perl -e 'alarm shift; exec @ARGV' {TO} ffmpeg -nostdin -v error -y {' '.join(ins)} -filter_complex {q(';'.join(fc))} -map [v] -map [a] "
                              f'-frames:v {nf} {venc} -t {nf / FPS:.3f} {A} parts/tmp.mov && mv parts/tmp.mov {p}')
        L.append(f'ok {p} || {{ {mk(V)}; }} || true; ok {p} || {{ echo "RETRY {p}"; rm -f {p}; {mk("-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p")}; }}')
    L.append('for f in ' + ' '.join(parts) + '; do ok "$f" || { echo "MISSING $f"; exit 3; }; done; echo "parts $(date +%T)"')
    L.append("printf '%s\\n' " + ' '.join(q(f"file '{p.split('/')[-1]}'") for p in parts) + ' > parts/list.txt')
    L.append('ffmpeg -v error -xerror -y -f concat -safe 0 -i parts/list.txt -c copy base.mov')
    tot = sum(round((e['src_out'] - e['src_in']) * FPS) for e in E) / FPS
    L.append(f'B=$(ffprobe -v error -show_entries format=duration -of csv=p=0 base.mov); python3 -c "import sys; b=float(sys.argv[1]); sys.exit(0 if abs(b-{tot:.2f})<1.0 else 4)" "$B" || {{ echo "BASE_LEN $B"; exit 4; }}')
    L.append(f'echo "BASE_OK $B (ожидалось {tot:.2f}) $(date +%T)"')
    return L

def final(edl_p, g_p, JD, OUT, pre=5.0, hw=12.0, end=5.0):
    G = json.load(open(g_p))
    L = HEAD + [f'JD={q(JD)}; cd "$JD"', 'ok base.mov || { echo "NO base.mov"; exit 3; }', 'echo "start $(date +%T)"']
    def card(png, d, name):
        return (f'ffmpeg -v error -y -loop 1 -framerate {FPS} -t {d} -i {q("gfx/" + png.split("/")[-1])} -f lavfi -t {d} -i anullsrc=r=48000:cl=stereo '
                f'-vf "format=yuv420p,fade=t=in:d=0.45,fade=t=out:st={d - 0.45}:d=0.45" -shortest {V} {A} {name}')
    if G.get('intro_mp4'):   # анимированная заставка урока (graphics/nation/intro_v3.html, вариант B) вместо статичной карточки
        L.append(f'ffmpeg -v error -y -i {q("gfx/" + G["intro_mp4"].split("/")[-1])} -f lavfi -t {pre} -i anullsrc=r=48000:cl=stereo '
                 f'-vf "scale=1920:1080,fps={FPS},format=yuv420p,fade=t=out:st={pre - 0.4}:d=0.4" -t {pre} {V} {A} pre.mov')
    else: L.append(card(G['intro'], pre, 'pre.mov'))
    L.append(card(G['hw'], hw, 'hw.mov')); L.append(card(G['end'], end, 'end.mov'))
    L.append("printf \"file 'pre.mov'\\nfile 'base.mov'\\nfile 'hw.mov'\\nfile 'end.mov'\\n\" > final_list.txt")
    af = 'highpass=f=70,afftdn=nf=-30,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000'
    L.append(f'ffmpeg -v error -y -f concat -safe 0 -i final_list.txt -af {q(af)} -c:v h264_videotoolbox -b:v 8M -maxrate 10M -pix_fmt yuv420p '
             f'-c:a aac -b:a 192k -movflags +faststart {q(OUT + ".tmp.mp4")} && mv {q(OUT + ".tmp.mp4")} {q(OUT)}')
    L.append(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {q(OUT)}; echo "FINAL_OK $(date +%T)"')
    return L

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'base': print('\n'.join(base(*a[1:7])))
    else: print('\n'.join(final(a[1], a[2], a[3], a[4], *map(float, a[5:8]))))
