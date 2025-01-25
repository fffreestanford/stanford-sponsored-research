import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data
# ChatGPT utilized for initial code generation + adapting to streamlit
@st.cache_data
def load_data():
    pi_project_count = pd.read_csv('processed/pi_project_count.csv')
    projects = pd.read_csv('data/Project_List_Report_2005_2024.csv')
    congo_companies = pd.read_csv('data/congo_sponsors.csv')
    fossil_companies = pd.read_csv('data/fossil_sponsors.csv')
    return pi_project_count, projects, congo_companies, fossil_companies

pi_project_count, projects, congo_companies, fossil_companies = load_data()

st.title('Stanford Fossil Fuel Funding Analysis')

# Overall statistics
st.header('Overall Statistics')
total_pis = len(projects['Principal Investigator'].unique())
ff_funded_pis = len(pi_project_count)
ff_funded_percent = (ff_funded_pis / total_pis * 100)

st.write(f'Total PIs: {total_pis}')
st.write(f'PIs with FF Funding: {ff_funded_pis}')
st.write(f'Percentage of PIs with FF Funding: {ff_funded_percent:.1f}%')

# Funding analysis
st.header('Funding Analysis')

# Calculate funding by department
dept_funding = {}
awarded_projects = projects[projects['Project Status'] == 'Awarded']

for idx, project in awarded_projects.iterrows():
    dept = project['Department']
    amount = float(project['Funded'].replace('$', '').replace(',', ''))

    if dept not in dept_funding:
        dept_funding[dept] = {'ff': 0, 'total': 0}

    dept_funding[dept]['total'] += amount

    # Check if any sponsor column matches FF companies
    if any(project[col] in fossil_companies['Company Name'].values for col in ['Sponsor', 'Prime Sponsor']):
        dept_funding[dept]['ff'] += amount

# Calculate percentages and create dataframe
dept_stats = []
for dept, amounts in dept_funding.items():
    ff_pct = (amounts['ff'] / amounts['total'] * 100) if amounts['total'] > 0 else 0
    dept_stats.append({
        'Department': dept,
        'FF Funding': amounts['ff'],
        'Total Funding': amounts['total'],
        'FF Percentage': ff_pct
    })

dept_df = pd.DataFrame(dept_stats)
dept_df = dept_df.sort_values('FF Funding', ascending=False)
n_depts = 6
top_depts = dept_df.head(n_depts)

# Overall statistics
total_funding = dept_df['Total Funding'].sum()
ff_funding = dept_df['FF Funding'].sum()
ff_funding_pct = (ff_funding / total_funding * 100) if total_funding > 0 else 0

st.write(f"Total Funding: ${total_funding:,.2f}")
st.write(f"Fossil Fuel Funding: ${ff_funding:,.2f}")
st.write(f"Percentage from Fossil Fuel Sources: {ff_funding_pct:.1f}%")

# Visualizations
st.header('Visualizations')

# Overall pie chart
fig_pie = go.Figure(data=[go.Pie(
    labels=['FF Funding', 'Other Funding'],
    values=[ff_funding_pct, 100-ff_funding_pct],
    marker_colors=['#ff9999', '#66b3ff']
)])
fig_pie.update_layout(title='Stanford-Wide Sponsored Research Funds')
st.plotly_chart(fig_pie)

# Top departments bar chart
fig_bar = px.bar(
    top_depts,
    x='FF Percentage',
    y='Department',
    orientation='h',
    title=f'Top {n_depts} Departments by FF Funding Percentage',
    color_discrete_sequence=['#ff9999']
)
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar)

# TODO:
st.header('Future Improvements')
st.markdown("""
- Add faculty who are indirectly accepting FF funds through Industrial Affiliate Programs
- Add a year-by-year breakdown: is the number of faculty accepting fossil fuel money increasing,
  decreasing, or staying the same over time? I.e. is Stanford getting better or worse?
""")
