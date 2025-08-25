import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import re

matplotlib.use('Agg')

cleaned_data = pd.read_excel('Week_4_Cleaned.xlsx')


def split_name_city(text):
    m = re.match(r'^(.*?)\((.*?)\)', str(text))
    if m:
        return pd.Series([m.group(1).strip(), m.group(2).strip()])
    return pd.Series([str(text).strip(), ''])


def clean_city(city):
    if not city:
        return ''

    city = str(city).strip().upper()
    
    if 'FL' in city:
        pos = city.find('FL')
        fixed_city = city[:pos-1]
        if fixed_city[-1] == ',':
            return fixed_city[:len(fixed_city)-1]
        else:
            return fixed_city

    return city


cleaned_data[['Client Name', 'City']] = cleaned_data['CLIENT NAME (END DATE ONLY)'].dropna().apply(split_name_city)
cleaned_data['City'] = cleaned_data['City'].apply(clean_city)
print(cleaned_data[['Client Name', 'City']])

resume_by_city = (
    cleaned_data.groupby('City')['Resume Completed']
      .apply(lambda x: (x == 'Yes').mean() * 100)
      .reset_index(name='Resume Completion Rate (%)')
      .sort_values('Resume Completion Rate (%)', ascending=False)
)
print(resume_by_city)

plt.figure(figsize=(10,6))
plt.barh(resume_by_city['City'], resume_by_city['Resume Completion Rate (%)'])
plt.xticks(rotation=45, ha='right')
plt.ylabel('Resume Completion Rate (%)')
plt.title('Resume Completion Rates by City')
plt.tight_layout()
plt.savefig('resume_completion_rates_chart.png')


def clean_staff(val: str) -> str:
    if pd.isna(val):
        return ''
    s = str(val).strip().upper()

    if s in {'YES', 'NO', 'CSI', 'ON PAUSE'}:
        return ''

    s = re.sub(r'\(.*?\)', '', s)
    s = re.split(r'[,-/]', s)[0].strip()
    s = re.sub(r'[^A-Z ]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()

    return s.title()

cleaned_data['Staff'] = cleaned_data['CSI'].apply(clean_staff)

staff_map = {
    'Joycelyn Dbs': 'Joycelyn',
    'Ari Lakeland': 'Ari',
    'Damieka': 'Damieka',
    'Raymond': 'Raymond',
}

cleaned_data['Staff'] = cleaned_data['Staff'].replace(staff_map)

staff_counts = (
    cleaned_data.loc[cleaned_data['Staff'].ne(''), 'Staff']
      .value_counts()
      .rename_axis('Staff')
      .reset_index(name='Client Count')
      .sort_values('Client Count', ascending=False)
      .reset_index(drop=True)
)

print(staff_counts)

staff_counts = staff_counts.sort_values(by='Client Count', ascending=False).reset_index(drop=True)

staff_counts['Client Count'] = pd.to_numeric(staff_counts['Client Count'], errors='coerce').fillna(0)


total = staff_counts['Client Count'].sum()
staff_counts['Cumulative %'] = (
    staff_counts['Client Count'].cumsum().div(total).mul(100).round(2) if total else 0
)

fig, ax1 = plt.subplots(figsize=(10,6))

ax1.bar(staff_counts['Staff'], staff_counts['Client Count'], color='skyblue')
ax1.set_ylabel('Client Count')
ax1.set_xticklabels(staff_counts['Staff'], rotation=45, ha='right')

ax2 = ax1.twinx()
ax2.plot(staff_counts['Staff'], staff_counts['Cumulative %'], color='red', marker='o', linestyle='-')
ax2.set_ylabel('Cumulative %')

ax2.axhline(80, color='green', linestyle='--', linewidth=1)

plt.title('Pareto Chart of Clients per Staff')
plt.tight_layout()
plt.savefig('clients_staff_pareto_chart.png')
