import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

cleaned_data = pd.read_excel('cleaned_data.xlsx')

primary_language = cleaned_data['Primary Language']

# PRINTING ALL NON ENGLISH ENTRIES
english = cleaned_data[primary_language == 'English']
not_english = cleaned_data[primary_language != 'English']

print(not_english[['First', 'Last Name', 'Primary Language']])

# VISUALIZATIONS

insurance_counts = cleaned_data.groupby(['Primary Language', 'Insurance Name']).size().unstack(fill_value=0)
copay_counts = cleaned_data.groupby(['Primary Language', 'Co-Pay Paid']).size().unstack(fill_value=0)
service_type_counts = cleaned_data.groupby(['Primary Language', 'Type Of Services']).size().unstack(fill_value=0)

insurance_counts.T.plot(kind='bar', figsize=(8, 5))
plt.xlabel('Insurance Name')
plt.ylabel('Number of People')
plt.title('Insurance Distribution: English vs Non-English Speakers')
plt.xticks(rotation=90)
plt.legend(title='Language Group')
plt.tight_layout()
plt.savefig('insurance_distribution.png')

copay_counts.T.plot(kind='bar', figsize=(8, 5))
plt.xlabel('Co-Pay Paid')
plt.ylabel('Number of People')
plt.title('Co-Pay Paid Distribution: English vs Non-English Speakers')
plt.xticks(rotation=90)
plt.legend(title='Language Group')
plt.tight_layout()
plt.savefig('copay_distribution.png')

plt.pie(cleaned_data['Type Of Services'].value_counts(), labels=cleaned_data['Type Of Services'].value_counts().index, autopct='%1.1f%%')
plt.title('Service Type Pie Chart')
plt.tight_layout()
plt.savefig('service_distribution.png')
