#!/usr/bin/env python3
"""edl.json + specs.json -> FCPXML 1.9 для DaVinci Resolve.

fcpxml.py <edl.json> <specs.json> <исходник.mov на Mac> <длина исходника, с> <папка gfx на Mac> <out.fcpxml> [интро.mp4 на Mac]
Таймкод исходника берётся из edl (tc_start, в кадрах). Если дано интро — оно стоит в спайне на месте гэпа заставки
(со своим звуком); иначе гэп остаётся пустым. Плашки — gfx/<id>.mov (ProRes 4444 с альфой) на дорожках над видео.
Импорт: сначала перетащить исходник, интро и gfx/ в медиапул, затем Import Timeline без «Automatically import source clips».
"""
import json, sys, os
from xml.sax.saxutils import quoteattr as qa
ep, sp, SRC, SRC_DUR, GFX, OUT = sys.argv[1:7]
INTRO = sys.argv[7] if len(sys.argv) > 7 else ''
E = json.load(open(ep)); S = json.load(open(sp))
FPS = E.get('fps', 25); TC0 = E.get('tc_start', 0) / FPS
def t(sec): return f"{round(sec * FPS)}/{FPS}s"
url = lambda p: 'file://' + p.replace(' ', '%20')
name = os.path.splitext(os.path.basename(SRC))[0]
res = [f'<format id="r1" name="FFVideoFormat3840x2160p25" frameDuration="1/25s" width="3840" height="2160"/>',
       f'<asset id="src" name="{name}" start="{t(TC0)}" duration="{t(float(SRC_DUR))}" hasVideo="1" hasAudio="1" format="r1" audioSources="1" audioChannels="2" audioRate="48000"><media-rep kind="original-media" src={qa(url(SRC))}/></asset>']
if INTRO:
    res.append(f'<asset id="intro" name="intro" start="0s" duration="{t(E["gap"])}" hasVideo="1" hasAudio="1" format="r1" audioSources="1" audioChannels="2" audioRate="48000"><media-rep kind="original-media" src={qa(url(INTRO))}/></asset>')
for s in S:
    res.append(f'<asset id="g_{s["id"]}" name="gfx_{s["id"]}" start="0s" duration="{t(s["dur"])}" hasVideo="1" format="r1"><media-rep kind="original-media" src={qa(url(GFX + "/" + s["id"] + ".mov"))}/></asset>')

spine = [dict(kind='clip', off=e['rec'], start=TC0 + e['src_in'], dur=e['src_out'] - e['src_in'], scale=e['scale'], kids=[]) for e in E['edl']]
if E.get('gap_at') is not None:
    spine.append(dict(kind='intro' if INTRO else 'gap', off=E['gap_at'], start=0, dur=E['gap'], kids=[]))
spine.sort(key=lambda x: x['off'])

lanes = []
for s in sorted(S, key=lambda s: s['rec']):
    for i, end in enumerate(lanes):
        if end <= s['rec'] + 1e-6: lanes[i] = s['rec'] + s['dur']; s['lane'] = i + 1; break
    else: lanes.append(s['rec'] + s['dur']); s['lane'] = len(lanes)
    par = [p for p in spine if p['off'] <= s['rec'] + 1e-6][-1]
    par['kids'].append(f'<asset-clip ref="g_{s["id"]}" lane="{s["lane"]}" offset="{t(par["start"] + s["rec"] - par["off"])}" name="gfx_{s["id"]}" start="0s" duration="{t(s["dur"])}"/>')

body = []
for p in spine:
    kids = ''.join(p['kids'])
    if p['kind'] == 'gap':
        body.append(f'<gap name="Заставка" offset="{t(p["off"])}" start="0s" duration="{t(p["dur"])}">{kids}</gap>')
    elif p['kind'] == 'intro':
        body.append(f'<asset-clip ref="intro" offset="{t(p["off"])}" name="intro" start="0s" duration="{t(p["dur"])}">{kids}</asset-clip>')
    else:
        tr = f'<adjust-transform scale="{p["scale"]} {p["scale"]}"/>' if p['scale'] != 1.0 else ''
        body.append(f'<asset-clip ref="src" offset="{t(p["off"])}" name="{name}" start="{t(p["start"])}" duration="{t(p["dur"])}" tcFormat="NDF">{tr}{kids}</asset-clip>')
title = os.path.splitext(os.path.basename(OUT))[0]
xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
<resources>{''.join(res)}</resources>
<library><event name="{title}"><project name="{title}"><sequence format="r1" duration="{t(E['total'])}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k"><spine>
{chr(10).join(body)}
</spine></sequence></project></event></library>
</fcpxml>
'''
open(OUT, 'w').write(xml)
print(OUT, len(E['edl']), 'кусков,', len(S), 'плашек, дорожек', len(lanes))
