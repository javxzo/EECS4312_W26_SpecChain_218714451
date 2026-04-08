"""imports or reads your raw dataset; if you scraped, include scraper here"""

from google_play_scraper import reviews
import json

APP_ID = "com.getsomeheadspace.android"

print("Collecting reviews from Google Play...")

result, _ = reviews(
    APP_ID,
    lang="en",
    count=2000
)

with open("data/reviews_raw.jsonl", "w", encoding="utf-8") as f:
    for i, r in enumerate(result):
        review_data = {
            "id": i,
            "review": r["content"]
        }
        f.write(json.dumps(review_data) + "\n")

print("Reviews saved to data/reviews_raw.jsonl")
print(f"Total reviews collected: {len(result)}")