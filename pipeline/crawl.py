#!/usr/bin/env python3
"""Бегущая строка окнами: crawl.py <crawl_src.json> <папка_вывода>
crawl_src.json: {"speed":110, "windows":[{"from":с,"to":с,"label":"ДАЛЕЕ В ВЫПУСКЕ","items":[...]}, ...]}
→ crawl_<i>.png, crawl_label_<i>.png (1x, высота 52) и crawl.json для mac_final.py (windows с png/label/cycle/lw)."""
import sys, json, os, html
from playwright.sync_api import sync_playwright
src, out = sys.argv[1], sys.argv[2]; C = json.load(open(src)); os.makedirs(out, exist_ok=True)
NM = '/home/claude/news_generator/graphics/node_modules/@fontsource'
CSS = f"""<link rel="stylesheet" href="{NM}/manrope/800.css"><link rel="stylesheet" href="{NM}/jetbrains-mono/700.css">
<style>*{{margin:0;padding:0}}body{{background:transparent}}
#b{{display:inline-flex;align-items:center;height:52px;background:#C8FF2E;color:#0D0D0F;white-space:nowrap;font-family:'Manrope';font-weight:800;font-size:24px}}
.it{{padding:0 22px}}.st{{font-family:'JetBrains Mono';font-size:20px}}
.lb{{display:inline-flex;align-items:center;height:52px;padding:0 20px;background:#0D0D0F;color:#C8FF2E;font-family:'JetBrains Mono';font-weight:700;font-size:20px;letter-spacing:.12em;white-space:nowrap}}
</style>"""
res = {'speed': C.get('speed', 110), 'windows': []}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1920, 'height': 200})
    for i, w in enumerate(C['windows']):
        one = ''.join(f'<span class="it">{html.escape(t)}</span><span class="st">✶</span>' for t in w['items'])
        pg.set_content(f'<!doctype html><html><head><meta charset="utf-8">{CSS}</head><body><div id="b">{one}</div><br><div id="l" class="lb">{html.escape(w["label"])}</div></body></html>')
        pg.evaluate('document.fonts.ready.then(()=>1)')
        cyc = pg.evaluate("document.getElementById('b').getBoundingClientRect().width")
        reps = int(1920 // cyc) + 3
        pg.evaluate(f"(()=>{{const b=document.getElementById('b');b.innerHTML=b.innerHTML.repeat({reps});return 1}})()")
        pg.set_viewport_size({'width': int(cyc * reps) + 10, 'height': 200})
        pg.locator('#b').screenshot(path=f'{out}/crawl_{i}.png', omit_background=True)
        pg.locator('#l').screenshot(path=f'{out}/crawl_label_{i}.png', omit_background=True)
        lw = pg.evaluate("document.getElementById('l').getBoundingClientRect().width")
        res['windows'].append({'from': w['from'], 'to': w['to'], 'png': f'crawl_{i}.png', 'label': f'crawl_label_{i}.png', 'cycle': round(cyc, 2), 'lw': round(lw, 1)})
    b.close()
json.dump(res, open(f'{out}/crawl.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False))
