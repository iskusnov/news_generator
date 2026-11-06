import json, re
W = json.load(open('/home/claude/work/b1023/words.json'))
W = W['words'] if isinstance(W, dict) else W
N = [re.sub(r'[^\wё-]', '', w['word'].lower()) for w in W]
LOG = []

def find(kw, a, b=None, nth=0):
    """Start time of first occurrence of kw (words prefix-matched in sequence) within [a, b]."""
    b = b if b is not None else a + 600
    ks = [re.sub(r'[^\wё-]', '', k.lower()) for k in kw.split()]
    hits = []
    for i, w in enumerate(W):
        if w['start'] < a or w['start'] > b: continue
        if all(i + j < len(N) and N[i + j].startswith(k) for j, k in enumerate(ks)):
            hits.append(i)
    if len(hits) <= nth:
        raise SystemExit(f'NOT FOUND {kw!r} in {a}-{b}')
    i = hits[nth]
    LOG.append(f"{W[i]['start']:8.1f} {kw!r}: " + ' '.join(x['word'] for x in W[max(0, i - 4):i + 8]))
    return round(W[i]['start'], 2)

def ctx(a, b):
    return ' '.join(f"[{w['start']:.0f}]{w['word']}" if k % 12 == 0 else w['word'] for k, w in enumerate(x for x in W if a <= x['start'] <= b))
