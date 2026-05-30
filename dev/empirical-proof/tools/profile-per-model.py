import sys, re, json, gzip
path = sys.argv[1]
opener = gzip.open if path.endswith('.gz') else open
data = opener(path, 'rb').read().decode('utf-8', errors='ignore')

# Canonical model whitelist
CANON = {
  'claude-opus-4.7':   (15, 75, 18.75, 1.50),
  'claude-opus-4-7':   (15, 75, 18.75, 1.50),
  'claude-sonnet-4.6': (3, 15, 3.75, 0.30),
  'claude-sonnet-4-6': (3, 15, 3.75, 0.30),
  'claude-haiku-4.5':  (1, 5, 1.25, 0.10),
  'claude-haiku-4-5':  (1, 5, 1.25, 0.10),
}
NORM = {'claude-opus-4-7':'claude-opus-4.7','claude-sonnet-4-6':'claude-sonnet-4.6','claude-haiku-4-5':'claude-haiku-4.5'}

# Find all model declarations (request side)
model_events = []
for m in re.finditer(r'"model"\s*:\s*"([^"]+)"', data):
    name = m.group(1)
    if name in CANON:
        model_events.append((m.start(), NORM.get(name, name)))

# Find all usage blocks
usage_events = []
for m in re.finditer(r'"usage"\s*:\s*\{([^}]+)\}', data):
    body = m.group(1)
    try:
        pt = int(re.search(r'"prompt_tokens"\s*:\s*(\d+)', body).group(1))
        ct = int(re.search(r'"completion_tokens"\s*:\s*(\d+)', body).group(1))
    except: continue
    cache_read = int((re.search(r'"cached_tokens"\s*:\s*(\d+)', body) or re.search(r'"cache_read_input_tokens"\s*:\s*(\d+)', body) or re.match('^$','x')).group(1)) if (re.search(r'"cached_tokens"\s*:\s*(\d+)', body) or re.search(r'"cache_read_input_tokens"\s*:\s*(\d+)', body)) else 0
    cache_write = int(re.search(r'"cache_creation_(?:input_)?tokens"\s*:\s*(\d+)', body).group(1)) if re.search(r'"cache_creation_(?:input_)?tokens"\s*:\s*(\d+)', body) else 0
    usage_events.append((m.start(), pt, ct, cache_read, cache_write))

events = sorted([('m', p, n) for p,n in model_events] + [('u', p, *rest) for p,*rest in [(e[0], e[1], e[2], e[3], e[4]) for e in usage_events]], key=lambda x: x[1])

current = None
totals = {}
turns = {}
for e in events:
    if e[0] == 'm':
        current = e[2]
    else:
        if not current: continue
        _, _, pt, ct, cr, cw = e
        t = totals.setdefault(current, {'pt':0,'ct':0,'cr':0,'cw':0,'turns':0})
        t['pt'] += pt; t['ct'] += ct; t['cr'] += cr; t['cw'] += cw; t['turns'] += 1

print(f"=== {path} ===")
grand = 0.0; gturns = 0; gprompt = 0
for model, t in sorted(totals.items()):
    pin, pout, pcw, pcr = CANON[model]
    base_in = max(0, t['pt'] - t['cr'] - t['cw'])
    cost = base_in/1e6*pin + t['ct']/1e6*pout + t['cw']/1e6*pcw + t['cr']/1e6*pcr
    grand += cost; gturns += t['turns']; gprompt += t['pt']
    print(f"  {model}: turns={t['turns']:>4}  prompt={t['pt']:>10,}  completion={t['ct']:>8,}  cache_read={t['cr']:>10,}  cache_write={t['cw']:>8,}  cost=${cost:.2f}")
print(f"  TOTAL: turns={gturns} prompt={gprompt:,} cost=${grand:.2f}")
