#!/usr/bin/env python3
"""edl.json + specs.json -> FCPXML 1.9 для DaVinci Resolve"""
import json, sys
from xml.sax.saxutils import quoteattr as qa
E = json.load(open('edl.json')); S = json.load(open('specs.json'))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/Users/anton/Downloads/A001_11020636_C015.mov'
GFX = sys.argv[2] if len(sys.argv) > 2 else '/Users/anton/Downloads/transcribe/podcast_2026-11-02/gfx'
TC0 = 6 * 3600 + 36 * 60 + 16  # таймкод исходника 06:36:16:00
FPS = 25
def t(sec): return f"{round(sec * FPS)}/{FPS}s"
url = lambda p: 'file://' + p.replace(' ', '%20')

res = [f'<format id="r1" name="FFVideoFormat3840x2160p25" frameDuration="1/25s" width="3840" height="2160"/>',
       f'<asset id="src" name="A001_11020636_C015" start="{t(TC0)}" duration="{t(833.2)}" hasVideo="1" hasAudio="1" format="r1" audioSources="1" audioChannels="2" audioRate="48000"><media-rep kind="original-media" src={qa(url(SRC))}/></asset>',
       f'<asset id="sfx" name="opener_sfx" start="0s" duration="{t(5.2)}" hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000"><media-rep kind="original-media" src={qa(url(GFX + "/opener_sfx.wav"))}/></asset>']
for s in S:
    res.append(f'<asset id="g_{s["id"]}" name="gfx_{s["id"]}" start="0s" duration="{t(s["dur"])}" hasVideo="1" format="r1"><media-rep kind="original-media" src={qa(url(GFX + "/" + s["id"] + ".mov"))}/></asset>')

# спайн: куски исходника + гэп под заставку
spine = []
for e in E['edl']:
    spine.append(dict(kind='clip', off=e['rec'], start=TC0 + e['src_in'], dur=e['src_out'] - e['src_in'], scale=e['scale'], kids=[]))
spine.append(dict(kind='gap', off=E['gap_at'], start=0, dur=E['gap'], kids=[]))
spine.sort(key=lambda x: x['off'])

# дорожки: жадно, чтобы пересекающиеся элементы были на разных
lanes = []
for s in sorted(S, key=lambda s: s['rec']):
    for i, end in enumerate(lanes):
        if end <= s['rec'] + 1e-6: lanes[i] = s['rec'] + s['dur']; s['lane'] = i + 1; break
    else: lanes.append(s['rec'] + s['dur']); s['lane'] = len(lanes)
    par = [p for p in spine if p['off'] <= s['rec'] + 1e-6][-1]
    par['kids'].append(f'<asset-clip ref="g_{s["id"]}" lane="{s["lane"]}" offset="{t(par["start"] + s["rec"] - par["off"])}" name="gfx_{s["id"]}" start="0s" duration="{t(s["dur"])}"/>')
    if s['id'] == 'opener':
        par['kids'].append(f'<asset-clip ref="sfx" lane="-1" offset="{t(par["start"] + s["rec"] - par["off"])}" name="opener_sfx" start="0s" duration="{t(5.2)}"/>')

body = []
for p in spine:
    kids = ''.join(p['kids'])
    if p['kind'] == 'gap':
        body.append(f'<gap name="Заставка" offset="{t(p["off"])}" start="0s" duration="{t(p["dur"])}">{kids}</gap>')
    else:
        tr = f'<adjust-transform scale="{p["scale"]} {p["scale"]}"/>' if p['scale'] != 1.0 else ''
        body.append(f'<asset-clip ref="src" offset="{t(p["off"])}" name="A001_11020636_C015" start="{t(p["start"])}" duration="{t(p["dur"])}" tcFormat="NDF">{tr}{kids}</asset-clip>')

xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
<resources>
{chr(10).join(res)}
</resources>
<library><event name="Подкаст 2026-11-02"><project name="Подкаст 02.11 — монтаж v1">
<sequence format="r1" duration="{t(E['total'])}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k"><spine>
{chr(10).join(body)}
</spine></sequence></project></event></library>
</fcpxml>
'''
open('podcast_2026-11-02_montage.fcpxml', 'w').write(xml)
print('lanes', len(lanes), 'clips', len(E['edl']))
