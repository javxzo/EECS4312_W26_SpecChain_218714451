"""computes metrics: coverage/traceability/ambiguity/testability"""

import json
import os
import re

# ── Paths ─────────────────────────────────────────────────────────────────────
CLEAN_FILE        = "data/reviews_clean.jsonl"
DATASET_META      = "data/dataset_metadata.json"

PIPELINES = {
    "manual": {
        "groups":    "data/review_groups_manual.json",
        "personas":  "personas/personas_manual.json",
        "spec":      "spec/spec_manual.md",
        "tests":     "tests/tests_manual.json",
        "out":       "metrics/metrics_manual.json",
    },
    "automated": {
        "groups":    "data/review_groups_auto.json",
        "personas":  "personas/personas_auto.json",
        "spec":      "spec/spec_auto.md",
        "tests":     "tests/tests_auto.json",
        "out":       "metrics/metrics_auto.json",
    },
    "hybrid": {
        "groups":    "data/review_groups_hybrid.json",
        "personas":  "personas/personas_hybrid.json",
        "spec":      "spec/spec_hybrid.md",
        "tests":     "tests/tests_hybrid.json",
        "out":       "metrics/metrics_hybrid.json",
    },
}

VAGUE_TERMS = {
    "fast", "easy", "easily", "better", "user-friendly", "friendly",
    "simple", "simply", "smooth", "smoothly", "acceptable", "quickly",
    "quick", "clear", "clearly", "consistent", "consistently",
    "accessible", "seamless", "seamlessly", "intuitive", "intuitively",
}

SUMMARY_OUT = "metrics/metrics_summary.json"


# ── Helpers ───────────────────────────────────────────────────────────────────
def count_clean_reviews(path: str) -> int:
    if not os.path.exists(path):
        return 0
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_spec(path: str) -> list[dict]:
    """Return list of requirement dicts parsed from a spec .md file."""
    if not os.path.exists(path):
        return []
    content = open(path, encoding="utf-8").read()
    blocks = [b.strip() for b in content.split("---") if b.strip()]
    reqs = []
    for block in blocks:
        req_id = re.search(r"Requirement ID:\s*(\S+)", block)
        desc   = re.search(r"Description:\s*\[(.+?)\]", block)
        ac     = re.search(r"Acceptance Criteria:\s*\[(.+?)\]", block)
        persona = re.search(r"Source Persona:\s*\[(.+?)\]", block)
        if req_id and desc:
            reqs.append({
                "id":       req_id.group(1),
                "desc":     desc.group(1),
                "ac":       ac.group(1) if ac else "",
                "persona":  persona.group(1) if persona else "",
            })
    return reqs


def compute_ambiguity(reqs: list[dict]) -> float:
    """Proportion of requirements containing at least one vague term."""
    if not reqs:
        return 0.0
    ambig = 0
    for req in reqs:
        text = (req["desc"] + " " + req["ac"]).lower()
        words = set(re.findall(r"\b\w+\b", text))
        if words & VAGUE_TERMS:
            ambig += 1
    return round(ambig / len(reqs), 4)


def compute_review_coverage(groups_data, total_reviews: int) -> float:
    """Ratio of unique review IDs covered by groups to total reviews."""
    if not groups_data or total_reviews == 0:
        return 0.0
    covered = set()
    for g in groups_data.get("groups", []):
        for rid in g.get("review_ids", []):
            covered.add(rid)
    return round(len(covered) / total_reviews, 4)


def compute_traceability_ratio(reqs: list[dict], personas_data) -> float:
    """Proportion of requirements that reference a known persona."""
    if not reqs or not personas_data:
        return 0.0
    known_personas = {
        p["name"].lower()
        for p in personas_data.get("personas", [])
    }
    traced = sum(
        1 for r in reqs
        if r["persona"].lower() in known_personas
    )
    return round(traced / len(reqs), 4)


def compute_testability_rate(reqs: list[dict], tests_data) -> float:
    """Proportion of requirements that have at least one test."""
    if not reqs or not tests_data:
        return 0.0
    tested_req_ids = {t["requirement_id"] for t in tests_data.get("tests", [])}
    tested = sum(1 for r in reqs if r["id"] in tested_req_ids)
    return round(tested / len(reqs), 4)


def count_traceability_links(reqs: list[dict], tests_data) -> int:
    """Count explicit traceability links: each req->persona ref + each test->req ref."""
    persona_links = sum(1 for r in reqs if r["persona"])
    test_links = len(tests_data.get("tests", [])) if tests_data else 0
    return persona_links + test_links


# ── Main ──────────────────────────────────────────────────────────────────────
def compute_pipeline_metrics(name: str, paths: dict, total_reviews: int) -> dict:
    groups_data   = load_json(paths["groups"])
    personas_data = load_json(paths["personas"])
    tests_data    = load_json(paths["tests"])
    reqs          = parse_spec(paths["spec"])

    persona_count    = len(personas_data.get("personas", [])) if personas_data else 0
    requirements_count = len(reqs)
    tests_count      = len(tests_data.get("tests", [])) if tests_data else 0
    traceability_links = count_traceability_links(reqs, tests_data)
    review_coverage  = compute_review_coverage(groups_data, total_reviews)
    traceability_ratio = compute_traceability_ratio(reqs, personas_data)
    testability_rate = compute_testability_rate(reqs, tests_data)
    ambiguity_ratio  = compute_ambiguity(reqs)

    return {
        "pipeline":            name,
        "dataset_size":        total_reviews,
        "persona_count":       persona_count,
        "requirements_count":  requirements_count,
        "tests_count":         tests_count,
        "traceability_links":  traceability_links,
        "review_coverage":     review_coverage,
        "traceability_ratio":  traceability_ratio,
        "testability_rate":    testability_rate,
        "ambiguity_ratio":     ambiguity_ratio,
    }


def main():
    total_reviews = count_clean_reviews(CLEAN_FILE)
    print(f"Total cleaned reviews: {total_reviews}")

    os.makedirs("metrics", exist_ok=True)
    summary = {}

    for name, paths in PIPELINES.items():
        print(f"\nComputing metrics for: {name}")
        metrics = compute_pipeline_metrics(name, paths, total_reviews)

        # Write individual metrics file
        with open(paths["out"], "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"  Saved to {paths['out']}")

        # Print summary to console
        for k, v in metrics.items():
            if k != "pipeline":
                print(f"  {k}: {v}")

        # Add to summary (exclude top-level "pipeline" key)
        summary[name] = {k: v for k, v in metrics.items() if k != "pipeline"}

    # Write summary file
    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary to {SUMMARY_OUT}")
    print("\nDone.")


if __name__ == "__main__":
    main()