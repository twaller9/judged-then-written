"""Figure 1: mean P(at fault) across the model's reply, own vs other framing, one panel per model. Writes paper/figure1.svg."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = [("llama31-8b", "Llama-3.1-8B"), ("qwen25-7b", "Qwen2.5-7B")]
SERIES = [("own", '"I wrote this"', "#2a78d6", ""), ("other", '"Someone else wrote this"', "#eb6834", "6 4")]
crowd = [json.loads(l)["crowd_fault"] for l in open(ROOT / "data/items.jsonl")]
crowd_mean = sum(crowd) / len(crowd)

W, H, PW, PH, L, T = 920, 400, 360, 250, 70, 70  # canvas, panel size, left/top margins
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def curve(tag, framing):
    rows = [json.loads(l) for l in open(ROOT / "results/verdicts" / f"{tag}.jsonl")]
    rows = [r for r in rows if r["framing"] == framing]
    fracs = sorted({x["frac"] for x in rows[0]["reads"]})
    return [(f, sum(next(x for x in r["reads"] if x["frac"] == f)["p"]["YTA"] + next(x for x in r["reads"] if x["frac"] == f)["p"]["ESH"] for r in rows) / len(rows)) for f in fracs]


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>',
       f'<text x="{L}" y="28" font-size="17" font-weight="600" fill="{INK}">Chance the model says the author is at fault, as it writes its reply</text>']
for k, (tag, name) in enumerate(MODELS):
    x0 = L + k * (PW + 110)
    px = lambda f: x0 + f * PW
    py = lambda v: T + (1 - v) * PH
    svg.append(f'<text x="{x0}" y="{T - 14}" font-size="14" font-weight="600" fill="{INK}">{name}</text>')
    for v in (0, .25, .5, .75, 1):
        svg.append(f'<line x1="{x0}" x2="{x0 + PW}" y1="{py(v)}" y2="{py(v)}" stroke="{GRID}" stroke-width="1"/>')
        svg.append(f'<text x="{x0 - 8}" y="{py(v) + 4}" font-size="11" fill="{MUTED}" text-anchor="end">{v:.2f}</text>')
    for f in (0, .25, .5, .75, 1):
        svg.append(f'<text x="{px(f)}" y="{T + PH + 18}" font-size="11" fill="{MUTED}" text-anchor="middle">{int(f * 100)}%</text>')
    svg.append(f'<text x="{x0 + PW / 2}" y="{T + PH + 38}" font-size="12" fill="{MUTED}" text-anchor="middle">share of the reply written (0% = before writing)</text>')
    svg.append(f'<line x1="{x0}" x2="{x0 + PW}" y1="{py(crowd_mean)}" y2="{py(crowd_mean)}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="2 3"/>')
    svg.append(f'<text x="{x0 + PW}" y="{py(crowd_mean) + 16}" font-size="11" fill="{MUTED}" text-anchor="end">crowd average {crowd_mean:.2f}</text>')
    for fr, label, color, dash in SERIES:
        pts = curve(tag, fr)
        d = " ".join(f"{px(f):.1f},{py(v):.1f}" for f, v in pts)
        svg.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}" stroke-linejoin="round"/>')
        for f, v in pts:
            svg.append(f'<circle cx="{px(f):.1f}" cy="{py(v):.1f}" r="4.5" fill="{color}" stroke="#fcfcfb" stroke-width="2"/>')
# legend
lx = L
for fr, label, color, dash in SERIES:
    svg.append(f'<line x1="{lx}" x2="{lx + 26}" y1="{H - 20}" y2="{H - 20}" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}"/>')
    svg.append(f'<text x="{lx + 32}" y="{H - 16}" font-size="12" fill="{INK}">{label}</text>')
    lx += 250
svg.append("</svg>")
(ROOT / "paper/figure1.svg").write_text("\n".join(svg))
print("wrote paper/figure1.svg")
