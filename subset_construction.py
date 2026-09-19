import html
import math
import re
import sys
from collections import deque
from pathlib import Path

CELL = re.compile(r"\{[^}]*\}|\d+")


def parse_set(text, n):
    """Parse '0', '{1 5}' or '3 5' into a frozenset of state numbers."""
    tokens = text.replace("{", " ").replace("}", " ").split()
    if n < 10:  # single-digit states: tolerate compact forms such as {15}
        tokens = [d for t in tokens for d in t]
    return frozenset(int(t) for t in tokens if t != "0")


class NFA:
    def __init__(self, n, initial, alphabet, final, delta):
        self.n = n
        self.initial = initial
        self.alphabet = alphabet
        self.final = final
        self.delta = delta  # delta[state][symbol] -> frozenset of states

    def move(self, subset, symbol):
        result = set()
        for state in subset:
            result |= self.delta[state][symbol]
        return frozenset(result)


def read_cases(lines):
    it = iter(lines)
    for _ in range(int(next(it))):
        n = int(next(it))
        initial = parse_set(next(it), n)
        alphabet = next(it).split()
        if len(alphabet) == 1 and len(alphabet[0]) > 1:
            alphabet = list(alphabet[0])
        final = parse_set(next(it), n)
        delta = {}
        for state in range(1, n + 1):
            row = next(it).strip()
            if row.startswith(str(state)):  # drop the row label
                row = row[len(str(state)):]
            cells = CELL.findall(row)
            delta[state] = {a: parse_set(c, n) for a, c in zip(alphabet, cells)}
        yield NFA(n, initial, alphabet, final, delta)


def subset_construction(nfa):
    """Return (start, ordered reachable subsets, transitions)."""
    start = nfa.initial
    order, table = [start], {}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        table[current] = {}
        for symbol in nfa.alphabet:
            target = nfa.move(current, symbol)
            table[current][symbol] = target
            if target not in table and target not in order:
                order.append(target)
                queue.append(target)
    return start, order, table


def name(subset):
    return "{" + " ".join(map(str, sorted(subset))) + "}" if subset else "0"


def render(nfa, start, order, table):
    rows = [("", "") + tuple(nfa.alphabet)]
    for subset in order:
        marker = ("->" if subset == start else "") + \
                 ("<-" if subset & nfa.final else "")
        rows.append((marker, name(subset)) +
                    tuple(name(table[subset][a]) for a in nfa.alphabet))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return [" ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in rows]


# ---------------------------------------------------------------------------
# Optional feature: HTML report with tables and diagrams (--html [file])
# ---------------------------------------------------------------------------

NODE_RY, ROW, GAP = 24, 122, 92

CSS = """
:root{--bg:#f3f5fb;--card:#fff;--text:#1b2236;--muted:#6f7a93;--line:#e4e9f3;
--accent:#5b5bd6;--accent-soft:#e7e7fb;--final:#0e9f8b;--final-soft:#ddf5f0;
--edge:#77829e;--shadow:0 10px 34px rgba(27,34,54,.08)}
@media (prefers-color-scheme:dark){:root{--bg:#0d1120;--card:#161b2e;--text:#e8ecf7;
--muted:#8f99b5;--line:#252c44;--accent:#8f8fff;--accent-soft:#25274d;--final:#2fd6ba;
--final-soft:#113a3b;--edge:#8b95b4;--shadow:none}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:56px 24px 72px;color:#fff;
background:linear-gradient(135deg,#4338ca 0%,#6d5bf0 45%,#0ea5a4 100%)}
header .in,main{max-width:1080px;margin:0 auto}
header h1{margin:0 0 6px;font-size:34px;letter-spacing:-.02em}
header p{margin:0;opacity:.88;font-size:16px}
main{padding:0 20px 56px;margin-top:-40px}
.card{background:var(--card);border:1px solid var(--line);border-radius:20px;
box-shadow:var(--shadow);padding:28px;margin-bottom:28px}
.card h2{margin:0 0 14px;font-size:22px;letter-spacing:-.01em}
.card h3{margin:26px 0 10px;font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{background:var(--accent-soft);color:var(--accent);border-radius:999px;
padding:4px 13px;font-size:13px;font-weight:600}
.chip b{color:var(--text);font-weight:700}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:14px;padding:6px}
svg{display:block;max-width:none;margin:0 auto}
.edge{fill:none;stroke:var(--edge);stroke-width:1.7}
.arrow{fill:var(--edge)}
.body{fill:var(--card);stroke:var(--accent);stroke-width:2}
.start .body{fill:var(--accent-soft)}
.ring{fill:none;stroke:var(--final);stroke-width:2}
.final .body{stroke:var(--final)}
.final .ring{fill:var(--final-soft)}
.dead .body{stroke:var(--muted);stroke-dasharray:5 4}
.node text{font:600 13px ui-monospace,SFMono-Regular,Consolas,monospace;fill:var(--text);
text-anchor:middle;dominant-baseline:central}
.lbl{font:700 13px ui-monospace,SFMono-Regular,Consolas,monospace;fill:var(--accent);
text-anchor:middle;dominant-baseline:central;stroke:var(--card);stroke-width:5;
paint-order:stroke;stroke-linejoin:round}
.init{stroke:var(--accent);stroke-width:2.4;fill:none}
.arrow-i{fill:var(--accent)}
.legend{display:flex;flex-wrap:wrap;gap:18px;margin-top:12px;color:var(--muted);font-size:13px}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:14px}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.06em}
tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--accent-soft)}
td.m,th.m{width:1%;white-space:nowrap}
.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.empty{color:var(--muted)}
.badge{display:inline-block;border-radius:6px;padding:1px 8px;margin-right:4px;font-size:11px;
font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.b-start{background:var(--accent-soft);color:var(--accent)}
.b-final{background:var(--final-soft);color:var(--final)}
details{margin-top:22px}
summary{cursor:pointer;color:var(--muted);font-weight:600}
footer{text-align:center;color:var(--muted);font-size:13px;padding-bottom:36px}
"""


def pretty(subset):
    return "{" + " ".join(map(str, sorted(subset))) + "}" if subset else "∅"


def node_rx(subset):
    return max(30, 3.8 * len(pretty(subset)) + 18)


def boundary(center, rx, target, pad=0):
    """Point where the ray center->target leaves the node ellipse."""
    dx, dy = target[0] - center[0], target[1] - center[1]
    t = 1 / math.hypot(dx / (rx + pad), dy / (NODE_RY + pad))
    return center[0] + dx * t, center[1] + dy * t


def segment_distance(p, a, b):
    """Distance from point p to segment a-b."""
    (px, py), (ax, ay), (bx, by) = p, a, b
    length2 = (bx - ax) ** 2 + (by - ay) ** 2
    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / length2))
    return math.hypot(px - (ax + t * (bx - ax)), py - (ay + t * (by - ay)))


def diagram(index, nfa, start, order, table):
    depth = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for symbol in nfa.alphabet:
            target = table[current][symbol]
            if target not in depth:
                depth[target] = depth[current] + 1
                queue.append(target)
    layers = {}
    for subset in order:
        layers.setdefault(depth[subset], []).append(subset)

    rx = {s: node_rx(s) for s in order}
    height = max(len(v) for v in layers.values()) * ROW + 100
    pos, x, previous = {}, 0, 0
    for d in sorted(layers):
        widest = max(rx[s] for s in layers[d])
        x = widest + 76 if d == 0 else x + previous + GAP + widest
        previous = widest
        for i, subset in enumerate(layers[d]):
            pos[subset] = (x, height / 2 + (i - (len(layers[d]) - 1) / 2) * ROW)
    width = round(x + previous + 40)

    groups = {}
    for source in order:
        for symbol in nfa.alphabet:
            groups.setdefault((source, table[source][symbol]), []).append(symbol)

    aid, iid = f"arrow-{index}", f"init-{index}"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{round(height)}" '
           f'viewBox="0 0 {width} {round(height)}" role="img" aria-label="DFA diagram">',
           f'<defs><marker id="{aid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
           f'markerHeight="8" orient="auto"><path class="arrow" d="M0 0L10 5L0 10z"/></marker>'
           f'<marker id="{iid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
           f'markerHeight="8" orient="auto"><path class="arrow-i" d="M0 0L10 5L0 10z"/></marker></defs>']

    for (source, target), symbols in groups.items():
        label = ",".join(symbols)
        (x1, y1), (x2, y2) = pos[source], pos[target]
        if source == target:
            top = y1 - NODE_RY * math.sqrt(max(0, 1 - (14 / rx[source]) ** 2))
            out.append(f'<path class="edge" marker-end="url(#{aid})" d="M{x1 - 14:.1f} {top:.1f} '
                       f'C{x1 - 36:.1f} {top - 48:.1f} {x1 + 36:.1f} {top - 48:.1f} '
                       f'{x1 + 12:.1f} {top - 1:.1f}"/>')
            out.append(f'<text class="lbl" x="{x1:.1f}" y="{top - 42:.1f}">{html.escape(label)}</text>')
            continue
        dist = math.hypot(x2 - x1, y2 - y1)
        px, py = -(y2 - y1) / dist, (x2 - x1) / dist  # right of travel direction
        bend = 0
        if (target, source) in groups:  # opposite edge exists: separate the two
            bend = 36
        elif any(o not in (source, target) and
                 segment_distance(pos[o], pos[source], pos[target]) < NODE_RY + 14
                 for o in order):  # straight line would cross another node
            bend = 62
        control = ((x1 + x2) / 2 + px * bend, (y1 + y2) / 2 + py * bend)
        sx, sy = boundary(pos[source], rx[source], control)
        ex, ey = boundary(pos[target], rx[target], control, 3)
        out.append(f'<path class="edge" marker-end="url(#{aid})" '
                   f'd="M{sx:.1f} {sy:.1f} Q{control[0]:.1f} {control[1]:.1f} {ex:.1f} {ey:.1f}"/>')
        lx = (x1 + x2) / 2 + px * (bend / 2 + 12)
        ly = (y1 + y2) / 2 + py * (bend / 2 + 12)
        out.append(f'<text class="lbl" x="{lx:.1f}" y="{ly:.1f}">{html.escape(label)}</text>')

    sx, sy = pos[start]
    out.append(f'<line class="init" marker-end="url(#{iid})" x1="{sx - rx[start] - 46:.1f}" '
               f'y1="{sy:.1f}" x2="{sx - rx[start] - 2:.1f}" y2="{sy:.1f}"/>')
    for subset in order:
        cx, cy = pos[subset]
        css = "node" + (" start" if subset == start else "") + \
              (" final" if subset & nfa.final else "") + ("" if subset else " dead")
        out.append(f'<g class="{css}"><ellipse class="body" cx="{cx:.1f}" cy="{cy:.1f}" '
                   f'rx="{rx[subset]:.1f}" ry="{NODE_RY}"/>')
        if subset & nfa.final:
            out.append(f'<ellipse class="ring" cx="{cx:.1f}" cy="{cy:.1f}" '
                       f'rx="{rx[subset] - 5:.1f}" ry="{NODE_RY - 5}"/>')
        out.append(f'<text x="{cx:.1f}" y="{cy:.1f}">{html.escape(pretty(subset))}</text></g>')
    out.append("</svg>")
    return "".join(out)


def cell(subset):
    text = html.escape(pretty(subset))
    return f'<td class="mono{"" if subset else " empty"}">{text}</td>'


def badges(is_start, is_final):
    return ('<span class="badge b-start">start</span>' if is_start else "") + \
           ('<span class="badge b-final">final</span>' if is_final else "")


def case_section(index, nfa, start, order, table):
    head = "".join(f"<th>{html.escape(a)}</th>" for a in nfa.alphabet)
    dfa_rows = "".join(
        f'<tr><td class="m">{badges(s == start, bool(s & nfa.final))}</td>'
        f'<td class="mono"><b>{html.escape(pretty(s))}</b></td>'
        + "".join(cell(table[s][a]) for a in nfa.alphabet) + "</tr>"
        for s in order)
    nfa_rows = "".join(
        f'<tr><td class="m">{badges(q in nfa.initial, q in nfa.final)}</td>'
        f'<td class="mono"><b>{q}</b></td>'
        + "".join(cell(nfa.delta[q][a]) for a in nfa.alphabet) + "</tr>"
        for q in range(1, nfa.n + 1))
    finals = sum(1 for s in order if s & nfa.final)
    chips = "".join(f'<span class="chip">{k} <b>{html.escape(v)}</b></span>' for k, v in [
        ("NFA states", str(nfa.n)), ("Alphabet", " ".join(nfa.alphabet)),
        ("DFA states", str(len(order))), ("Final states", str(finals)),
        ("Start", pretty(start))])
    return f"""<section class="card"><h2>Case {index}</h2><div class="chips">{chips}</div>
<h3>Diagram</h3><div class="scroll">{diagram(index, nfa, start, order, table)}</div>
<div class="legend"><span>→ initial state</span><span>◎ double ring = final state</span>
<span>┅ dashed = empty set ∅ (printed as 0 in the console)</span></div>
<h3>Transition table (DFA)</h3><div class="scroll"><table><thead><tr><th class="m"></th>
<th>State</th>{head}</tr></thead><tbody>{dfa_rows}</tbody></table></div>
<details><summary>Input NFA</summary><div class="scroll" style="margin-top:12px"><table><thead>
<tr><th class="m"></th><th>State</th>{head}</tr></thead><tbody>{nfa_rows}</tbody></table></div>
</details></section>"""


def build_html(results):
    sections = "".join(case_section(i, *r) for i, r in enumerate(results, 1))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Subset Construction - NFA to DFA</title><style>{CSS}</style></head>
<body><header><div class="in"><h1>Subset Construction</h1>
<p>NFA → DFA · {len(results)} case{"s" if len(results) != 1 else ""}</p></div></header>
<main>{sections}</main>
<footer>Generated by subset_construction.py · SI2002 Formal Languages</footer></body></html>
"""


def main():
    args = sys.argv[1:]
    html_path = None
    if args[:1] == ["--html"]:
        html_path = args[1] if len(args) > 1 else "output.html"
    lines = [l for l in sys.stdin.read().splitlines() if l.strip()]
    results = []
    for nfa in read_cases(lines):
        result = (nfa, *subset_construction(nfa))
        print("\n".join(render(*result)))
        results.append(result)
    if html_path:
        Path(html_path).write_text(build_html(results), encoding="utf-8")


if __name__ == "__main__":
    main()
