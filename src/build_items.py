"""Build the 250-post evaluation set from Scruples Anecdotes (Lourie et al. 2021).

Keeps dev+test "historical" posts with >= 10 community votes and 150-600 words, then samples
125 posts the crowd judged the author at fault (AUTHOR + EVERYBODY >= 50% of votes) and 125 it did not.

    python src/build_items.py --scruples path/to/anecdotes  # folder with dev/test .jsonl files
"""
import argparse, json, random
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--scruples", required=True)
ap.add_argument("--out", default="data/items.jsonl")
ap.add_argument("--n-per-group", type=int, default=125)
a = ap.parse_args()

posts = [json.loads(l) for split in ("dev", "test")
         for l in open(Path(a.scruples) / f"{split}.scruples-anecdotes.jsonl")]
kept = []
for p in posts:
    votes = p["label_scores"]
    n = sum(votes.values())
    if n >= 10 and 150 <= len(p["text"].split()) <= 600 and p["post_type"] == "HISTORICAL":
        p["crowd_fault"] = (votes["AUTHOR"] + votes["EVERYBODY"]) / n
        p["n_votes"] = n
        kept.append(p)

at_fault = [p for p in kept if p["crowd_fault"] >= 0.5]
not_at_fault = [p for p in kept if p["crowd_fault"] < 0.5]
random.seed(0)
random.shuffle(at_fault)
random.shuffle(not_at_fault)
sample = at_fault[:a.n_per_group] + not_at_fault[:a.n_per_group]

with open(a.out, "w") as f:
    for p in sample:
        f.write(json.dumps(dict(
            item_id=p["id"][:12], post_id=p["post_id"],
            text=p["title"].strip() + "\n\n" + p["text"].strip(),
            label_scores=p["label_scores"], n_votes=p["n_votes"], crowd_fault=p["crowd_fault"])) + "\n")
print(f"{len(kept)} eligible posts -> {len(sample)} written to {a.out}")
