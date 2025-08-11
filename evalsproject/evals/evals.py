import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

matplotlib.use('Agg')

evals_data = pd.read_excel('Evals Datasheet 24.xlsx')

date_cols = ['Referral Date', 'Eval Date', 'Feedback Session Date']

# FORMATTING DATES

def convert_date_and_flag(date_str):
    date_str = str(date_str).strip().upper()
    parsed_date = pd.to_datetime(date_str, errors="coerce")
    
    if date_str.startswith('N/A') or pd.isna(parsed_date) or parsed_date.year < 1900:
        return 'FLAGGED: {}'.format(date_str)

    return parsed_date.strftime('%m/%d/%Y')

for col in date_cols:
    evals_data[col] = evals_data[col].apply(convert_date_and_flag)

print(evals_data['Feedback Session Date'].head())

# FIXING ERRORS

def validate_location(location):
    location = str(location).strip()

    if 'Orland ' in location:
        location = location.replace('Orland ', 'Orlando ')

    cities = ['Orlando', 'Lakeland', 'Kissimmee', 'Lake Mary', 'West Palm Beach', 'Haines City']
    for city in cities:
        if city in location:
            location = city

    return location

def validate_contractor_paid_status(contractor_paid_status):
    if pd.isna(contractor_paid_status):
        return "Unknown"
    
    contractor_paid_status = str(contractor_paid_status).strip()
    
    return contractor_paid_status

def validate_report_status(report_status):
    if pd.isna(report_status):
        return "Unknown"
    
    report_status = str(report_status).strip()
    
    return report_status

evals_data['Location'] = evals_data['Location'].apply(validate_location)
evals_data['Contractor Paid Status'] = evals_data['Contractor Paid Status'].apply(validate_contractor_paid_status)
evals_data['Report Status'] = evals_data['Report Status'].apply(validate_report_status)

# UNIQUE VALUES

report_status_counts = evals_data['Report Status'].value_counts()
contractor_paid_status_counts = evals_data['Contractor Paid Status'].value_counts()
referral_source_counts = evals_data['Referral Source'].value_counts()

print(report_status_counts)
print(contractor_paid_status_counts)
print(referral_source_counts)

plt.figure(figsize=(8,6))
plt.pie(report_status_counts.values, labels=report_status_counts.index)
plt.title('Report Status Counts by Value')
plt.savefig('report_status.png')

plt.figure(figsize=(8,6))
plt.pie(contractor_paid_status_counts.values, labels=contractor_paid_status_counts.index)
plt.title('Contractor Paid Counts by Value')
plt.savefig('contractor_paid_status.png')

plt.figure(figsize=(8,6))
plt.pie(referral_source_counts.values, labels=referral_source_counts.index)
plt.title('Referral Source Counts by Value')
plt.savefig('referral_source.png')

# MISSING/DUPLICATE FIELDS

print(evals_data['CASE ID #'].value_counts())
print(evals_data['Client Name'].value_counts())
print(evals_data['Email'].value_counts())

print(evals_data['CASE ID #'].isna().sum())
print(evals_data['Client Name'].isna().sum())
print(evals_data['Email'].isna().sum())

missing_case_id_rows = evals_data[evals_data['CASE ID #'].isna()]
print(missing_case_id_rows)
