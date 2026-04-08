"""Generates validation tests from requirements."""

import json
import os
import re
import requests

# ── Config ───────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SPEC_FILE = "spec/spec_auto.md"
TESTS_OUT = "tests/tests_auto.json"

TESTS_PER_REQ = 2


# ── Helpers ──────────────────────────────────────────────────────────────
def call_groq(system_prompt, user_prompt):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "temperature": 0.3,
        "max_tokens": 2048,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    return response.json()["choices"][0]["message"]["content"]


def extract_json(text):

    match = re.search(r"\[[\s\S]*\]", text)

    if match:
        return match.group(0)

    return text


def parse_spec():

    content = open(SPEC_FILE).read()

    blocks = content.split("---")

    reqs = []

    for block in blocks:

        rid = re.search(r"Requirement ID:\s*(\S+)", block)
        desc = re.search(r"Description:\s*\[(.+?)\]", block)
        ac = re.search(r"Acceptance Criteria:\s*\[(.+?)\]", block)

        if rid and desc:

            reqs.append(
                {
                    "requirement_id": rid.group(1),
                    "description": desc.group(1),
                    "acceptance_criteria": ac.group(1) if ac else "",
                }
            )

    return reqs


def fallback_tests(req):

    return [
        {
            "scenario": "Normal usage scenario",
            "steps": [
                "Open Headspace",
                "Navigate to the feature",
                "Perform the main action"
            ],
            "expected_result": req["acceptance_criteria"]
        },
        {
            "scenario": "Edge case scenario",
            "steps": [
                "Open Headspace",
                "Trigger the feature under unusual conditions",
                "Observe system behavior"
            ],
            "expected_result": req["acceptance_criteria"]
        }
    ]


# ── Test generation ──────────────────────────────────────────────────────
def generate_tests(requirements):

    all_tests = []
    counter = 1

    system_prompt = (
        "You are a QA engineer writing test cases for a mobile mindfulness app."
    )

    for req in requirements:

        prompt = f"""
Requirement: {req['description']}
Acceptance Criteria: {req['acceptance_criteria']}

Write EXACTLY {TESTS_PER_REQ} test scenarios.

Return JSON:

[
  {{
    "scenario": "...",
    "steps": ["..."],
    "expected_result": "..."
  }}
]
"""

        attempts = 0
        scenarios = []

        while attempts < 3:

            raw = call_groq(system_prompt, prompt)

            try:
                scenarios = json.loads(extract_json(raw))
            except:
                scenarios = []

            if isinstance(scenarios, list) and len(scenarios) >= TESTS_PER_REQ:
                break

            attempts += 1

        if len(scenarios) < TESTS_PER_REQ:
            scenarios = fallback_tests(req)

        for i, sc in enumerate(scenarios[:TESTS_PER_REQ]):

            all_tests.append(
                {
                    "test_id": f"T_auto_{counter}_{i+1}",
                    "requirement_id": req["requirement_id"],
                    "scenario": sc.get("scenario", ""),
                    "steps": sc.get("steps", []),
                    "expected_result": sc.get("expected_result", ""),
                }
            )

        counter += 1

    return all_tests


# ── Main ─────────────────────────────────────────────────────────────────
def main():

    requirements = parse_spec()

    if not requirements:
        raise ValueError("No requirements found")

    tests = generate_tests(requirements)

    os.makedirs("tests", exist_ok=True)

    with open(TESTS_OUT, "w") as f:
        json.dump({"tests": tests}, f, indent=2)

    print("Saved", len(tests), "tests")


if __name__ == "__main__":
    main()