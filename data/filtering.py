import pandas as pd

df = pd.read_csv('/data/Project_List_Report_2005_2024.csv', encoding='latin1')
fossil_sponsors = pd.read_csv('data/ff_sponsors.csv').iloc[:,0].tolist()
congo_sponsors = pd.read_csv('data/nsors.csv').iloc[:,0].tolist()
bigtech_defense_sponsors = pd.read_csv('data/bigtech_defense_sponsors.csv').iloc[:,0].tolist()
all_sponsors = fossil_sponsors + congo_sponsors + bigtech_defense_sponsors

print(f"Original dataframe length: {len(df)}")
df_approved = df[df['Project Status'].isin(['Approved', 'Awarded'])]
print(f"Approved/awarded length: {len(df_approved)}")

matches = df_approved['Sponsor/Party'].astype(str).isin(fossil_sponsors)
ff_funded = df_approved[matches]
print(f"FF funded length: {len(ff_funded)}")
ff_funded.to_csv('processed/ff_funded.csv', index=False)

total_pis = len(df['Principal Investigator'].unique())
print(f"Total PIs: {total_pis}")
pd.DataFrame(df['Principal Investigator'].unique(), columns=['Principal Investigator']).to_csv('processed/unique_pis.csv', index=False)

# Get department counts and save to CSV
dept_counts = df['Department'].value_counts().reset_index()
dept_counts.columns = ['Department', 'Number of Projects']
dept_counts.to_csv('processed/department_counts.csv', index=False)
