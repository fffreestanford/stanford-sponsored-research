import pandas as pd

df = pd.read_csv('~/Downloads/Project_List_Report_2005_2024.csv', encoding='latin1')
fossil_sponsors = pd.read_csv('~/Downloads/ff_sponsors.csv').iloc[:,0].tolist()
print(f"Original dataframe length: {len(df)}")

df_approved = df[df['Project Status'].isin(['Approved', 'Awarded'])]
print(f"Approved/awarded length: {len(df_approved)}")

matches = df_approved['Sponsor/Party'].astype(str).isin(fossil_sponsors)
ff_funded = df_approved[matches]
print(f"FF funded length: {len(ff_funded)}")

ff_funded.to_csv('processed/ff_funded.csv', index=False)
