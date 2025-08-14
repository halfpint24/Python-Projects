import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import ast

cleaned_data = pd.read_excel('cleaned_data.xlsx')

cpt_codes = ast.literal_eval(cleaned_data['CPT'].iloc[0])

print('Occurrences of CPT codes from most to least common: {}'.format(dict(sorted(cpt_codes.items(), key=lambda item: item[1], reverse=True))))

# PARETO CHART

cpt_counts_df = pd.DataFrame(sorted(cpt_codes.items(), key=lambda x: x[1], reverse=True),
                  columns=['CPT Code', 'Count'])

cpt_counts_df['Cumulative %'] = cpt_counts_df['Count'].cumsum() / cpt_counts_df['Count'].sum() * 100

fig, ax1 = plt.subplots()

ax1.bar(cpt_counts_df['CPT Code'], cpt_counts_df['Count'], color='skyblue')
ax1.set_xlabel('CPT Code')
ax1.set_ylabel('Frequency', color='blue')

ax2 = ax1.twinx()
ax2.plot(cpt_counts_df['CPT Code'], cpt_counts_df['Cumulative %'], color='red', marker='o')
ax2.set_ylabel('Cumulative %', color='red')
ax2.set_ylim(0, 110)
ax2.axhline(80, color='gray', linestyle='--')

plt.title('Pareto Chart of CPT Codes')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('cptpareto.png')

# INSURER

cleaned_data['CPT'] = cleaned_data['CPT'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
cpt_insurer = {}
cpt_counts = {}

for _, row in cleaned_data.iterrows():
    insurer = row['Insurer'] if 'Insurer' in row and pd.notna(row['Insurer']) else 'Unknown'
    for code, num in row['CPT'].items():
        cpt_counts[code] = cpt_counts.get(code, 0) + num
        if code not in cpt_insurer:
            cpt_insurer[code] = {}
        cpt_insurer[code][insurer] = cpt_insurer[code].get(insurer, 0) + num

print()
print('CPT codes heavily tied to one insurer:')
for code, insurers in cpt_insurer.items():
    total = sum(insurers.values())
    top_insurer, top_count = max(insurers.items(), key=lambda x: x[1])
    share = top_count / total * 100
    if share >= 60:
        print(f'{code}: {top_insurer} ({share:.1f}%)')

# RARE CODES

RARE_THRESHOLD = 5
rare_codes = [c for c, count in cpt_counts.items() if count <= RARE_THRESHOLD]
print()
print(f'Rarely used codes (less than {RARE_THRESHOLD} occurrences):', rare_codes)

print()
print('Possible coding inconsistencies:')
for code, insurers in cpt_insurer.items():
    if len(insurers) > 1:
        total = sum(insurers.values())
        top_share = max(insurers.values()) / total * 100
        if top_share < 50:
            print(f'{code}: spread across insurers {insurers}')
    else:
        print('No inconsistencies')
