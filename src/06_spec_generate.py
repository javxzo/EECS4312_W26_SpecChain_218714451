"""Generates structured requirements from personas."""

import json
import os
import re
import requests

# ── Config ───────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

PERSONAS_FILE = "personas/personas_auto.json"
GROUPS_FILE = "data/review_groups_auto.json"
SPEC_OUT = "spec/spec_auto.md"

REQS_PER_PERSONA = 2


# ── Helpers ──────────────────────────────────────────────────────────────
def call_groq(system_prompt, user_prompt):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "temperature": 0.3,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def extract_json_block(text):

    match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
    if match:
        return match.group(1)

    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1:
        return text[start:end + 1]

    return text


def format_requirement(req):

    return (
        f"# Requirement ID: {req['requirement_id']}\n"
        f"* Description: [{req['description']}]\n"
        f"* Source Persona: [{req['source_persona']}]\n"
        f"* Traceability: [{req['traceability']}]\n"
        f"* Acceptance Criteria: [{req['acceptance_criteria']}]\n"
        "---"
    )


# ── Requirement generation ───────────────────────────────────────────────
def generate_specs(personas, group_map):

    all_reqs = []
    counter = 1

    system_prompt = (
        "You are a requirements engineering expert. "
        "Write precise, testable functional requirements following IEEE style. "
        "Each requirement MUST start with 'The system shall'. "
        "Each must include acceptance criteria using Given/When/Then."
    )

    for persona in personas:

        group_id = persona.get("derived_from_group", "")
        theme = group_map.get(group_id, {}).get("theme", "")

        user_prompt = f"""
Persona: {persona['name']}
Description: {persona['description']}
Goals: {persona.get('goals', [])}
Pain Points: {persona.get('pain_points', [])}
Constraints: {persona.get('constraints', [])}

Derived review theme: {theme}

Generate EXACTLY {REQS_PER_PERSONA} requirements.

Return ONLY JSON:

[
  {{
    "description": "The system shall ...",
    "acceptance_criteria": [
      "Given ... When ... Then ..."
    ]
  }}
]
"""

        print("Generating for persona:", persona["name"])

        attempts = 0
        parsed = []

        while attempts < 3:

            raw = call_groq(system_prompt, user_prompt)
            json_block = extract_json_block(raw)

            try:
                parsed = json.loads(json_block)
            except Exception:
                parsed = []

            if isinstance(parsed, list) and len(parsed) >= REQS_PER_PERSONA:
                break

            attempts += 1
            print("Retrying requirement generation...")

        if not isinstance(parsed, list):
            parsed = []

        for item in parsed[:REQS_PER_PERSONA]:

            description = item.get("description", "").strip()
            ac = item.get("acceptance_criteria", "")

            if isinstance(ac, list):
                ac = " | ".join(ac)

            if not ac:
                ac = "Given the feature is implemented When the user performs the action Then the system satisfies the requirement."

            req = {
                "requirement_id": f"FR_auto_{counter}",
                "description": description,
                "source_persona": persona["name"],
                "traceability": f"Derived from review group {group_id}",
                "acceptance_criteria": ac,
            }

            all_reqs.append(req)
            counter += 1

    return all_reqs


# ── Main ─────────────────────────────────────────────────────────────────
def main():

    if not GROQ_API_KEY:
        raise EnvironmentError("Set GROQ_API_KEY")

    personas = json.load(open(PERSONAS_FILE))["personas"]

    groups = json.load(open(GROUPS_FILE))["groups"]
    group_map = {g["group_id"]: g for g in groups}

    requirements = generate_specs(personas, group_map)

    os.makedirs("spec", exist_ok=True)

    with open(SPEC_OUT, "w") as f:
        for r in requirements:
            f.write(format_requirement(r) + "\n")

    print("Saved", len(requirements), "requirements")


if __name__ == "__main__":
    main()