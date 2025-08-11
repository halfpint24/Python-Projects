import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

evals_data = pd.read_excel('Evals Datasheet 24.xlsx')

st.header('Report Status metrics')
st.write('A vast majory of reports have been sent, while roughly 1 in 4 were N/A. There were only 3 payment issues.')
status_counts = evals_data['Report Status'].value_counts(dropna=False)

st.subheader('Report completion % by category')
fig, ax = plt.subplots()
ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%')
ax.axis('equal')
st.pyplot(fig)

st.subheader('Number of reports by report status')
st.write(status_counts)

st.header('Report Status based on Referral Source, Eval Type, Month')
evals_data = evals_data.dropna(subset=['Eval Date'])
evals_data['Eval Date'] = pd.to_datetime(evals_data['Eval Date'], errors='coerce')
evals_data['Month'] = evals_data['Eval Date'].dt.to_period('M')
print(evals_data['Eval Date'])

st.subheader('Referral Source')
st.write('The three most common referral sources are VR, insurance carrier, and private pay in that order.')
st.write('The other sources are used infrequently.')
st.write(evals_data['Referral Source'].value_counts())
st.bar_chart(evals_data['Referral Source'].value_counts())

st.subheader('Eval Type')
st.write('Psychological is the most common evaluation type.')
st.write(evals_data['Eval Type'].value_counts())
st.bar_chart(evals_data['Eval Type'].value_counts())

st.subheader('Month')
st.write('The amount of evaluations per month appears to fluctuate on a monthly basis, though fairly steady with the exception of the beginning of 2024 and 2025')
st.write(evals_data['Month'].astype(str).value_counts())
st.bar_chart(evals_data['Month'].astype(str).value_counts())

st.header('Investigating payment issues')
st.write('All 3 payment issues were from Orlando or the Orlando office, were Psychological eval type, and had a referral date within a span of less than 2 months.')
st.write('2 of the referral sources were private pay, with one being from an insurance carrier.')
payment_issues = evals_data[evals_data['Report Status'] == 'Payment Issues']
st.write(payment_issues[['Client Name', 'Referral Date', 'Eval Date', 'Referral Source', 'Eval Type', 'Location']])

st.subheader('Referral Source counts')
st.bar_chart(payment_issues['Referral Source'].value_counts())

st.subheader('Location counts')
st.bar_chart(payment_issues['Location'].value_counts())
