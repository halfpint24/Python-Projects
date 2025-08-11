import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

matplotlib.use('Agg')

def print_divider(str):
    print('---------------------------------')
    print(str)
    print('---------------------------------')

# Open dataset and print columns and data
clientstats = pd.read_csv('clientstats.csv')

# Print data information
print_divider('Data Information')
clientstats.head()
clientstats.info()
clientstats.describe()
print(clientstats.columns)

# DISABILITY

print_divider('Disability')

disability_data = clientstats.copy()

# strip text and all uppercase
disability_data['DISABILITY'] = disability_data['DISABILITY'].astype(str).str.strip().str.upper()

# replace unidentified values
disability_data['DISABILITY'] = disability_data['DISABILITY'].replace({
    'UNIDENIFIED': "UNIDENTIFIED",
    'UNIDENTIED': 'UNIDENTIFIED'
})


# function to map values into consistent categories
def categorize_disability(value):
    if pd.isna(value) or value == 'UNIDENTIFIED':
        return 'UNIDENTIFIED'
    if 'INTELLECTUAL' in value or 'COGNITIVE' in value:
        return 'INTELLECTUAL DISABILITY'
    if 'AUTISM' in value:
        return 'AUTISM'
    if 'LEARNING' in value:
        return 'LEARNING DISABILITY'
    if 'HEARING' in value:
        return 'HEARING IMPAIRMENT'
    if 'VISUAL' in value or 'VISION' in value:
        return 'VISUAL IMPAIRMENT'
    if 'ORTHOPEDIC' in value:
        return 'ORTHOPEDIC'
    if 'NEOPLASM' in value or 'CANCER' in value:
        return 'CANCER'
    if 'PSYCHIATRIC' in value or 'MENTAL' in value:
        return 'MENTAL HEALTH'
    if 'NEURO' in value:
        return 'NEUROLOGICAL'
    if 'PHYSICAL' in value or 'MOBILITY' in value:
        return 'PHYSICAL IMPAIRMENT'
    return 'OTHER'


# apply categories
disability_data['DISABILITY_CATEGORY'] = disability_data['DISABILITY'].apply(categorize_disability)

print(disability_data['DISABILITY_CATEGORY'])

# count each disability category and display
disability_counts = disability_data['DISABILITY_CATEGORY'].value_counts()
print(disability_counts)

# create a chart and save it as a png file
plt.figure(figsize=(12, 6))
sns.barplot(x=disability_counts.index, y=disability_counts.values)
plt.title('Disability Type Counts')
plt.xlabel('Disability')
plt.ylabel('Type')
plt.tight_layout()
plt.savefig("disability_chart.png")

# STATUS

print_divider('Status')

status_data = clientstats.copy()

# remove all NAs
status_data = status_data.dropna(subset=['STATUS'])


# function to map values into consistent categories
def categorize_status(value):
    if 'PENDING OJT' in value or 'OJT PENDING' in value:
        return 'PENDING OJT'
    if 'EMPLOYMENT BENCHMARK' in value:
        return 'OTHER'
    elif 'EMPLOY' in value or 'CLOSED' in value or 'INTAKE' in value or 'CAMP' in value or 'CLOSURE' in value:
        return value
    return 'OTHER'


# apply categories
status_data['STATUS_CATEGORY'] = status_data['STATUS'].apply(categorize_status)

print(status_data['STATUS_CATEGORY'])

# count each status category and display
status_counts = status_data['STATUS_CATEGORY'].value_counts()
print(status_counts)

# create a chart and save it as a png file
plt.figure(figsize=(12, 6))
sns.barplot(x=status_counts.index, y=status_counts.values)
plt.title('Status Type Counts')
plt.xlabel('Status')
plt.ylabel('Type')
plt.tight_layout()
plt.savefig("status_chart.png")

# LOCATION

print_divider('Location')

location_data = clientstats.copy()

# remove zip codes, strip, uppercase
location_data['LOCATION'] = location_data['LOCATION'].str.replace(r'\s*\d{5}$', '', regex=True).str.strip().str.upper()

# replace all NAs with filler values
location_data['LOCATION'] = location_data['LOCATION'].fillna("Unknown Location")


# filter location function
def filter_location(location):
    if 'ORLANDO' in location:
        return 'ORLANDO'

    return location


# apply locations
location_data['LOCATION'] = location_data['LOCATION'].apply(filter_location)

# count each location and display
location_counts = location_data['LOCATION'].value_counts()
print(location_counts)

# IPE

print_divider('IPE')

ipe_data = clientstats.copy()

# strip and upper
ipe_data['IPE'] = ipe_data['IPE'].astype(str).str.strip().str.upper()

# replace unidentified values
ipe_data['IPE'] = ipe_data['IPE'].replace({
    'UNIDENIFIED': "UNIDENTIFIED",
    'UNIDENTIED': 'UNIDENTIFIED',
    'UNIDENTIFY': 'UNIDENTIFIED'
})

# remove unidentified values
ipe_data = ipe_data[ipe_data['IPE'] != 'UNIDENTIFIED']


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
ipe_data['IPE_CATEGORY'] = ipe_data['IPE'].apply(categorize_ipe)

# count IPEs and display
ipe_counts = ipe_data['IPE_CATEGORY'].value_counts()
print(ipe_counts)

# print most common IPE
print('The most common IPE is {}'.format(str(ipe_counts.idxmax())))
