# Positive Daily Digest

A small Python script that prints a **Daily Digest** with:
- A motivational quote
- A workplace productivity tip
- A fun element (joke or fact)

## Files

- `daily_digest.py`
- `quotes.csv`
- `tips.csv`
- `fun.csv`
- `digest_log.csv` (auto-created)
- `user_config.json` (auto-created)

## Run

```bash
python3 daily_digest.py
```

The script validates the CSVs (must exist, correct headers, ≥15 rows). If any validation fails, it exits with error.

It logs each digest and can show a history summary (total digests, streaks, most frequent tip category, joke/fact counts).
