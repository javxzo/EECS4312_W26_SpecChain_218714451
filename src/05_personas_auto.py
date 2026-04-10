"""automated persona generation pipeline"""

import json
import os
import re
import requests
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "PUT YOUR API KEY HERE") # add yours as mine deactivated due to the forks unchangable visibilty 
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

CLEAN_FILE = "data/reviews_clean.jsonl"
GROUPS_OUT = "data/review_groups_auto.json"
PERSONAS_OUT = "personas/personas_auto.json"
PROMPT_OUT = "prompts/prompt_auto.json"

NUM_GROUPS = 5
SAMPLE_SIZE = 200          # reviews sent to LLM for grouping
MIN_PER_GROUP = 10         # minimum reviews assigned per group


# ── Helpers ───────────────────────────────────────────────────────────────────
def call_groq(system_prompt: str, user_prompt: str) -> str:
    """Send a request to the Groq API and return the assistant message text."""
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


def load_reviews(path: str) -> list[dict]:
    reviews = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                reviews.append(json.loads(line))
    return reviews


def extract_json_block(text: str) -> str:
    """Extract the first JSON object or array from a string."""
    # Try to find a JSON block wrapped in ```json ... ``` or just raw JSON
    match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text)
    if match:
        return match.group(1)
    # Fallback: find first { or [ and parse from there
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        idx = text.find(start_char)
        if idx != -1:
            depth = 0
            for i, ch in enumerate(text[idx:], idx):
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                if depth == 0:
                    return text[idx:i + 1]
    return text


# ── Step 4.1: Group reviews automatically ─────────────────────────────────────
def group_reviews(reviews: list[dict]) -> dict:
    """Use LLM to assign reviews to thematic groups."""

    # Sample for prompt (keep token cost manageable)
    sample = reviews[:SAMPLE_SIZE]
    numbered = "\n".join(f"{r['id']}: {r['review']}" for r in sample)

    system_prompt = (
        "You are a requirements engineering assistant. "
        "Your task is to group user reviews into thematic clusters that represent "
        "distinct types of users or user situations for a mindfulness/meditation app."
    )

    user_prompt = (
        f"Below are {len(sample)} cleaned user reviews (id: text) for the Headspace app.\n\n"
        f"{numbered}\n\n"
        f"Group these reviews into exactly {NUM_GROUPS} thematic groups. "
        "Each group should represent a distinct type of user concern or situation. "
        "Each group must contain at least 10 review IDs.\n\n"
        "Respond ONLY with a valid JSON object in exactly this format, no preamble:\n"
        "{\n"
        '  "groups": [\n'
        "    {\n"
        '      "group_id": "A1",\n'
        '      "theme": "<short theme label>",\n'
        '      "review_ids": [<list of integer IDs>],\n'
        '      "example_reviews": ["<verbatim review text 1>", "<verbatim review text 2>"]\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    print("Calling Groq API for review grouping...")
    raw = call_groq(system_prompt, user_prompt)
    json_str = extract_json_block(raw)
    result = json.loads(json_str)

    # Save prompt used
    os.makedirs("prompts", exist_ok=True)
    with open(PROMPT_OUT, "w", encoding="utf-8") as f:
        json.dump(
            {
                "task": "review_grouping",
                "model": MODEL,
                "system_prompt": system_prompt,
                "user_prompt_template": user_prompt,
            },
            f,
            indent=2,
        )

    # Validate and patch: ensure group IDs are A1–A5 and have enough reviews
    seen_ids: set[int] = set()
    for i, group in enumerate(result["groups"]):
        group["group_id"] = f"A{i + 1}"
        # deduplicate review IDs
        deduped = []
        for rid in group["review_ids"]:
            if rid not in seen_ids:
                deduped.append(rid)
                seen_ids.add(rid)
        group["review_ids"] = deduped

    # Assign any leftover reviews round-robin so every group hits MIN_PER_GROUP
    all_assigned = {rid for g in result["groups"] for rid in g["review_ids"]}
    leftover = [r["id"] for r in sample if r["id"] not in all_assigned]
    gi = 0
    for rid in leftover:
        while len(result["groups"][gi]["review_ids"]) >= MIN_PER_GROUP:
            gi = (gi + 1) % NUM_GROUPS
            if gi == 0:
                break
        if len(result["groups"][gi]["review_ids"]) < MIN_PER_GROUP:
            result["groups"][gi]["review_ids"].append(rid)

    return result


# ── Step 4.2: Generate personas from groups ───────────────────────────────────
def generate_personas(groups: list[dict], reviews: list[dict]) -> dict:
    """Use LLM to create one structured persona per review group."""
    id_to_text = {r["id"]: r["review"] for r in reviews}

    personas = []
    for group in groups:
        sample_reviews = [
            id_to_text[rid] for rid in group["review_ids"][:10] if rid in id_to_text
        ]
        reviews_text = "\n".join(f"- {r}" for r in sample_reviews)

        system_prompt = (
            "You are a requirements engineering assistant specialising in user research. "
            "Create detailed, grounded personas based only on evidence from the provided reviews."
        )

        user_prompt = (
            f"The following reviews represent users in the theme: '{group['theme']}'\n\n"
            f"{reviews_text}\n\n"
            "Create ONE persona for this user group. "
            "Base every field strictly on evidence from the reviews above. "
            "Do not invent details.\n\n"
            "Respond ONLY with a valid JSON object in exactly this format:\n"
            "{\n"
            f'  "id": "{group["group_id"].replace("A", "P_auto_")}",\n'
            '  "name": "<descriptive persona name>",\n'
            '  "description": "<2-3 sentence description grounded in review evidence>",\n'
            f'  "derived_from_group": "{group["group_id"]}",\n'
            '  "goals": ["<goal 1>", "<goal 2>"],\n'
            '  "pain_points": ["<pain point 1>", "<pain point 2>"],\n'
            '  "context": ["<usage context 1>", "<usage context 2>"],\n'
            '  "constraints": ["<constraint 1>", "<constraint 2>"],\n'
            '  "evidence_reviews": [<list of review IDs used as evidence>]\n'
            "}"
        )

        print(f"  Generating persona for group {group['group_id']} ({group['theme']})...")
        raw = call_groq(system_prompt, user_prompt)
        json_str = extract_json_block(raw)
        persona = json.loads(json_str)

        # Ensure derived_from_group is set correctly
        persona["derived_from_group"] = group["group_id"]
        # Ensure evidence_reviews are integer IDs
        persona["evidence_reviews"] = group["review_ids"][:5]

        personas.append(persona)

    return {"personas": personas}


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY environment variable is not set. "
            "Export it before running this script."
        )

    print("Loading cleaned reviews...")
    reviews = load_reviews(CLEAN_FILE)
    print(f"Loaded {len(reviews)} reviews.")

    # 4.1 – Group reviews
    print(f"\nStep 4.1: Grouping reviews into {NUM_GROUPS} themes...")
    groups_data = group_reviews(reviews)
    os.makedirs("data", exist_ok=True)
    with open(GROUPS_OUT, "w", encoding="utf-8") as f:
        json.dump(groups_data, f, indent=2)
    print(f"Saved review groups to {GROUPS_OUT}")
    for g in groups_data["groups"]:
        print(f"  {g['group_id']}: {g['theme']} ({len(g['review_ids'])} reviews)")

    # 4.2 – Generate personas
    print("\nStep 4.2: Generating personas...")
    personas_data = generate_personas(groups_data["groups"], reviews)
    os.makedirs("personas", exist_ok=True)
    with open(PERSONAS_OUT, "w", encoding="utf-8") as f:
        json.dump(personas_data, f, indent=2)
    print(f"Saved {len(personas_data['personas'])} personas to {PERSONAS_OUT}")

    print("\nDone. Run 06_spec_generate.py next.")


if __name__ == "__main__":
    main()
