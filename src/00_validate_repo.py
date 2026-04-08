"""checks required files/folders exist"""
import os

REQUIRED_FILES = [
    "data/reviews_clean.jsonl",
    "data/review_groups_auto.json",
    "personas/personas_auto.json",
    "spec/spec_auto.md",
    "tests/tests_auto.json",
    "tests/tests_manual.json",
    "tests/tests_hybrid.json",
    "metrics/metrics_summary.json"
]

print("Checking repository structure...\n")

missing = []

for file in REQUIRED_FILES:
    if os.path.exists(file):
        print("OK:", file)
    else:
        print("MISSING:", file)
        missing.append(file)

if missing:
    print("\nRepository incomplete.")
else:
    print("\nRepository validation successful.")