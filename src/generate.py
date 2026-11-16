"""Generate one reply per post and framing with a local MLX model. Resumable.

    python src/generate.py --model ~/models/llama-3.1-8b-instruct-8bit --tag llama31-8b --framings own other
Writes results/replies/<tag>.jsonl
"""
import argparse, json, time
from pathlib import Path
from mlx_lm import load, batch_generate
from mlx_lm.sample_utils import make_sampler

ROOT = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--framings", nargs="+", required=True, help="prompt names in prompts/")
ap.add_argument("--items", default=str(ROOT / "data/items.jsonl"))
ap.add_argument("--temperature", type=float, default=0.7)
ap.add_argument("--max-tokens", type=int, default=800)
ap.add_argument("--batch", type=int, default=16)
a = ap.parse_args()

prompts = {f: (ROOT / "prompts" / f"{f}.txt").read_text() for f in a.framings}
items = [json.loads(l) for l in open(a.items)]
out = ROOT / "results/replies" / f"{a.tag}.jsonl"
done = {(r["item_id"], r["framing"]) for r in map(json.loads, open(out))} if out.exists() else set()
jobs = [(it["item_id"], f, prompts[f].format(story=it["text"]).strip())
        for it in items for f in a.framings if (it["item_id"], f) not in done]
jobs.sort(key=lambda j: len(j[2]))  # similar lengths per batch -> less padding
print(f"{len(jobs)} replies to generate -> {out}")

model, tok = load(str(Path(a.model).expanduser()))
sampler = make_sampler(temp=a.temperature)

def encode(user_text):
    msgs = [{"role": "user", "content": user_text}]
    try:
        s = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        s = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return tok.encode(s, add_special_tokens=False)

t0 = time.time()
for i in range(0, len(jobs), a.batch):
    chunk = jobs[i:i + a.batch]
    texts = batch_generate(model, tok, [encode(p) for _, _, p in chunk], max_tokens=a.max_tokens, sampler=sampler).texts
    with open(out, "a") as f:
        for (iid, fr, p), t in zip(chunk, texts):
            f.write(json.dumps(dict(item_id=iid, framing=fr, prompt=p, reply=t, model=a.model, temperature=a.temperature)) + "\n")
    n = i + len(chunk)
    print(f"  {n}/{len(jobs)}  {(time.time() - t0) / 60:.1f} min", flush=True)
