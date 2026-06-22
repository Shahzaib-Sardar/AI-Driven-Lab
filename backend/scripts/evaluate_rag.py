from __future__ import annotations

import json
import os
import time
from pathlib import Path
from app.services import rag

ROOT = Path(__file__).resolve().parents[2]
PROMPTS_FILE = ROOT / "tests" / "evaluation" / "prompts.txt"
OUTPUT_DIR = ROOT / "tests" / "evaluation" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE = OUTPUT_DIR / "report.md"


def run():
    prompts = []
    if PROMPTS_FILE.exists():
        prompts = [line.strip() for line in PROMPTS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    results = []
    for idx, p in enumerate(prompts, start=1):
        start = time.perf_counter()
        retrieved = rag.retrieve(p, top_k=3)
        elapsed = time.perf_counter() - start
        out = {
            "id": idx,
            "prompt": p,
            "latency_s": round(elapsed, 4),
            "retrieved": retrieved,
        }
        results.append(out)
        # save per-prompt output
        (OUTPUT_DIR / f"output_{idx}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # create a simple markdown report
    lines = ["# RAG Evaluation Report", "", f"Total prompts: {len(results)}", ""]
    avg_latency = sum(r["latency_s"] for r in results) / max(1, len(results))
    lines.append(f"Average latency: {avg_latency:.4f}s")
    lines.append("")
    lines.append("## Results")
    for r in results:
        lines.append(f"### Prompt {r['id']}")
        lines.append(f"- Prompt: {r['prompt']}")
        lines.append(f"- Latency: {r['latency_s']}s")
        lines.append(f"- Top retrievals:")
        for ret in r["retrieved"]:
            title = ret.get("title") or ret.get("metadata", {}).get("source", "unknown")
            score = round(ret.get("score", 0), 4)
            text_preview = (ret.get("text") or "")[:200].replace('\n',' ')
            lines.append(f"  - {title} (score: {score}) - {text_preview}")
        lines.append("")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print("Evaluation complete. Report:", REPORT_FILE)


if __name__ == "__main__":
    run()
