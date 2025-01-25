import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data
# ChatGPT utilized for initial code generation + adapting to streamlit
@st.cache_data
def load_data():
    pi_project_count = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/pi_project_count.csv')
    projects = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/ff_funded.csv')
    unique_pis = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/unique_pis.csv')
    congo_companies = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/data/congo_sponsors.csv').iloc[:,0].tolist()
    fossil_companies = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/data/ff_sponsors.csv').iloc[:,0].tolist()
    dept_counts = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/department_counts.csv')  # New file
    return pi_project_count, projects, unique_pis, congo_companies, fossil_companies, dept_counts

pi_project_count, projects, unique_pis, congo_companies, fossil_companies, dept_counts = load_data()

st.title('Stanford Fossil Fuel Funding Analysis')

# Overall statistics
st.header('Overall Statistics')
total_pis = len(unique_pis)
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
    if any(project[col] in fossil_companies for col in ['Sponsor/Party']):
        dept_funding[dept]['ff'] += amount

# Now add the total number of projects from dept_counts to the department funding
dept_counts = dept_counts.set_index('Department')  # Set department as index for easy access

# Calculate the total number of projects by combining the funding and the department counts
dept_project_count = awarded_projects.groupby('Department').size()  # Get the count of awarded projects per department
dept_project_count = dept_project_count.add(dept_counts['Number of Projects'], fill_value=0)  # Add the number of projects from dept_counts

# Merge the dept_project_count into the dept_funding stats
dept_stats = []
for dept, amounts in dept_funding.items():
    total_projects = dept_project_count.get(dept, 0)  # Get the number of projects for that department
    ff_pct = (amounts['ff'] / amounts['total'] * 100) if amounts['total'] > 0 else 0
    dept_stats.append({
        'Department': dept,
        'FF Funding': amounts['ff'],
        'Total Funding': amounts['total'],
        'FF Percentage': ff_pct,
        'Total Projects': total_projects  # Add total projects for that department
    })

dept_df = pd.DataFrame(dept_stats)
dept_df = dept_df.sort_values('FF Funding', ascending=False)
n_depts = 6
top_depts = dept_df.head(n_depts)

# Overall statistics for funding
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

# Show the department funding table
st.subheader('Department Funding Breakdown')
st.dataframe(dept_df[['Department', 'Total Projects', 'FF Funding', 'Total Funding', 'FF Percentage']])

# TODO: Future Improvements
st.header('Future Improvements')
st.markdown("""
- Add faculty who are indirectly accepting FF funds through Industrial Affiliate Programs
- Add a year-by-year breakdown: is the number of faculty accepting fossil fuel money increasing,
  decreasing, or staying the same over time? I.e. is Stanford getting better or worse?
""")
