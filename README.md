# EECS4312_W26_SpecChain
Javeria Alam - 218714451

Application: [HeadSpace]

Dataset:
- reviews_raw.jsonl contains the collected reviews.
- reviews_clean.jsonl contains the cleaned dataset.
- The original dataset contained 2000 reviews. The cleaned dataset contains 1978 reviews.
- User reviews were collected through automated web scraping using the google_play_scraper Python library. 

Repository Structure:
- data/ contains datasets and review groups
- personas/ contains persona files
- spec/ contains specifications
- tests/ contains validation tests
- metrics/ contains all metric files
- src/ contains executable Python scripts
- reflection/ contains the final reflection

How to Run:
1. python src/00_validate_repo.py
2. $env:GROQ_API_KEY="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"
3. python src/run_all.py
4. Open metrics/metrics_summary.json for comparison results

NOTE:
- Should you run the code and recieve this error: 429 Client Error: "Too Many Requests for url: https://api.groq.com/openai/v1/chat/completions". Please run it again after a moment.