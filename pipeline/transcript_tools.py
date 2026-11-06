#!/usr/bin/env python3
"""Транскрипты встреч: сырой текст из Groq, спикеры из Zoom, таймкоды.

Подкоманды:
  raw       <timed_dir> <out.md>                 — сырой текст из JSON Groq (по частям)
  speakers  <zoom.txt|.vtt> <in.md> <out.md>     — разметить реплики именами из Zoom-расшифровки (txt или vtt)
  timecodes <clean.md> <out.md> <timed_dir>      — проставить `ЧЧ:ММ:СС` в начале каждого абзаца
  words     <words.json> <zoom.vtt> <out.md> [names.json] — сырой текст из groq_words.py: абзацы по паузам,
            таймкоды из слов, спикеры по времени реплик .vtt (names.json: {"Имя в Zoom": "Имя в тексте"})

timed_dir — папка *_timed с zapis_chast_00.json, zapis_chast_01.json … (части по 30 мин = 1800 с).
Только стандартная библиотека Python 3.
"""
import sys, re, json, glob, os, difflib, bisect, collections

PART_SEC = 1800


def key(w):
    return re.sub(r"[^a-zа-яё0-9]", "", w.lower().replace("ё", "е"))[:5]


def part_files(timed_dir):
    fs = sorted(glob.glob(os.path.join(timed_dir, "*.json")))
    if not fs:
        sys.exit(f"Нет JSON в {timed_dir}")
    return fs


def align(C, T):
    """Сопоставить два списка ключей слов; вернуть индекс в T для каждого слова C (с интерполяцией)."""
    mb = difflib.SequenceMatcher(None, C, T, autojunk=False).get_matching_blocks()
    mp = [None] * len(C)
    for a, b, n in mb:
        for x in range(n):
            mp[a + x] = b + x
    known = [i for i, v in enumerate(mp) if v is not None]
    print(f"сопоставлено слов: {len(known)} из {len(C)}", file=sys.stderr)
    if not known:
        sys.exit("Тексты не совпали — проверьте, что файлы от одной записи")
    out = []
    for i in range(len(C)):
        if mp[i] is not None:
            out.append(float(mp[i])); continue
        j = bisect.bisect_left(known, i)
        lo = known[j - 1] if j > 0 else None
        hi = known[j] if j < len(known) else None
        if lo is None: out.append(float(mp[hi]))
        elif hi is None: out.append(float(mp[lo]))
        else: out.append(mp[lo] + (mp[hi] - mp[lo]) * (i - lo) / (hi - lo))
    return out


def cmd_raw(timed_dir, out_path):
    chunks = []
    for i, p in enumerate(part_files(timed_dir)):
        d = json.load(open(p, encoding="utf-8"))
        chunks.append(f"## Часть {i + 1}\n\n{d.get('text', '').strip()}\n")
    open(out_path, "w", encoding="utf-8").write("\n".join(chunks))


def cmd_speakers(zoom_path, in_path, out_path, names=None):
    names = names or {}
    Z, ZS = [], []
    # принимает и txt-расшифровку Zoom («Имя: текст»), и .vtt (таймкоды пропускаются)
    for l in open(zoom_path, encoding="utf-8"):
        if "-->" in l or l.strip().isdigit() or l.startswith("WEBVTT"): continue
        m = re.match(r"^([^:]{1,60}): (.*)", l)
        if not m: continue
        spk = names.get(m[1], m[1])
        for w in m[2].split():
            k = key(w)
            if k: Z.append(k); ZS.append(spk)
    blocks = []
    for ln in open(in_path, encoding="utf-8").read().split("\n"):
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("_"):
            blocks.append(("raw", ln)); continue
        s = re.sub(r"^\*\*[^*]{1,60}:\*\*\s*", "", s)
        sents = [x for x in re.split(r"(?<=[.!?…])\s+(?=[«\"A-ZА-ЯЁ0-9—–-])", s) if x]
        blocks.append(("para", sents))
    C, CS, sents_all = [], [], []
    for b in blocks:
        if b[0] != "para": continue
        for s in b[1]:
            sid = len(sents_all); sents_all.append(s)
            for w in s.split():
                k = key(w)
                if k: C.append(k); CS.append(sid)
    pos = align(C, Z)
    votes = collections.defaultdict(collections.Counter)
    for i, sid in enumerate(CS):
        votes[sid][ZS[min(int(round(pos[i])), len(ZS) - 1)]] += 1
    spk = [votes[i].most_common(1)[0][0] if votes[i] else None for i in range(len(sents_all))]
    for i in range(len(spk)):
        if spk[i] is None: spk[i] = spk[i - 1] if i else "?"
    out, cur, sid, after_h = [], None, 0, False
    for b in blocks:
        if b[0] == "raw":
            out.append(b[1]); after_h = after_h or b[1].startswith("#"); continue
        run, rs = [], None
        def flush():
            nonlocal cur, after_h
            if not run: return
            lab = f"**{rs}:** " if (rs != cur or after_h) else ""
            out.extend([lab + " ".join(run), ""]); cur = rs; after_h = False
        for s in b[1]:
            sp = spk[sid]; sid += 1
            if rs is not None and sp != rs:
                flush(); run = []
            rs = sp; run.append(s)
        flush()
    txt = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    open(out_path, "w", encoding="utf-8").write(txt)
    print(collections.Counter(spk).most_common(), file=sys.stderr)


def cmd_timecodes(clean_path, out_path, timed_dir):
    T, TT = [], []
    for i, p in enumerate(part_files(timed_dir)):
        d = json.load(open(p, encoding="utf-8")); off = i * PART_SEC
        for s in d.get("segments", []):
            ws = [w for w in s["text"].split() if key(w)]
            for j, w in enumerate(ws):
                T.append(key(w)); TT.append(off + s["start"] + (s["end"] - s["start"]) * j / max(len(ws), 1))
    lines = open(clean_path, encoding="utf-8").read().split("\n")
    C, CL = [], []
    for li, l in enumerate(lines):
        s = l.strip()
        if not s or s.startswith("#") or s.startswith("_") or re.match(r"^`\d\d:\d\d:\d\d`", s): continue
        s = re.sub(r"^\*\*[^*]{1,60}:\*\*", "", s)
        for w in s.split():
            k = key(w)
            if k: C.append(k); CL.append(li)
    pos = align(C, T)
    first = {}
    for i, li in enumerate(CL): first.setdefault(li, i)
    def t_at(p):
        lo = int(p); hi = min(lo + 1, len(TT) - 1)
        return TT[lo] + (TT[hi] - TT[lo]) * (p - lo)
    for li, i in first.items():
        t = int(t_at(pos[i]))
        lines[li] = f"`{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}` " + lines[li]
    open(out_path, "w", encoding="utf-8").write("\n".join(lines))


def vtt_cues(vtt_path, names=None):
    """[(start, end, speaker)] из .vtt Zoom."""
    names = names or {}
    cues, cur = [], None
    ts = lambda s: sum(float(x) * m for x, m in zip(s.replace(",", ".").split(":"), (3600, 60, 1)))
    for l in open(vtt_path, encoding="utf-8"):
        m = re.match(r"(\d\d:\d\d:\d\d\.\d+) --> (\d\d:\d\d:\d\d\.\d+)", l)
        if m: cur = (ts(m[1]), ts(m[2])); continue
        m = re.match(r"^([^:]{1,60}): ", l)
        if cur and m: cues.append((cur[0], cur[1], names.get(m[1], m[1]))); cur = None
    return cues


def cmd_words(words_path, vtt_path, out_path, names_path=None, gap=1.6, max_words=140):
    """Сырой текст из words.json (groq_words.py): абзацы по паузам, `ЧЧ:ММ:СС` и спикер по времени реплик Zoom (.vtt).
    Абзац рвётся на паузе > gap с, на смене спикера или после max_words слов на конце предложения."""
    names = json.load(open(names_path, encoding="utf-8")) if names_path else {}
    W = json.load(open(words_path, encoding="utf-8"))["words"]
    cues = vtt_cues(vtt_path, names); starts = [c[0] for c in cues]
    def spk_at(t):
        i = bisect.bisect_right(starts, t) - 1
        best, bd = "?", 1e9
        for j in (i, i + 1):
            if 0 <= j < len(cues):
                s, e, sp = cues[j]
                d = 0 if s <= t <= e else min(abs(t - s), abs(t - e))
                if d < bd: best, bd = sp, d
        return best if bd < 6 else "?"
    paras, cur = [], None
    for k, w in enumerate(W):
        sp = spk_at((w["start"] + w["end"]) / 2)
        brk = cur is None or (w["start"] - W[k - 1]["end"] > gap) or (sp != cur["sp"] and sp != "?") or \
              (len(cur["w"]) >= max_words and re.search(r"[.!?…]$", W[k - 1]["word"].strip()))
        if brk:
            cur = {"t": w["start"], "sp": sp if sp != "?" else (cur["sp"] if cur else "?"), "w": []}; paras.append(cur)
        cur["w"].append(w["word"].strip())
    out, last = [], None
    for p in paras:
        t = int(p["t"]); tc = f"`{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}`"
        lab = f" **{p['sp']}:**" if p["sp"] != last else ""
        out += [f"{tc}{lab} " + " ".join(p["w"]), ""]; last = p["sp"]
    open(out_path, "w", encoding="utf-8").write("\n".join(out))
    print(len(paras), "абзацев;", collections.Counter(p["sp"] for p in paras).most_common(), file=sys.stderr)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) in (4, 5) and a[0] == "words": cmd_words(*a[1:]); sys.exit()
    if len(a) == 3 and a[0] == "raw": cmd_raw(a[1], a[2])
    elif len(a) == 4 and a[0] == "speakers": cmd_speakers(a[1], a[2], a[3])
    elif len(a) == 4 and a[0] == "timecodes": cmd_timecodes(a[1], a[2], a[3])
    else: sys.exit(__doc__)
