import csv
import json
import os
import random
import sys
from datetime import datetime
from getpass import getuser

QUOTES_FILE = "quotes.csv"
TIPS_FILE = "tips.csv"
FUN_FILE = "fun.csv"
LOG_FILE = "digest_log.csv"
CONFIG_FILE = "user_config.json"

QUOTES_FIELDS = ["quote", "author"]
TIPS_FIELDS = ["category", "tip"]
FUN_FIELDS = ["type", "content"]
LOG_FIELDS = ["timestamp","username","quote","author","tip","tip_category","fun_type","fun_content"]

MIN_ROWS = 15

def load_config_username():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("username"):
                    return data["username"]
        except Exception:
            pass
    try:
        name = input("Enter your name (press Enter to use system username): ").strip()
    except EOFError:
        name = ""
    if not name:
        name = getuser() or "User"
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": name}, f)
    except Exception:
        pass
    return name

def fail(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)

def validate_and_load(path, expected_fields):
    if not os.path.exists(path):
        fail(f"Missing data file: {path}")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            for h in expected_fields:
                if h not in headers:
                    fail(f"{path} has wrong headers. Expected: {expected_fields}. Found: {headers}")
            rows = [r for r in reader if any((v or "").strip() for v in r.values())]
            if len(rows) < MIN_ROWS:
                fail(f"{path} has fewer than {MIN_ROWS} rows (found {len(rows)}).")
            return rows
    except Exception as e:
        fail(f"Failed to load {path}: {e}")

def ensure_log():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        with open(LOG_FILE, "w", encoding="utf-8", newline="") as f:
            csv.DictWriter(f, fieldnames=LOG_FIELDS).writeheader()

def pick_random(rows):
    return random.choice(rows)

def print_digest(quote_row, tip_row, fun_row, username):
    line = "-" * 31
    print(line)
    print("Positive Daily Digest")
    print(line)
    quote_text = (quote_row.get("quote") or "").strip()
    author = (quote_row.get("author") or "").strip()
    if author:
        print(f'Quote: "{quote_text}" — {author}')
    else:
        print(f'Quote: "{quote_text}"')
    print(f'Workplace Tip: {(tip_row.get("tip") or "").strip()}')
    ftype = (fun_row.get("type") or "").strip().lower()
    label = "Fun Fact" if ftype == "fact" else "Joke"
    print(f'{label}: {(fun_row.get("content") or "").strip()}')
    print(f"Prepared by: {username}")
    print(line)

def write_log(username, quote_row, tip_row, fun_row):
    ts = datetime.now().isoformat(timespec="seconds")
    out = {
        "timestamp": ts,
        "username": username,
        "quote": (quote_row.get("quote") or "").strip(),
        "author": (quote_row.get("author") or "").strip(),
        "tip": (tip_row.get("tip") or "").strip(),
        "tip_category": (tip_row.get("category") or "").strip(),
        "fun_type": (fun_row.get("type") or "").strip().lower(),
        "fun_content": (fun_row.get("content") or "").strip(),
    }
    with open(LOG_FILE, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        w.writerow(out)

def load_log_rows():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def compute_streaks(rows):
    from datetime import datetime
    def parse_date(s):
        try:
            return datetime.fromisoformat(s).date()
        except Exception:
            return None
    days = sorted({parse_date(r["timestamp"]) for r in rows if r.get("timestamp")})
    days = [d for d in days if d is not None]
    if not days:
        return 0, 0
    longest = 1
    cur = 1
    for i in range(1, len(days)):
        if (days[i] - days[i-1]).days == 1:
            cur += 1
        else:
            if cur > longest:
                longest = cur
            cur = 1
    if cur > longest:
        longest = cur
    current = 1
    for i in range(len(days)-1, 0, -1):
        if (days[i] - days[i-1]).days == 1:
            current += 1
        else:
            break
    return current, longest

def history_summary():
    rows = load_log_rows()
    total = len(rows)
    current_streak, longest_streak = compute_streaks(rows)
    counts = {}
    for r in rows:
        c = (r.get("tip_category") or "").strip()
        if c:
            counts[c] = counts.get(c, 0) + 1
    if counts:
        maxc = max(counts.values())
        modes = sorted([k for k, v in counts.items() if v == maxc])
        cat_mode = ", ".join(modes) + f" (×{maxc})"
    else:
        cat_mode = "N/A"
    jokes = sum(1 for r in rows if (r.get("fun_type") or "").strip().lower() == "joke")
    facts = sum(1 for r in rows if (r.get("fun_type") or "").strip().lower() == "fact")
    print("\n=== History Summary ===")
    print(f"Total digests generated: {total}")
    print(f"Current streak: {current_streak}")
    print(f"Longest streak: {longest_streak}")
    print(f"Most frequent tip category (mode): {cat_mode}")
    print(f"Counts — Jokes: {jokes} | Facts: {facts}")
    print("=======================\n")

def generate_digest_once(username, quotes, tips, funs):
    q = pick_random(quotes)
    t = pick_random(tips)
    f = pick_random(funs)
    print_digest(q, t, f, username)
    write_log(username, q, t, f)

def main():
    quotes = validate_and_load(QUOTES_FILE, QUOTES_FIELDS)
    tips = validate_and_load(TIPS_FILE, TIPS_FIELDS)
    funs = validate_and_load(FUN_FILE, FUN_FIELDS)
    ensure_log()
    username = load_config_username()
    generate_digest_once(username, quotes, tips, funs)
    while True:
        print("\nMenu")
        print("1 — Generate another digest now")
        print("2 — View history summary")
        print("3 — Exit")
        try:
            choice = input("Select an option (1/2/3): ").strip()
        except EOFError:
            choice = "3"
        if choice == "1":
            generate_digest_once(username, quotes, tips, funs)
        elif choice == "2":
            history_summary()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid selection. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    random.seed()
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
