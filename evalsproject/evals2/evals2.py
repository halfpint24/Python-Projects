import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use('Agg')

evals_data = pd.read_excel('Evals Datasheet 24.xlsx')

# SEARCHING FOR LONGEST REPORT

longest_without_report = evals_data[evals_data['Referral Date'] != 'Report Sent']
print(longest_without_report[['Client Name', 'Referral Date']].head(5))

# TEST TYPE CATEGORIES

def categorize_test_type(test_type):
    test_type = str(test_type).strip().upper()
    
    if 'ADHD' in test_type or 'ADD' in test_type or 'CAARS' in test_type:
        return 'ADHD-related'
    if 'AUTISM' in test_type or 'SRS' in test_type or 'ASRS' in test_type:
        return 'Autism'
    if 'LEARNING DISABILITY' in test_type:
        return 'Learning Disability'
    if 'INTELLECTUAL' in test_type:
        return 'Intellectual Disability'
    if 'PERSONALITY' in test_type or 'PAI' in test_type:
        return 'Personality assessment'
    if 'ADAPTIVE' in test_type:
        return 'Adaptive behavior'
    if 'BDI' in test_type:
        return 'Depression'
    if 'BAI' in test_type:
        return 'Anxiety'
    if 'VOCATIONAL' in test_type:
        return 'Vocational'
    if test_type == '' or test_type == 'NAN':
        return 'Unknown assessment'

    return 'Needs clarification: {}'.format(test_type)

categorized_test_type = evals_data['Test Type'].apply(categorize_test_type)

print(evals_data['Client Name'].head(20) + ' - ' + categorized_test_type.head(20))

# REFERRAL COMPARISON

referral_distribution = pd.crosstab(evals_data['Referral Source'], evals_data['Report Status'])
print(referral_distribution)

referral_distribution.plot(kind='bar')

plt.title('Referral Source distribution across Report Statuses')
plt.xlabel('Referral Source')
plt.ylabel('Count')
plt.legend(title='Report Status')
plt.tight_layout()
plt.savefig('referral_source.png')

# MISSING TEST TYPE

clients_missing_test_type = evals_data[evals_data['Test Type'].isna()].dropna(subset=['Client Name', 'Email'])

print(clients_missing_test_type[['Client Name', 'Email', 'Test Type']])
