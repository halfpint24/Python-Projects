import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, date

matplotlib.use('Agg')

clientstats = pd.read_csv('clientstats.csv')

def print_divider(str):
    print('')
    print('---------------------------------')
    print(str)
    print('---------------------------------')
    print('')

# IPE GOALS

print_divider('IPE Goals')

# clean data and remove values
clientstats['IPE'] = clientstats['IPE'].astype(str).str.strip().str.upper()
clientstats['IPE'] = clientstats['IPE'].replace({
    'UNIDENIFIED': "UNIDENTIFIED",
    'UNIDENTIED': 'UNIDENTIFIED',
    'UNIDENTIFY': 'UNIDENTIFIED'
})
clientstats = clientstats[clientstats['IPE'] != 'UNIDENTIFIED']

# function to map values into consistent categories
def categorize_ipe(ipe):
    if 'CUSTODIAN' in ipe or 'JANITOR' in ipe or 'CLEAN' in ipe or 'HOUSEKEEP' in ipe:
        return 'MAINTENANCE'
    if 'SECURITY' in ipe or 'GUARD' in ipe:
        return 'SECURITY'
    if 'CLERK' in ipe or 'ADMIN' in ipe or 'SECRETARY' in ipe or 'RECEPTIONIST' in ipe or 'OFFICE' in ipe or 'LIBRARY' in ipe:
        return 'ADMINISTRATIVE'
    if 'FOOD' in ipe or 'PREP' in ipe or 'COOK' in ipe or 'CHEF' in ipe or 'RESTAURANT' in ipe or 'DISHWASHER' in ipe or 'BAKER' in ipe or 'CAFE' in ipe:
        return 'FOOD SERVICE'
    if 'STOCK' in ipe or 'ORDER' in ipe or 'WAREHOUSE' in ipe or 'LOADER' in ipe or 'INVENTORY' in ipe or 'PACKER' in ipe:
        return 'STOCKING & WAREHOUSE'
    if 'CHILD CARE' in ipe or 'TEACH' in ipe:
        return 'EDUCATION'
    if 'RETAIL' in ipe or 'CASHIER' in ipe or 'SALES' in ipe or 'STORE' in ipe or 'CUSTOMER SERVICE' in ipe:
        return 'RETAIL'
    if 'MEDICAL' in ipe or 'NURSE' in ipe or 'HEALTH' in ipe or 'HOME HEALTH' in ipe or 'CAREGIVER' in ipe or 'NURSING' in ipe:
        return 'HEALTHCARE'
    if 'DRIVER' in ipe or 'DELIVERY' in ipe or 'CARGO' in ipe or 'AUTO' in ipe:
        return 'TRANSPORTATION'
    if 'MECHANIC' in ipe or 'TECHNICIAN' in ipe or 'MAINTENANCE' in ipe:
        return 'SKILLED TRADES'
    if 'IT' in ipe or 'TECH' in ipe or 'COMPUTER' in ipe or 'DATABASE' in ipe or 'SOFTWARE' in ipe:
        return 'TECHNOLOGY'
    return ipe

# apply categories
clientstats['IPE_CATEGORY'] = clientstats['IPE'].apply(categorize_ipe)

# count IPEs and display
ipe_counts = clientstats['IPE_CATEGORY'].value_counts()
print(ipe_counts)

# print most common career paths
print('The most common career paths are: ')
print(ipe_counts.head())

# DOB

print_divider('DOB')

# remove all NAs
clientstats = clientstats.dropna(subset=['DOB'])

# convert DOB column to datetime type
clientstats['DOB'] = pd.to_datetime(clientstats['DOB'], errors='coerce')

# function to calculate age based on DOB
def calculate_age(dob):
    dob_date = dob.date()
    today = date.today()
    age = today.year - dob_date.year
    if (today.month, today.day) < (dob_date.month, dob_date.day):
        age -= 1
    return age

# add age column
clientstats['AGE'] = clientstats['DOB'].apply(calculate_age)
    
# function to categorize DOB values into age ranges
def categorize_dob(age):
    if age < 20:
        return '< 20'
    elif age >= 20 and age <= 24:
        return '20-24'
    elif age >= 25 and age <= 29:
        return '25-29'
    elif age >= 30 and age <= 35:
        return '30-35'
    elif age >= 36 and age <= 45:
        return '36-45'
    elif age >= 46 and age <= 60:
        return '46-60'
    elif age > 60:
        return '> 60'
    return age

# apply categories
clientstats['DOB_CATEGORY'] = clientstats['AGE'].apply(categorize_dob)

# print the counts of age ranges
print(clientstats['DOB_CATEGORY'].value_counts())

# display the age ranges in a histogram
sns.histplot(clientstats['DOB_CATEGORY'])
plt.title('Age Ranges Histogram')
plt.xlabel('Age Range')
plt.ylabel('Frequency')
plt.savefig('age_range_hist.png')

# AGE RANGE IPE GOAL

print_divider('AGE RANGE IPE GOAL')

# group the DOB and IPE goals to find the relationship 
age_ipe_counts = clientstats.groupby(['DOB_CATEGORY', 'IPE_CATEGORY']).size().unstack(fill_value=0)
print(age_ipe_counts)

# create a heatmap
plt.figure(figsize=(14,8))
sns.heatmap(age_ipe_counts)
plt.title('IPE Age Range Heatmap')
plt.xlabel('IPE Goal Category')
plt.ylabel('Age Range')
plt.tight_layout()
plt.savefig('age_ipe_heatmap.png')
