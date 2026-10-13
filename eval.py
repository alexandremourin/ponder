"""Ponder evaluation harness.

Measures the two halves of a RAG system separately:

  * Retrieval quality  — recall@k and MRR against gold source files, plus
    retrieval latency. Needs NO API key (local embeddings only).
  * Answer quality     — end-to-end correctness via an LLM-as-judge, plus
    end-to-end latency and cost per query. Needs an LLM key.

Usage:
    python eval.py --retrieval-only      # no key required
    python eval.py                       # full eval (needs ANTHROPIC/OPENAI key)
    python eval.py --limit 5             # quick smoke test

Outputs a printed report, assets/eval_results.json, and a PNG chart in assets/.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from ponder.config import ASSETS_DIR, EVAL_FILE, has_llm_key

HARD_FILE = EVAL_FILE.parent / "eval_hard.jsonl"
from ponder.vectorstore import VectorStore

KS = (1, 3, 5)


def load_eval(path: Path = EVAL_FILE) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


# --- Retrieval metrics -------------------------------------------------------
def eval_retrieval(rows: list[dict], k: int = 5) -> dict:
    rows = [r for r in rows if r.get("sources")]  # unanswerable rows have no gold source
    store = VectorStore()
    if store.count() == 0:
        raise RuntimeError("Index is empty. Run `python -m ponder.ingest` first.")

    recall_hits = {kk: 0 for kk in KS}
    reciprocal_ranks: list[float] = []
    latencies: list[float] = []

    for row in rows:
        gold = set(row["sources"])
        t0 = time.perf_counter()
        docs = store.search(row["question"], k=max(k, max(KS)))
        latencies.append((time.perf_counter() - t0) * 1000)  # ms

        ranked_sources = [d.source for d in docs]
        # recall@k: did a gold source appear within the top kk?
        for kk in KS:
            if gold & set(ranked_sources[:kk]):
                recall_hits[kk] += 1
        # reciprocal rank of the first gold hit
        rr = 0.0
        for idx, src in enumerate(ranked_sources, start=1):
            if src in gold:
                rr = 1.0 / idx
                break
        reciprocal_ranks.append(rr)

    n = len(rows)
    return {
        "n": n,
        "recall_at_k": {str(kk): round(recall_hits[kk] / n, 3) for kk in KS},
        "mrr": round(statistics.mean(reciprocal_ranks), 3),
        "retrieval_latency_ms_mean": round(statistics.mean(latencies), 1),
        "retrieval_latency_ms_p95": round(sorted(latencies)[int(0.95 * (n - 1))], 1),
    }


# --- Answer quality (needs an LLM) ------------------------------------------
def _abstain_schema():
    from pydantic import BaseModel, Field

    class Abstention(BaseModel):
        abstained: bool = Field(description="True if the system clearly said the documents do not contain the answer, instead of inventing one.")
        reasoning: str = Field(description="One short sentence.")

    return Abstention


def _judge_schema():
    from pydantic import BaseModel, Field

    class Judgement(BaseModel):
        correct: bool = Field(description="True if the answer is factually correct and addresses the question, judged against the reference.")
        score: float = Field(description="Quality from 0.0 to 1.0.")
        reasoning: str = Field(description="One short sentence justifying the verdict.")

    return Judgement


def eval_answers(rows: list[dict]) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    from ponder.llm import get_llm
    from ponder.pipeline import ask

    Judgement = _judge_schema()
    judge = get_llm(temperature=0).with_structured_output(Judgement)
    judge_sys = (
        "You are a strict grader for a question-answering system. Compare the "
        "system's answer to the reference answer. Mark it correct only if it is "
        "factually accurate and actually addresses the question. Minor wording "
        "differences are fine; missing or wrong facts are not."
    )

    Abstention = _abstain_schema()
    abstain_judge = get_llm(temperature=0).with_structured_output(Abstention)

    scores: list[float] = []
    correct = 0
    latencies: list[float] = []
    costs: list[float] = []
    source_hits = 0
    answerable = 0
    unanswerable = 0
    abstained = 0
    all_gold_cited = 0
    details = []

    for i, row in enumerate(rows, start=1):
        result = ask(row["question"])
        latencies.append(result.latency_s)
        costs.append(result.cost_usd)

        if row.get("type") == "unanswerable":
            unanswerable += 1
            verdict = abstain_judge.invoke(
                [
                    SystemMessage(content="You check whether a question-answering system abstained. The question has NO answer in its documents. Did the system say so clearly, rather than invent an answer?"),
                    HumanMessage(content=f"Question:\n{row['question']}\n\nSystem answer:\n{result.answer}"),
                ]
            )
            abstained += int(verdict.abstained)
            print(f"  [{i}/{len(rows)}] {'ABSTAINED' if verdict.abstained else 'INVENTED '} {result.latency_s:.1f}s ${result.cost_usd:.4f}")
            details.append({"question": row["question"], "type": "unanswerable", "abstained": verdict.abstained, "cited_sources": result.sources})
            continue

        answerable += 1
        if set(row["sources"]) & set(result.sources):
            source_hits += 1
        if set(row["sources"]) <= set(result.sources):
            all_gold_cited += 1

        verdict = judge.invoke(
            [
                SystemMessage(content=judge_sys),
                HumanMessage(
                    content=(
                        f"Question:\n{row['question']}\n\n"
                        f"Reference answer:\n{row['answer']}\n\n"
                        f"System answer:\n{result.answer}"
                    )
                ),
            ]
        )
        scores.append(verdict.score)
        correct += int(verdict.correct)
        print(
            f"  [{i}/{len(rows)}] {'OK ' if verdict.correct else 'MISS'} "
            f"score={verdict.score:.2f} {result.latency_s:.1f}s ${result.cost_usd:.4f}"
        )
        details.append(
            {
                "question": row["question"],
                "type": row.get("type", "standard"),
                "correct": verdict.correct,
                "score": verdict.score,
                "cited_sources": result.sources,
                "gold_sources": row["sources"],
            }
        )

    n = answerable
    out = {
        "n_answerable": n,
        "accuracy": round(correct / n, 3) if n else None,
        "mean_judge_score": round(statistics.mean(scores), 3) if scores else None,
        "answer_source_hit_rate": round(source_hits / n, 3) if n else None,
        "all_gold_sources_cited_rate": round(all_gold_cited / n, 3) if n else None,
        "e2e_latency_s_mean": round(statistics.mean(latencies), 2),
        "cost_usd_per_query_mean": round(statistics.mean(costs), 5),
        "cost_usd_total": round(sum(costs), 4),
        "details": details,
    }
    if unanswerable:
        out["n_unanswerable"] = unanswerable
        out["abstention_rate"] = round(abstained / unanswerable, 3)
    return out


# --- Reporting ---------------------------------------------------------------
def make_chart(results: dict, out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    retr = results["retrieval"]
    has_answers = "answers" in results

    ncols = 2 if has_answers else 1
    fig, axes = plt.subplots(1, ncols, figsize=(5.5 * ncols, 4.2), squeeze=False)
    axes = list(axes[0])  # squeeze=False -> always a 2D array; take the single row

    accent = "#d4a44a"

    # Recall@k chart
    ks = list(retr["recall_at_k"].keys())
    vals = [retr["recall_at_k"][k] for k in ks]
    ax = axes[0]
    bars = ax.bar([f"recall@{k}" for k in ks], vals, color=accent, width=0.55)
    ax.set_ylim(0, 1.05)
    ax.set_title("Retrieval quality", fontsize=12, fontweight="bold")
    ax.bar_label(bars, fmt="%.2f", padding=3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(1.0, color="#cccccc", lw=0.8, ls="--")

    # Answer quality chart
    if has_answers:
        ans = results["answers"]
        ax2 = axes[1]
        labels = ["accuracy", "judge score", "source hit"]
        vals2 = [ans["accuracy"], ans["mean_judge_score"], ans["answer_source_hit_rate"]]
        bars2 = ax2.bar(labels, vals2, color="#2c2c2c", width=0.55)
        ax2.set_ylim(0, 1.05)
        ax2.set_title("Answer quality (LLM-judge)", fontsize=12, fontweight="bold")
        ax2.bar_label(bars2, fmt="%.2f", padding=3)
        ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Ponder — evaluation results", fontsize=13, fontweight="bold")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130)
    print(f"\nChart saved to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Ponder.")
    parser.add_argument("--retrieval-only", action="store_true", help="Skip the LLM answer eval.")
    parser.add_argument("--limit", type=int, default=0, help="Only evaluate the first N questions.")
    parser.add_argument("--k", type=int, default=5, help="Top-k for retrieval metrics.")
    parser.add_argument("--set", choices=["standard", "hard"], default="standard",
                        help="'standard' = 18 in-domain questions; 'hard' = 10 paraphrased, multi-source and unanswerable questions.")
    args = parser.parse_args()

    rows = load_eval(HARD_FILE if args.set == "hard" else EVAL_FILE)
    if args.limit:
        rows = rows[: args.limit]
    print(f"Loaded {len(rows)} eval questions.\n")

    results: dict = {}

    print("== Retrieval evaluation ==")
    results["retrieval"] = eval_retrieval(rows, k=args.k)
    r = results["retrieval"]
    for kk, v in r["recall_at_k"].items():
        print(f"  recall@{kk}: {v}")
    print(f"  MRR: {r['mrr']}")
    print(f"  retrieval latency: {r['retrieval_latency_ms_mean']} ms (p95 {r['retrieval_latency_ms_p95']} ms)")

    if not args.retrieval_only:
        if not has_llm_key():
            print(
                "\n[skip] No LLM key found — skipping answer evaluation. "
                "Set ANTHROPIC_API_KEY (or OPENAI_API_KEY) and re-run, "
                "or use --retrieval-only to silence this."
            )
        else:
            print("\n== Answer evaluation (end-to-end) ==")
            results["answers"] = eval_answers(rows)
            a = results["answers"]
            print(f"\n  accuracy: {a['accuracy']}")
            print(f"  mean judge score: {a['mean_judge_score']}")
            print(f"  answer source hit rate: {a['answer_source_hit_rate']}")
            print(f"  all gold sources cited: {a['all_gold_sources_cited_rate']}")
            if "abstention_rate" in a:
                print(f"  abstention on unanswerable: {a['abstention_rate']} ({a['n_unanswerable']} questions)")
            print(f"  e2e latency: {a['e2e_latency_s_mean']} s/query")
            print(f"  cost: ${a['cost_usd_per_query_mean']}/query (total ${a['cost_usd_total']})")

    suffix = "" if args.set == "standard" else f"_{args.set}"
    out_json = ASSETS_DIR / f"eval_results{suffix}.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults written to {out_json}")
    make_chart(results, ASSETS_DIR / f"eval_recall{suffix}.png")


if __name__ == "__main__":
    main()
