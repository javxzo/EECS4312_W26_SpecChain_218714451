import json
import re
import nltk
import spacy

from nltk.corpus import stopwords

# download stopwords if not already installed
nltk.download("stopwords")

# load spaCy model
nlp = spacy.load("en_core_web_sm")

stop_words = set(stopwords.words("english"))

input_file = "data/reviews_raw.jsonl"
output_file = "data/reviews_clean.jsonl"

seen_reviews = set()

def clean_text(text):

    # lowercase
    text = text.lower()

    # remove punctuation and special characters
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # remove stopwords + lemmatize
    doc = nlp(text)

    cleaned_words = []

    for token in doc:
        lemma = token.lemma_

        if lemma not in stop_words and lemma.strip() != "":
            cleaned_words.append(lemma)

    return " ".join(cleaned_words)


cleaned_reviews = []

with open(input_file, "r", encoding="utf-8") as f:

    for line in f:

        review = json.loads(line)

        text = review["review"]

        if not text or len(text.strip()) < 3:
            continue

        cleaned = clean_text(text)

        if cleaned in seen_reviews:
            continue

        seen_reviews.add(cleaned)

        cleaned_reviews.append({
            "id": review["id"],
            "review": cleaned
        })


with open(output_file, "w", encoding="utf-8") as f:

    for r in cleaned_reviews:
        f.write(json.dumps(r) + "\n")

print("Cleaning complete")
print("Total cleaned reviews:", len(cleaned_reviews))