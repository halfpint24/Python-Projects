import argparse
import json
import os
import sys
import pandas as pd


def normalize_cell(v):
    if isinstance(v, str):
        return v.strip().casefold()
    return v


def build_key(row, cols, normalized=False):
    vals = []
    for c in cols:
        val = row.get(c)
        if normalized:
            val = normalize_cell(val)
        vals.append(val)
    return tuple(vals)


def find_missing_required(df, required_cols):
    results = []
    for col in required_cols:
        if col not in df.columns:
            for idx in range(len(df)):
                results.append({'column': col, 'row_index': int(idx)})
            continue
        for idx, val in df[col].items():
            if pd.isna(val) or (isinstance(val, str) and val.strip() == ''):
                results.append({'column': col, 'row_index': int(idx)})
    return results


def find_duplicates(df, unique_cols, normalized=False):
    groups = {}
    for idx, row in df.iterrows():
        k = build_key(row, unique_cols, normalized)
        groups.setdefault(k, []).append(int(idx))

    dup_rows = []
    dup_meta = []
    gid = 1
    for k, idxs in groups.items():
        if len(idxs) > 1:
            key_val = str(k)
            dup_meta.append({
                'group_id': gid,
                'key_type': 'normalized' if normalized else 'exact',
                'size': len(idxs),
                'key_value': key_val
            })
            for i in idxs:
                dup_rows.append({
                    'group_id': gid,
                    'key_type': 'normalized' if normalized else 'exact',
                    'key_value': key_val,
                    'row_index': int(i)
                })
            gid += 1
    return dup_rows, dup_meta


def make_summary(missing_rows, dup_meta_exact, dup_meta_norm, required_cols, normalize_keys):
    missing_counts = {c: 0 for c in required_cols}
    for r in missing_rows:
        missing_counts[r['column']] += 1

    df_missing = pd.DataFrame(
        [{'column': c, 'missing_count': count} for c, count in missing_counts.items()]
    )

    dup_summary = []
    dup_summary.append({'key_type': 'exact', 'duplicate_groups': len(dup_meta_exact)})
    if normalize_keys:
        dup_summary.append({'key_type': 'normalized', 'duplicate_groups': len(dup_meta_norm)})
    df_dups = pd.DataFrame(dup_summary)

    df_counts = pd.DataFrame([
        {'metric': 'total_missing_required', 'count': sum(missing_counts.values())},
        {'metric': 'total_duplicate_groups',
         'count': len(dup_meta_exact) + (len(dup_meta_norm) if normalize_keys else 0)}
    ])

    return df_missing, df_dups, df_counts


def main():
    parser = argparse.ArgumentParser(description='Data integrity checker')
    parser.add_argument('--in', dest='in_path', required=True)
    parser.add_argument('--out', dest='out_path', required=True)
    parser.add_argument('--unique-cols', nargs='+', required=True)
    parser.add_argument('--required-cols', nargs='+', required=True)
    parser.add_argument('--normalize-keys', type=lambda x: x.lower() == 'true', default=False)
    parser.add_argument('--dry-run', type=lambda x: x.lower() == 'true', default=False)
    args = parser.parse_args()

    try:
        df = pd.read_excel(args.in_path)
    except Exception as e:
        sys.stderr.write(f'[read-error] {e}\n')
        sys.exit(10)

    # 1. Missing required
    missing_rows = find_missing_required(df, args.required_cols)

    # 2. Duplicates
    dup_exact, meta_exact = find_duplicates(df, args.unique_cols, normalized=False)
    dup_norm, meta_norm = ([], [])
    if args.normalize_keys:
        dup_norm, meta_norm = find_duplicates(df, args.unique_cols, normalized=True)

    # 3. Summary
    df_missing, df_dups, df_counts = make_summary(
        missing_rows, meta_exact, meta_norm, args.required_cols, args.normalize_keys
    )

    # 4. Dry run prints only
    if args.dry_run:
        print('Missing required:', len(missing_rows))
        print('Duplicate groups (exact):', len(meta_exact))
        if args.normalize_keys:
            print('Duplicate groups (normalized):', len(meta_norm))
        sys.exit(0)

    # 5. Write Excel
    try:
        with pd.ExcelWriter(args.out_path, engine='openpyxl') as writer:
            pd.DataFrame(missing_rows).to_excel(writer, index=False, sheet_name='missing_required')
            pd.DataFrame(dup_exact + dup_norm).to_excel(writer, index=False, sheet_name='duplicates')
            df_counts.to_excel(writer, index=False, sheet_name='Summary', startrow=0)
            df_missing.to_excel(writer, index=False, sheet_name='Summary', startrow=len(df_counts) + 3)
            df_dups.to_excel(writer, index=False, sheet_name='Summary',
                             startrow=len(df_counts) + len(df_missing) + 6)
    except Exception as e:
        sys.stderr.write(f'[write-excel-error] {e}\n')
        sys.exit(11)

    # 6. Write JSON meta
    meta_file = os.path.splitext(args.out_path)[0] + '_meta.json'
    meta = {
        'counts': {
            'total_rows': int(len(df)),
            'missing_required_rows': int(len(missing_rows)),
            'duplicate_groups_exact': int(len(meta_exact)),
            'duplicate_groups_normalized': int(len(meta_norm)),
        },
        'duplicate_groups': meta_exact + meta_norm
    }
    try:
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    except Exception as e:
        sys.stderr.write(f'[write-meta-error] {e}\n')
        sys.exit(12)


if __name__ == '__main__':
    main()
