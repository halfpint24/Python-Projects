import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

cleaned_data = pd.read_excel('Week_4_Cleaned.xlsx')

def categorize_ppt_hours(val):
    if isinstance(val, int):
        if val <= 10:
            return '0-10 hours'
        if val >= 11 and val <= 20:
            return '11-20 hours'
        if val >= 21 and val <= 40:
            return '21-40 hours'
        if val >= 41:
            return '41+ hours'

    if isinstance(val, str):
        if val == 'Yes' or val == 'PPT Hours Completed':
            return '41+ hours'
        if val == 'No':
            return '0-10 hours'

    return 'Unknown hours completed'


cleaned_data['PPT Hours Category'] = cleaned_data['PPT Hours Completed'].apply(categorize_ppt_hours)
print(cleaned_data['PPT Hours Category'])
print(cleaned_data['PPT Hours Category'].value_counts())

ppt_status_ct = pd.crosstab(cleaned_data['CLIENT STATUS'], cleaned_data['PPT Hours Category'])
ppt_status_ct.plot(kind='barh', stacked=True)
plt.ylabel('Number of Clients')
plt.title('Client Status by PPT Hours Completed')
plt.legend(title='Client Status')
plt.tight_layout()
plt.savefig('ppt_status_stacked_bar.png')


def find_notes_completed_without_resume(val):
    if val['Case Notes Submitted'] == 'Yes':
        if val['Resume Completed'] != 'Yes':
            return 'Yes'

    return 'No'


notes_completed_without_resume = cleaned_data.copy()
notes_completed_without_resume['Case Notes Completed Without Resume'] = notes_completed_without_resume.apply(find_notes_completed_without_resume, axis=1)
notes_completed_without_resume[['CLIENT NAME (END DATE ONLY)', 'Case Notes Submitted', 'Resume Completed', 'Case Notes Completed Without Resume']].to_excel('notes_completed_without_resume.xlsx')
