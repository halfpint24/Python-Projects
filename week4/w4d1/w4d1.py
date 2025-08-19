import pandas as pd

raw_data = pd.read_excel('Employment_OJT Anon.xlsx')

row_issues = {i: [] for i in raw_data.index}

for col in raw_data.columns:
    if 'date' in col.lower():
        if col.lower() == 'client name (end date only)':
            continue
        
        raw_data[col] = pd.to_datetime(raw_data[col], errors='coerce')

        mask_missing = raw_data[col].isna()
        for i in raw_data[mask_missing].index:
            row_issues[i].append(f'{col}: Missing/Invalid')

        mask_dups = raw_data[col].duplicated(keep=False)
        for i in raw_data[mask_dups].index:
            row_issues[i].append(f'{col}: Duplicate')

        raw_data[col] = raw_data[col].dt.strftime('%m/%d/%Y')


def normalize_yes_no(val):
    if pd.isna(val): 
        return None
    v = str(val).strip().lower()
    if v in ['yes', 'y', 'true']:
        return 'Yes'
    if v in ['no', 'n', 'false']:
        return 'No'
    return val


for col in ['Resume Completed', 'Case Notes Submitted']:
    if col in raw_data.columns:
        raw_data[col] = raw_data[col].map(normalize_yes_no)

if 'CLIENT STATUS' in raw_data.columns:
    raw_data['CLIENT STATUS'] = raw_data['CLIENT STATUS'].str.strip().str.title()

raw_data['Issues'] = raw_data.index.map(lambda i: '; '.join(row_issues[i]) if row_issues[i] else '')

raw_data.to_excel('Week_4_Cleaned.xlsx', index=False)
