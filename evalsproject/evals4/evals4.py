import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use('Agg')

evals_data = pd.read_excel('Evals Datasheet 24.xlsx')

# GETTING MISSING DATA

missing_data = evals_data.copy()[['Client Name', 'VR Counselor/ Case Manager Name', 'VR Technician', 'Proficient in English?', 'Email', 'Contact Attempts']]


def get_missing_data(row):
    if pd.isna(row['VR Counselor/ Case Manager Name']):
        return 'Missing VR Counselor / Case Manager'
    if pd.isna(row['VR Technician']):
        return 'Missing VR technician'
    if pd.isna(row['Proficient in English?']):
        return 'Missing English proficiency'

    return 'Nothing missing'


missing_data['Missing Data'] = missing_data.apply(get_missing_data, axis=1)
print(missing_data['Missing Data'].value_counts())

# MISSING EMAIL / NO CONTACT ATTEMPS

missing_data = missing_data[missing_data['Missing Data'] == 'Nothing missing']


def get_missing_email_contacts_reported(row):
    if pd.isna(row['Email']):
        return 'No Email'
    if pd.isna(row['Contact Attempts']):
        return 'No Contact Attempts'

    return 'No Email/Contact Attempts missing'


missing_data['Missing Data'] = missing_data.apply(get_missing_email_contacts_reported, axis=1)
print(missing_data['Missing Data'].value_counts())
print(missing_data.loc[missing_data['Missing Data'] == 'No Contact Attempts', ['Client Name']])


# COMPLETED REPORTS

completed_reports = evals_data.copy()[evals_data['Report Status'] == 'Report Sent']
pending_reports = evals_data.copy()[evals_data['Report Status'] != 'Report Sent']

print(completed_reports['Report Status'].value_counts())
print(pending_reports['Report Status'].value_counts(dropna=False))

# COMPLETION RATES

vr_private_pay_reports = completed_reports[(completed_reports['Referral Source'] == 'Vocational Rehabilitation') | (completed_reports['Referral Source'] == 'Private Pay')]

print(vr_private_pay_reports['Referral Source'].value_counts())

plt.figure(figsize=(8, 6))
plt.pie(vr_private_pay_reports['Referral Source'].value_counts(), labels=['VR', 'Private Pay'])
plt.axis('equal')
plt.title('VR vs Private Pay completed reports')
plt.savefig('vr_private_pay_pie_chart.png')
