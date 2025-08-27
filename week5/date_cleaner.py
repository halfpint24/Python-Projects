import argparse
import json
import os
import re
import sys
from difflib import get_close_matches
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

# --- SIMPLE SETTINGS ---
PLACEHOLDERS = {'', 'na', 'n/a', 'n.a.', '-', '–', '—'}
NAIROBI = ZoneInfo('Africa/Nairobi')
TODAY_KE = datetime.now(NAIROBI).date()

# very basic date patterns we try to detect inside a cell
DATE_RE = re.compile(
    r'(\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'        # 2025-08-26 or 2025/8/26
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'       # 8/26/25 or 08-26-2025
    r'\b\d{1,2}\s+[A-Za-z]{3,}\s+\d{2,4}\b|'    # 26 Aug 2025
    r'\b[A-Za-z]{3,}\s+\d{1,2},\s*\d{2,4}\b)'   # Aug 26, 2025
)

def norm(s):
    s = (s or '').lower()
    return re.sub(r'[^a-z0-9]', '', s)

def map_columns(actual_cols, target_cols, strict):
    rename = {}
    missing = []
    by_norm = {norm(c): c for c in actual_cols}

    for t in target_cols:
        tn = norm(t)
        if tn in by_norm:
            rename[by_norm[tn]] = t
        else:
            if strict == 'True':
                missing.append(t)
            else:
                # fuzzy on normalized names
                picks = get_close_matches(tn, list(by_norm.keys()), n=1, cutoff=0.82)
                if picks:
                    rename[by_norm[picks[0]]] = t
                else:
                    missing.append(t)
    return rename, missing

def parse_cell_to_date(value):
    # returns (date or None, issue_type or None)
    if pd.isna(value):
        return None, 'placeholder'
    s = str(value).strip()
    if s.lower() in PLACEHOLDERS:
        return None, 'placeholder'

    m = DATE_RE.search(s)
    if not m:
        return None, 'no_date_found'

    token = m.group(1)
    # try parse with dayfirst False then True
    for dayfirst in (False, True):
        try:
            d = pd.to_datetime(token, errors='raise', dayfirst=dayfirst).date()
            return d, None
        except Exception:
            pass
    return None, 'invalid_date'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='in_path', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--issues', required=True)
    parser.add_argument('--date-cols', nargs='+', required=True)
    parser.add_argument('--min-year', type=int, default=None)
    parser.add_argument('--strict', choices=['True','False'], default='True')
    parser.add_argument('--dry-run', choices=['True','False'], default='False')
    args = parser.parse_args()

    # read input
    try:
        df = pd.read_excel(args.in_path)
    except Exception as e:
        sys.stderr.write(f'[read-error] {e}\n')
        sys.exit(10)

    # column mapping
    rename_map, missing = map_columns(df.columns, args.date_cols, args.strict)
    if missing and args.strict == 'True':
        sys.stderr.write(f'[missing-columns] {missing}\n')
        sys.exit(11)

    if rename_map:
        df = df.rename(columns=rename_map)

    cleaned = df.copy()
    issues_rows = []

    # go column by column
    for col in args.date_cols:
        if col not in cleaned.columns:
            # if non-strict and still missing, just skip
            continue
        for i, val in cleaned[col].items():
            d, err = parse_cell_to_date(val)

            if err is not None:
                # leave original text in cleaned for idempotency/safety
                issues_rows.append((i, col, val, err))
                continue

            # extra checks
            if args.min_year and d.year < args.min_year:
                issues_rows.append((i, col, val, 'year_lt_min'))
                continue

            if d > TODAY_KE:
                issues_rows.append((i, col, val, 'future_date'))
                continue

            # normalize valid dates
            cleaned.at[i, col] = d.strftime('%m/%d/%Y')

    issues_df = pd.DataFrame(
        issues_rows,
        columns=['row_index', 'column', 'original_value', 'issue_type']
    )

    # meta (always write)
    meta = {
        'run_at_nairobi': datetime.now(NAIROBI).isoformat(),
        'today_nairobi_date': str(TODAY_KE),
        'input': os.path.abspath(args.in_path),
        'out': os.path.abspath(args.out),
        'issues': os.path.abspath(args.issues),
        'targets': args.date_cols,
        'min_year': args.min_year,
        'strict': args.strict,
        'dry_run': args.dry_run,
        'rename_map': rename_map,
        'missing_targets': missing,
    }

    try:
        with open('run_meta.json', 'w', encoding='utf-8') as f:
            os.makedirs(os.path.dirname(args.out), exist_ok=True)
            os.makedirs(os.path.dirname(args.issues), exist_ok=True)

            json.dump(meta, f, indent=2)

        if args.dry_run == 'False':
            cleaned.to_excel(args.out, index=False)
            issues_df.to_excel(args.issues, index=False)
    except Exception as e:
        sys.stderr.write(f'[write-error] {e}\n')
        sys.exit(12)

    sys.exit(0)

if __name__ == '__main__':
    main()
