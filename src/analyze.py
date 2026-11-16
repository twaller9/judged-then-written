"""Summarise verdict reads: does the verdict change between before writing and after the reply, and does ownership matter?

P(fault) = P(YTA) + P(ESH). Unit = post; paired differences; 95% bootstrap CIs over posts.
    python src/analyze.py                      # all models/pairs found in results/verdicts
Writes results/summary.md
"""
import json, random, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAIRS = {"own": "other", "own_plain": "reddit_plain"}  # own framing -> matched third-party framing
items = {r["item_id"]: r for r in map(json.loads, open(ROOT / "data/items.jsonl"))}


def ci(xs, n=2000):
    random.seed(0)
    m = sum(xs) / len(xs)
    b = sorted(sum(random.choice(xs) for _ in xs) / len(xs) for _ in range(n))
    return f"{m:+.3f} [{b[int(.025 * n)]:+.3f}, {b[int(.975 * n)]:+.3f}]"


def load(path):
    d = {}
    for r in map(json.loads, open(path)):
        d.setdefault(r["item_id"], {})[r["framing"]] = {x["frac"]: x["p"]["YTA"] + x["p"]["ESH"] for x in r["reads"]}
    return d


def addressing(tag, framing):
    """Manipulation check: share of replies whose first sentence speaks to the reader as the writer."""
    rs = [r for r in map(json.loads, open(ROOT / "results/replies" / f"{tag}.jsonl")) if r["framing"] == framing]
    first = [re.split(r"(?<=[.!?])\s", r["reply"].strip(), maxsplit=1)[0] for r in rs]
    return sum(bool(re.search(r"\b(you|your|you're)\b", s, re.I)) for s in first), len(rs)


out = ["# Results summary", ""]
for path in sorted((ROOT / "results/verdicts").glob("*.jsonl")):
    if path.stem.endswith("_masked"):
        continue
    tag, d = path.stem, load(path)
    for own, other in PAIRS.items():
        ids = [i for i in d if own in d[i] and other in d[i]]
        if not ids:
            continue
        fracs = sorted(set(d[ids[0]][own]) & set(d[ids[0]][other]))
        first, last = fracs[0], fracs[-1]
        cf = {i: items[i]["crowd_fault"] for i in ids}
        out += [f"## {tag}: `{own}` vs `{other}` (n = {len(ids)} posts; crowd says at fault on {sum(v >= .5 for v in cf.values())})", ""]
        for fr in (own, other):
            k, n = addressing(tag, fr)
            out.append(f"- Manipulation check, `{fr}`: reply addresses the reader as the writer in {k}/{n}")
        out += ["", "Mean P(fault) by point in the reply (crowd mean " + f"{sum(cf.values()) / len(ids):.3f}):", "",
                "| framing | " + " | ".join(f"{int(f * 100)}%" for f in fracs) + " |", "|---|" + "---|" * len(fracs)]
        for fr in (own, other):
            out.append(f"| {fr} | " + " | ".join(f"{sum(d[i][fr][f] for i in ids) / len(ids):.3f}" for f in fracs) + " |")
        out += ["",
                f"- Ownership effect before writing (own − other): {ci([d[i][own][first] - d[i][other][first] for i in ids])}",
                f"- Ownership effect after reply (own − other): {ci([d[i][own][last] - d[i][other][last] for i in ids])}",
                f"- Writing effect, `{own}` (after − before): {ci([d[i][own][last] - d[i][own][first] for i in ids])}",
                f"- Writing effect, `{other}` (after − before): {ci([d[i][other][last] - d[i][other][first] for i in ids])}",
                f"- Writing × ownership: {ci([(d[i][own][last] - d[i][own][first]) - (d[i][other][last] - d[i][other][first]) for i in ids])}",
                "", "Agreement with the crowd majority (P(fault) ≥ 0.5 vs crowd share ≥ 0.5):", "",
                "| crowd says | framing | before | after |", "|---|---|---|---|"]
        for name, sel in (("at fault", lambda i: cf[i] >= .5), ("not at fault", lambda i: cf[i] < .5)):
            g = [i for i in ids if sel(i)]
            for fr in (own, other):
                acc = lambda f: sum((d[i][fr][f] >= .5) == (cf[i] >= .5) for i in g) / len(g)
                out.append(f"| {name} (n={len(g)}) | {fr} | {acc(first):.0%} | {acc(last):.0%} |")
        masked = path.with_name(f"{tag}_masked.jsonl")
        if masked.exists():
            dm = load(masked)
            mids = [i for i in ids if own in dm.get(i, {}) and other in dm.get(i, {})]
            if mids:
                out += ["", f"Copying control (verdict phrases deleted from the reply, n = {len(mids)}):", ""]
                for fr in (own, other):
                    out.append(f"- `{fr}` P(fault) after reply: original {sum(d[i][fr][last] for i in mids) / len(mids):.3f}, "
                               f"masked {sum(dm[i][fr][last] for i in mids) / len(mids):.3f}; "
                               f"writing effect with masking {ci([dm[i][fr][last] - d[i][fr][first] for i in mids])}")
        out.append("")

(ROOT / "results/summary.md").write_text("\n".join(out))
print("\n".join(out))
