import pandas as pd
from datetime import datetime

evals_data = pd.read_excel('Evals Datasheet 24.xlsx')

# FLAGGING DATES

client_eval_feedback_dates = evals_data[['Client Name', 'Eval Date', 'Feedback Session Date']]

def flag_dates(row):
    if pd.isna(row['Feedback Session Date']):
        return 'Flagged: no Feedback Session Date'
    if 'N/A' in str(row['Feedback Session Date']):
        return 'Flagged: Feedback Dession Date N/A - V/R'
    if isinstance(row['Feedback Session Date'], datetime) and isinstance(row['Eval Date'], datetime):
        if row['Feedback Session Date'] < row['Eval Date']:
            return 'Flagged: Feedback Session Date before Eval Date'
    
    return 'Not Flagged'

client_eval_feedback_dates = client_eval_feedback_dates.copy()
client_eval_feedback_dates['Flagged'] = client_eval_feedback_dates.apply(flag_dates, axis=1)
    
print(client_eval_feedback_dates.head(10))

# CLIENT SCHEDULER

clients_scheduled_by_schedulers = evals_data.groupby('Scheduler')['Client Name'].count()
print(clients_scheduled_by_schedulers.sort_values(ascending=False))

# NO FEEDBACK SESSION DATE

missing_date = evals_data[(evals_data['Feedback Session Time'].notna() | (evals_data['Feedback Session Time'] == 'N/A - VR')) & (evals_data['Feedback Session Date'].isna())]

print(missing_date[['Client Name', 'Feedback Session Date', 'Feedback Session Time']])
