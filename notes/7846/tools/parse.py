"""Parse a tape (string of 0/1 from the left end up to the head) as a RecT configuration:
   l0, base, Rl digits, then "01" and the head (state C)."""
import sys, re
TOK = {(2, 3): 'm', (2, 2): '0', (3, 3): '1', (3, 2): '2', (4, 3): '3'}
def rle(s):
    out = []
    for m in re.finditer(r'0+|1+', s):
        g = m.group(); out.append(f"{g[0]}^{len(g)}" if len(g) > 3 else g)
    return ' '.join(out)
def parse(s):
    k = s.rfind('00')
    if k < 0: return None
    left = s[:k + 1]
    runs = s[k + 2:].split('0')
    runs = [len(r) for r in runs]
    if runs[-1] != 1: return None
    runs = runs[:-1]
    if len(runs) % 2 == 1:
        if runs[0] != 3: return None
        tp = 'L'; runs = runs[1:]
    else:
        tp = None
    digs = []
    for i in range(0, len(runs), 2):
        t = TOK.get((runs[i], runs[i + 1]))
        if t is None: return None
        digs.append(t)
    if tp is None:
        tp = digs[0]; digs = digs[1:]
    return left, tp, ''.join(digs)
if __name__ == '__main__':
    for line in sys.stdin:
        st, lo, s = line.split()
        p = parse(s)
        if p is None:
            print(st, lo, 'unparsed', rle(s[-200:])); continue
        left, tp, digs = p
        print(st, lo, 'tp', tp, 'n', len(digs), 'W', digs, '| left', rle(left)[:150], '| len', len(left))
