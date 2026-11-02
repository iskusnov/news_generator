#!/usr/bin/env python3
"""Собрать экземпляр композиции: build.py <шаблон> <vars.json> <длительность_с> <выход.html> [аудио]
Подставляет длительность, переменные (window.__VARS__) и необязательную музыку."""
import sys, json, os
tpl, vars_path, dur, out = sys.argv[1:5]
audio = sys.argv[5] if len(sys.argv) > 5 else ''
h = open(tpl, encoding='utf-8').read()
v = json.load(open(vars_path, encoding='utf-8'))
h = h.replace('__DUR__', str(dur))
a = (f'<audio class="clip" src="{audio}" data-start="0" data-duration="{dur}" data-track-index="1"></audio>' if audio else '')
h = h.replace('__AUDIO__', a)
h = h.replace('<script>\nconst V=', '<script>window.__VARS__=' + json.dumps(v, ensure_ascii=False) + ';</script>\n<script>\nconst V=', 1)
os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
open(out, 'w', encoding='utf-8').write(h)
print(out)
