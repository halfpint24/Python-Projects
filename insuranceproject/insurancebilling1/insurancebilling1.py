import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import date, datetime, time

insurance_data = pd.read_excel('Insurance Billing.xlsx')

# DATA CLEANING

cleaned_data = insurance_data.copy()
yes_no_columns = ['Insurance Verified', 'Verification Email Sent', 'ICD and CPT Code Added', 'Co-Pay Paid']
date_columns = ['Date of Service', '96132 Integrating Patient Data, Interpreting , Clinical Decisions, Writing Report\n', '96136 neuropsychological test administration and scoring', 'Feedback Session Date']

# Standardizing yes/no columns

def standardize_yes_no_response(value):
    if value == 'YES' or isinstance(value, (date, datetime, time)) or value == 'Private Pay' or value == 'Neuro-Psychological':
        return 'YES'

    return 'NO'

cleaned_data[yes_no_columns] = insurance_data[yes_no_columns].map(standardize_yes_no_response)

# Converting dates to MM-DD-YYYY format

for col in date_columns:
    cleaned_data[col] = cleaned_data[col].astype(str).str.split("&").str[0].str.strip()
    cleaned_data[col] = pd.to_datetime(cleaned_data[col], errors='coerce')
    cleaned_data[col] = cleaned_data[col].dt.strftime('%m-%d-%Y')

# Fixing insurance names
    
def fix_insurance_names(insurance_name):
    if pd.isna(insurance_name):
        return 'No insurance provided'

    iname = insurance_name.upper().strip()

    if 'UNITED' in iname:
        return 'United Health'
    if 'CIGNA' in iname:
        return 'Cigna'
    if 'AETNA' in iname:
        return 'Aetna'
    if 'OSCAR' in iname:
        return 'Oscar'
    if 'CHAMPVA' in iname:
        return 'Champva'

    return insurance_name

cleaned_data['Insurance Name'] = cleaned_data['Insurance Name'].apply(fix_insurance_names)

# Handling multi code CPT entries

def parse_cpt_codes(value):
    if pd.isna(value):
        return {}
    
    matches = re.findall(r'(\d+)\s*\((\d+)\)', str(value))
    return {code: int(units) for code, units in matches}

cleaned_data['CPT'] = cleaned_data['CPT'].apply(parse_cpt_codes)

# Replacing missing values

cleaned_data['Type Of Services'].fillna('Unknown Service', inplace=True)
cleaned_data.fillna('N/A')

cleaned_data.to_excel('cleaned_data.xlsx', index=False)

# DASHBOARD

st.header('Verified vs unverified insurance')
st.write('Around 1 in 5 of insurance carriers are unverified.')
insurance_verified = cleaned_data['Insurance Verified'].value_counts()
st.write(insurance_verified)
fig, ax = plt.subplots()
ax.pie(insurance_verified, labels=insurance_verified.index, autopct='%1.1f%%')
ax.axis='equal'
st.pyplot(fig)

st.header('Co-Pay Paid Rates by Insurance Provider')
st.write('Across most insurance providers, the majority of co-pays were paid. Cigna and United Health had the highest number of overall co-pays and the highest number of unpaid co-pays; however, even for these two providers, most co-pays were still paid. Notably, when no insurance provider was listed, the majority of co-pays were unpaid.')
counts = cleaned_data.groupby(['Insurance Name', 'Co-Pay Paid']).size().unstack(fill_value=0)
fig, ax = plt.subplots()
counts.plot(kind='bar', stacked=True, ax=ax)
ax.set_ylabel('Count')
ax.set_xlabel('Insurance Provider')
ax.legend(title='Co-Pay Paid')
st.pyplot(fig)

heatmap_data = cleaned_data.pivot_table(
    index='Insurance Verified',
    columns='Co-Pay Paid',
    aggfunc='size',
    fill_value=0
)
st.header('Verification - co-pay status heatmap')
st.write('More than 80% of verified insurance are also co-pay paid, with no occurrences of unverified insurance. Only a few of the co-pays were not paid with both verified and unverified insurance.')
fig, ax = plt.subplots()
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

st.header('Recommendations')
st.write('- Use automated reminders such as through email or text message to improve verification')
st.write('- Offer mobile payment option for co-pays')
st.write('- Clearly explain verification and co-pay information at time of service')
