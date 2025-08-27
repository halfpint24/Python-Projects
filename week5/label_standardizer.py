import argparse
import json
import os
import re
import sys
import string
from collections import OrderedDict, Counter, defaultdict

import pandas as pd

try:
    import yaml
except Exception as _e:
    yaml = None  # we'll handle at parse time

# helpers

MISSING = {None, '', float('nan')}

def is_missing(val):
    if pd.isna(val):
        return True
    if isinstance(val, str) and val.strip() == '':
        return True
    return False


def norm(s, normalize):
    '''
    Normalize a value according to simple rules and a mode.
    - collapse internal whitespace
    - strip stray punctuation at edges
    - strip leading/trailing spaces
    - apply case mode
    '''
    if is_missing(s):
        return ''
    if not isinstance(s, str):
        s = str(s)

    # collapse multiple spaces into one
    s = re.sub(r'\s+', ' ', s)

    # remove stray punctuation (punctuation not surrounded by word characters)
    s = re.sub(rf'(?<!\w)[{re.escape(string.punctuation)}]+(?!\w)', '', s)

    # strip leading and trailing whitespace
    s = s.strip()

    # apply normalize option
    if normalize == 'lower':
        s = s.lower()
    elif normalize == 'upper':
        s = s.upper()
    elif normalize == 'title':
        s = string.capwords(s)
    elif normalize == 'none':
        pass

    return s


def build_reverse_map(yaml_obj, normalize):
    '''
    Expect YAML like:
    Report Status:
      Open: [Open, In Progress, 'WIP']
      Closed: [Closed, Done]
    Returns:
      canonicals_per_col: dict[col] = set of canonical labels
      reverse_maps: dict[col] = dict[normalized_synonym] -> canonical
    Deterministic: respects YAML order (first match wins).
    '''
    canonicals_per_col = {}
    reverse_maps = {}

    for col, mapping in yaml_obj.items():
        canon_set = []
        rmap = OrderedDict()

        # mapping can be dict canonical -> list synonyms (including itself)
        if not isinstance(mapping, dict):
            raise ValueError(f'Mapping for column \'{col}\' must be a dict of canonical -> [synonyms].')

        for canonical, synonyms in mapping.items():
            canon_norm = norm(canonical, normalize)
            if canon_norm == '':
                continue
            canon_set.append(canonical)

            # allow single synonym or list
            if isinstance(synonyms, (list, tuple, set)):
                syn_list = list(synonyms)
            elif synonyms is None:
                syn_list = []
            else:
                syn_list = [synonyms]

            # ensure canonical itself also maps to canonical
            syn_list = [*syn_list, canonical]

            for syn in syn_list:
                syn_norm = norm(syn, normalize)
                if syn_norm == '':
                    continue
                # first match wins; don't overwrite existing
                if syn_norm not in rmap:
                    rmap[syn_norm] = canonical

        canonicals_per_col[col] = sorted(set(canon_set))
        reverse_maps[col] = rmap

    return canonicals_per_col, reverse_maps


def standardize_dataframe(df, cols, reverse_maps, normalize):
    '''
    Applies mapping to selected columns.
    Returns:
      df_out, audit_rows (list of dicts), unmapped_counter (dict[col] -> Counter)
    '''
    df_out = df.copy()
    audit_rows = []
    unmapped_counter = defaultdict(Counter)

    for col in cols:
        if col not in df_out.columns:
            # handled earlier; skip to be safe
            continue

        # work on a series
        original_series = df_out[col]
        new_values = []

        for idx, val in original_series.items():
            if is_missing(val):
                new_values.append(val)
                continue

            val_norm = norm(val, normalize)
            mapped = reverse_maps.get(col, {}).get(val_norm)

            if mapped is None:
                # not mapped -> keep original, count as unmapped
                new_values.append(val)
                unmapped_counter[col][str(val)] += 1
            else:
                # apply canonical only if it differs
                if str(val) != mapped:
                    audit_rows.append({
                        'row_index': idx,
                        'column': col,
                        'before': val,
                        'after': mapped
                    })
                new_values.append(mapped)

        df_out[col] = new_values

    return df_out, audit_rows, unmapped_counter


def write_csv_safely(df_or_rows, path, columns=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(df_or_rows, list):
        df = pd.DataFrame(df_or_rows, columns=columns)
    else:
        df = df_or_rows
    df.to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser(description='Canonicalize label columns using a YAML mapping and produce an audit.')
    parser.add_argument('--in', dest='in_path', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--audit', required=True)
    parser.add_argument('--unmapped', required=True)
    parser.add_argument('--map', dest='map_path', required=True)
    parser.add_argument('--cols', nargs='+', required=True)
    parser.add_argument('--normalize', choices=['lower', 'upper', 'title', 'none'], default='none')
    parser.add_argument('--dry-run', choices=['True', 'False'], default='False')
    args = parser.parse_args()

    # read input
    try:
        df = pd.read_excel(args.in_path)
    except Exception as e:
        sys.stderr.write(f'[read-error] {e}\n')
        sys.exit(10)

    # verify columns
    missing_cols = [c for c in args.cols if c not in df.columns]
    if missing_cols:
        sys.stderr.write(f'[missing-cols] Missing columns: {missing_cols}\n')
        sys.exit(11)

    # read YAML map
    try:
        if yaml is None:
            raise RuntimeError('PyYAML not available')
        with open(args.map_path, 'r', encoding='utf-8') as f:
            yaml_obj = yaml.safe_load(f) or {}
        if not isinstance(yaml_obj, dict):
            raise ValueError('Top-level YAML must be a mapping of column -> {canonical: [synonyms...]}')
    except Exception as e:
        sys.stderr.write(f'[yaml-error] {e}\n')
        sys.exit(12)

    # build reverse maps (deterministic)
    try:
        canonicals_per_col, reverse_maps = build_reverse_map(yaml_obj, args.normalize)
    except Exception as e:
        sys.stderr.write(f'[yaml-parse-error] {e}\n')
        sys.exit(12)

    # apply mapping
    df_out, audit_rows, unmapped_counter = standardize_dataframe(df, args.cols, reverse_maps, args.normalize)

    # meta (always write)
    meta = {
        'input': args.in_path,
        'output': args.out,
        'audit': args.audit,
        'unmapped': args.unmapped,
        'mapping': args.map_path,
        'normalize': args.normalize,
        'columns': args.cols,
        'canonical_sets': canonicals_per_col,
        'unmapped_remaining': {col: (sum(unmapped_counter[col].values()) > 0) for col in args.cols},
        'audit_changes': len(audit_rows)
    }

    # write outputs
    try:
        # ensure parent dirs
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        os.makedirs(os.path.dirname(args.audit), exist_ok=True)
        os.makedirs(os.path.dirname(args.unmapped), exist_ok=True)

        # write meta
        with open('run_meta.json', 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)

        if args.dry_run == 'False':
            # write standardized excel
            df_out.to_excel(args.out, index=False)

            # write audit only for changes
            if audit_rows:
                write_csv_safely(audit_rows, args.audit, columns=['row_index', 'column', 'before', 'after'])
            else:
                # write empty audit with headers
                write_csv_safely([], args.audit, columns=['row_index', 'column', 'before', 'after'])

            # write unmapped if any, with counts
            if any(unmapped_counter[col] for col in args.cols):
                rows = []
                for col, counter in unmapped_counter.items():
                    for val, cnt in counter.items():
                        rows.append({'column': col, 'value': val, 'count': cnt})
                write_csv_safely(rows, args.unmapped, columns=['column', 'value', 'count'])
            else:
                # do not create file if no unmapped (edge-case requirement)
                pass

    except Exception as e:
        sys.stderr.write(f'[write-error] {e}\n')
        sys.exit(13)

    sys.exit(0)


if __name__ == '__main__':
    main()
