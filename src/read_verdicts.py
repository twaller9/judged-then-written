"""Read the model's verdict before it writes and partway through / after its own reply.

For each reply, cut it at a fraction of its words (0 = nothing written yet, 1 = full reply), close the
assistant turn, add a user turn asking for a one-word verdict, prefill "Verdict:", and score each verdict
string (YTA, NTA, ESH, NAH, INFO) by teacher forcing. Probabilities are renormalised over the five.
No sampling and no LLM judge.

    python src/read_verdicts.py --model ~/models/llama-3.1-8b-instruct-8bit --tag llama31-8b
    python src/read_verdicts.py ... --mask   # copying control: delete explicit verdict phrases first
Writes results/verdicts/<tag>[_masked].jsonl
"""
import argparse, json, re, time
from pathlib import Path
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache, trim_prompt_cache

ROOT = Path(__file__).resolve().parent.parent
VERDICTS = ["YTA", "NTA", "ESH", "NAH", "INFO"]
ASK = "Give your verdict as one word: YTA, NTA, ESH, NAH or INFO."
VERDICT_PHRASES = [
    r"\(?\b(YTA|NTA|ESH|NAH|INFO|AITA)\b\)?",
    r"\b(not\s+(entirely\s+|completely\s+|really\s+|necessarily\s+)?)?(the|an|a bit of an)\s+asshole\b",
    r"\b(not\s+)?(entirely\s+)?(in the wrong|at fault)\b",
]

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--fracs", nargs="+", type=float, default=[0, 0.25, 0.5, 0.75, 1.0])
ap.add_argument("--mask", action="store_true")
a = ap.parse_args()

model, tok = load(str(Path(a.model).expanduser()))
replies = [json.loads(l) for l in open(ROOT / "results/replies" / f"{a.tag}.jsonl")]
out = ROOT / "results/verdicts" / f"{a.tag}{'_masked' if a.mask else ''}.jsonl"
done = {(r["item_id"], r["framing"]) for r in map(json.loads, open(out))} if out.exists() else set()
replies = [r for r in replies if (r["item_id"], r["framing"]) not in done]
vtoks = {v: tok.encode(" " + v, add_special_tokens=False) for v in VERDICTS}


def chat(msgs):
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def verdict_probs(text):
    """Log-prob of each full verdict string after `text`, reusing the prefix cache."""
    cache = make_prompt_cache(model)
    logits = model(mx.array(tok.encode(text, add_special_tokens=False))[None], cache=cache)[0, -1].astype(mx.float32)
    first = logits - mx.logsumexp(logits)
    lp = {}
    for v, t in vtoks.items():
        x = float(first[t[0]].item())
        if len(t) > 1:
            rest = model(mx.array(t[:-1])[None], cache=cache)[0].astype(mx.float32)
            rest = rest - mx.logsumexp(rest, axis=-1, keepdims=True)
            x += sum(float(rest[i, t[i + 1]].item()) for i in range(len(t) - 1))
            trim_prompt_cache(cache, len(t) - 1)
        lp[v] = x
    z = mx.logsumexp(mx.array(list(lp.values()))).item()
    return {v: float(mx.exp(mx.array(lp[v] - z)).item()) for v in VERDICTS}, float(mx.exp(mx.array(z)).item())


t0 = time.time()
with open(out, "a") as f:
    for n, r in enumerate(replies, 1):
        reply = r["reply"]
        if a.mask:
            for pat in VERDICT_PHRASES:
                reply = re.sub(pat, "", reply, flags=re.I)
        words = reply.split(" ")
        reads = []
        for frac in a.fracs:
            partial = " ".join(words[:round(len(words) * frac)]).rstrip()
            msgs = [{"role": "user", "content": r["prompt"]}, {"role": "assistant", "content": partial}, {"role": "user", "content": ASK}]
            p, mass = verdict_probs(chat(msgs) + "Verdict:")
            reads.append(dict(frac=frac, p=p, mass=mass))
        f.write(json.dumps(dict(item_id=r["item_id"], framing=r["framing"], n_words=len(words), reads=reads)) + "\n")
        f.flush()
        if n % 25 == 0 or n == len(replies):
            print(f"  {n}/{len(replies)}  {(time.time() - t0) / 60:.1f} min", flush=True)
