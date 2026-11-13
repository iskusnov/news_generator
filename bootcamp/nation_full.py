#!/usr/bin/env python3
"""Раскладка «слайд на весь кадр» (урок 12.11, вариант В, решение Антона 13.11): студенты жаловались на мелкий текст.

nation_full.py base <edl.json> <gfx.json> <slides.json> <экран.mp4> <avo.mp4> <звук.m4a> <папка задания> > job.sh

Кадр 1920×1080 = запись экрана целиком (слайд Google Slides 16:9 заполняет демонстрацию 1:1); где кадр совпал со
страницей презентации (slides.json: [[src_a, src_b, страница]], сверка NCC прокси 1 к/с со страницами PDF > 0.85),
поверх — чистая страница PDF (gfx/sl-NN.png, 1920×1080): резче, без окна Zoom. Камера лектора 230×230 вплотную
в правый верхний угол (1690,0) — закрывает окно Zoom (на 1920: x≥1696, y≤128) и на кадрах без слайдов.
Реплики зала — gfx/qside2.png, камера выключена — gfx/camoff2.png, метка роли — gfx/roletop2.png.
Плашки-цитаты справа (side) не ставим — им нет места; шторки частей и титр спикера — как в nation_base.
noshare — камера Zoom на весь кадр (как раньше). Финал — nation_base.py final (без изменений).
"""
import sys, json, shlex, hashlib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from nation_base import HEAD, V, A, FPS, YEL, ov, q

CX, CY, CS = 1690, 0, 230

def base(edl_p, g_p, sl_p, SCR, CAM, AUD, JD, only=None):
    E = json.load(open(edl_p))['edl']; G = json.load(open(g_p)); SL = json.load(open(sl_p))
    if only: E = only
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
        fc = [f'[0:v]setpts=PTS-STARTPTS,fps={FPS},scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p,split[b0][sf]']
        cur = 'b0'
        sl = [x for x in SL if ov(x[0], x[1], S, nf)]
        by = {}
        for a, b, pg in sl: by.setdefault(pg, []).append((a, b))
        for pg, iv in by.items():
            ii = img(f'sl-{pg:02d}.png'); n = len(fc)
            fc.append(f"[{cur}][{ii}:v]overlay=0:0:enable='{'+'.join(btw(a, b) for a, b in iv)}'[s{n}]"); cur = f's{n}'
        fc.append(f'[1:v]setpts=PTS-STARTPTS,fps={FPS},crop=ih:ih:(iw-ih)/2:0,scale={CS}:{CS}:flags=lanczos,setsar=1[cm]')
        # камера только там, где слайда нет (решение Антона 13.11: на слайдах — чистый слайд); на записи экрана она закрывает окно Zoom
        noslide = f"not({'+'.join(btw(a, b) for a, b, _ in sl)})" if sl else '1'
        fc.append(f"[{cur}][cm]overlay={CX}:{CY}:enable='{noslide}'[l2]"); cur = 'l2'
        co = [x for x in G.get('camoff', []) if ov(x[0], x[1], S, nf)]
        if co:
            ic = img('camoff2.png'); fc.append(f"[{cur}][{ic}:v]overlay=0:0:enable='({'+'.join(btw(a, b) for a, b in co)})*{noslide}'[l2c]"); cur = 'l2c'
        ir = img('roletop2.png'); fc.append(f"[{cur}][{ir}:v]overlay=0:0:enable='{noslide}'[l3]"); cur = 'l3'
        qs = [x for x in G['qside'] if ov(x[0], x[1], S, nf)]
        if qs:
            iq = img('qside2.png'); fc.append(f"[{cur}][{iq}:v]overlay=0:0:enable='{'+'.join(btw(a, b) for a, b in qs)}'[l4]"); cur = 'l4'
        for c in G['cards']:
            if c['kind'] != 'chapter' or not ov(c['from'], c['to'], S, nf): continue
            a, b = c['from'], c['to']; ic = img(c['png']); n = len(fc)
            fc.append(f"[{ic}:v]format=rgba,fade=t=out:st={b - S - 0.45:.3f}:d=0.45:alpha=1[c{n}]")
            fc.append(f"[{cur}][c{n}]overlay=0:0:enable='{btw(a + 0.55, b)}'[m{n}]")
            fc.append(f"color=c={YEL}:s=1920x1080:r={FPS}:d={nf / FPS + 0.2:.2f}[y{n}]")
            fc.append(f"[m{n}][y{n}]overlay=x='if(lt({T},{a + 0.55:.2f}),-1920+1920*({T}-{a:.2f})/0.55,1920*({T}-{a + 0.55:.2f})/0.55)':y=0:enable='{btw(a, a + 1.1)}'[n{n}]")
            cur = f'n{n}'
        ns = [x for x in G['noshare'] if ov(x[0], x[1], S, nf)]
        if ns:
            fc.append(f"[{cur}][sf]overlay=0:0:enable='{'+'.join(btw(a, b) for a, b in ns)}'[o0]"); cur = 'o0'
            for c in [c for c in G['cards'] if c['id'] == 'speaker' and ov(c['from'], c['to'], S, nf)]:
                ic = img(c['png']); a, b = c['from'], c['to']
                fc.append(f"[{ic}:v]format=rgba," + (f"fade=t=in:st={a - S:.3f}:d=0.45:alpha=1," if a >= S else "") + f"fade=t=out:st={b - S - 0.45:.3f}:d=0.45:alpha=1[sp]")
                fc.append(f"[{cur}][sp]overlay=0:0:enable='{btw(a, b)}'[o1]"); cur = 'o1'
        else:
            fc.append('[sf]nullsink')
        fc.append(f'[{cur}]format=yuv420p[v]')
        fc.append(f'[2:a]aresample=48000,afade=t=in:d=0.015,afade=t=out:st={max(0, nf / FPS - 0.015):.3f}:d=0.015,apad[a]')
        sig = hashlib.md5(json.dumps([fc, ins[3:]]).encode()).hexdigest()[:8]
        p = f'parts/p_{S:.2f}_{nf}_{sig}.mov'; parts.append(p)
        TO = int(90 + nf / FPS * 3)
        def mk(venc, to): return (f"perl -e 'alarm shift; exec @ARGV' {to} ffmpeg -nostdin -v error -y {' '.join(ins)} -/filter_complex parts/fc_{sig}.txt -map [v] -map [a] "
                                  f'-frames:v {nf} {venc} -t {nf / FPS:.3f} {A} parts/tmp.mov && mv parts/tmp.mov {p}')
        L.append(f"printf '%s' {q(';'.join(fc))} > parts/fc_{sig}.txt")
        L.append(f'ok {p} || {{ {mk(V, TO)}; }} || true; ok {p} || {{ echo "RETRY {p}"; rm -f {p}; {mk("-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p", int(120 + nf / FPS * 8))}; }} || true')
    L.append('for f in ' + ' '.join(parts) + '; do ok "$f" || { echo "MISSING $f"; exit 3; }; done; echo "parts $(date +%T)"')
    L.append("printf '%s\\n' " + ' '.join(q(f"file '{p.split('/')[-1]}'") for p in parts) + ' > parts/list.txt')
    L.append('ffmpeg -v error -xerror -y -f concat -safe 0 -i parts/list.txt -c copy base.mov')
    tot = sum(round((e['src_out'] - e['src_in']) * FPS) for e in E) / FPS
    L.append(f'B=$(ffprobe -v error -show_entries format=duration -of csv=p=0 base.mov); python3 -c "import sys; b=float(sys.argv[1]); sys.exit(0 if abs(b-{tot:.2f})<1.0 else 4)" "$B" || {{ echo "BASE_LEN $B"; exit 4; }}')
    L.append(f'echo "BASE_OK $B (ожидалось {tot:.2f}) $(date +%T)"')
    return L

if __name__ == '__main__':
    a = sys.argv[1:]
    only = json.loads(a[8]) if len(a) > 8 else None
    print('\n'.join(base(*a[1:8], only=only)))
