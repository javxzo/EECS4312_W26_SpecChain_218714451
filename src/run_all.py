"""runs the full pipeline end-to-end"""

import subprocess
import sys
import os

# Ensure we run from the repo root regardless of where the script is called from
# REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
# os.chdir(REPO_ROOT)

PYTHON = sys.executable

STEPS = [
    # (script, description, produces)
    (
        "src/02_clean.py",
        "Step 1 — Clean raw reviews",
        ["data/reviews_clean.jsonl"],
    ),
    (
        "src/05_personas_auto.py",
        "Step 2 — Auto-group reviews and generate personas",
        ["data/review_groups_auto.json", "personas/personas_auto.json", "prompts/prompt_auto.json"],
    ),
    (
        "src/06_spec_generate.py",
        "Step 3 — Generate specifications from auto personas",
        ["spec/spec_auto.md"],
    ),
    (
        "src/07_tests_generate.py",
        "Step 4 — Generate validation tests from auto spec",
        ["tests/tests_auto.json"],
    ),
    (
        "src/08_metrics.py",
        "Step 5 — Compute metrics for all three pipelines",
        [
            "metrics/metrics_manual.json",
            "metrics/metrics_auto.json",
            "metrics/metrics_hybrid.json",
            "metrics/metrics_summary.json",
        ],
    ),
]


def run_step(script: str, description: str, produces: list[str]) -> bool:
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"  Running: python {script}")
    print(f"{'='*60}")

    result = subprocess.run([PYTHON, script], capture_output=False)

    if result.returncode != 0:
        print(f"\n[ERROR] {script} failed with exit code {result.returncode}")
        return False

    # Confirm expected outputs exist
    for path in produces:
        if os.path.exists(path):
            print(f"  [OK] {path}")
        else:
            print(f"  [MISSING] {path} was not created")

    return True


def main():
    print("SpecChain — Automated Pipeline")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")

    # Check GROQ API key is set before starting LLM steps
    if not os.environ.get("GROQ_API_KEY"):
        print(
            "\n[ERROR] GROQ_API_KEY environment variable is not set.\n"
            "Set it before running:\n"
            "  Windows:  $env:GROQ_API_KEY = 'PUT YOUR API KEY HERE'\n"
            "  Mac/Linux: export GROQ_API_KEY='PUT YOUR API KEY HERE'"
        )
        sys.exit(1)

    for script, description, produces in STEPS:
        success = run_step(script, description, produces)
        if not success:
            print(f"\n[ABORTED] Pipeline stopped at: {script}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Pipeline complete. All steps finished successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
