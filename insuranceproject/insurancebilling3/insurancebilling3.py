import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

cleaned_data = pd.read_excel('cleaned_data.xlsx')

# AVERAGE NUMBER OF DAYS

cleaned_data['Date of Service'] = pd.to_datetime(cleaned_data['Date of Service'], errors='coerce')
cleaned_data['Feedback Session Date'] = pd.to_datetime(cleaned_data['Feedback Session Date'], errors='coerce')

cleaned_data['Days Between'] = (cleaned_data['Feedback Session Date'] - cleaned_data['Date of Service']).dt.days

avg_days_by_insurance = (
    cleaned_data.groupby('Insurance Name')['Days Between']
    .mean()
    .reset_index()
    .sort_values(by='Days Between', ascending=False)
)

avg_days_by_service = (
    cleaned_data.groupby('Type Of Services')['Days Between']
    .mean()
    .reset_index()
    .sort_values(by='Days Between', ascending=False)
)

print('Average Days Between by Insurance Company:')
print(avg_days_by_insurance)

print('\nAverage Days Between by Service Type:')
print(avg_days_by_service)

# VISUALIZATIONS

plt.figure(figsize=(10, 6))
plt.barh(
    avg_days_by_insurance['Insurance Name'],
    avg_days_by_insurance['Days Between'],
    color='skyblue'
)
plt.xlabel('Average Days Between Service & Feedback')
plt.ylabel('Insurance Company')
plt.title('Average Turnaround Time by Insurance Company (Fastest to Slowest)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('insurertime.png')

plt.figure(figsize=(8, 5))
plt.bar(
    avg_days_by_service['Type Of Services'],
    avg_days_by_service['Days Between'],
    color='salmon'
)
plt.ylabel('Average Days Between Service & Feedback')
plt.xlabel('Service Type')
plt.title('Average Turnaround Time by Service Type')
plt.tight_layout()
plt.savefig('servicetime.png')

# OUTLIERS

largest_days_between = cleaned_data[['First', 'Last Name', 'Days Between', 'City', 'Insurance Name', 'Clinician']].sort_values('Days Between').head(10)
smallest_days_between = cleaned_data[['First', 'Last Name', 'Days Between', 'City', 'Insurance Name', 'Clinician']].sort_values('Days Between', ascending=False).head(10)

print(largest_days_between)
print(largest_days_between['City'].value_counts())
print(largest_days_between['Insurance Name'].value_counts())

print(smallest_days_between)
print(smallest_days_between['City'].value_counts())
print(smallest_days_between['Insurance Name'].value_counts())
