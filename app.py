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

# Calculate the number of fossil-funded projects by department
dept_funding = {}
awarded_projects = projects[projects['Project Status'] == 'Awarded']

# Count FF-funded projects by department
ff_projects_by_dept = awarded_projects.groupby('Department').size()

# Add the total number of projects from dept_counts
dept_counts = dept_counts.set_index('Department')  # Set department as index for easy access
total_projects_by_dept = dept_counts['Number of Projects']  # Get total number of projects per department

# Calculate the FF projects percentage for each department
dept_stats = []
for dept in total_projects_by_dept.index:
    ff_projects = ff_projects_by_dept.get(dept, 0)  # Number of FF-funded projects for this department
    total_projects = total_projects_by_dept[dept]  # Total number of projects for this department
    ff_pct = (ff_projects / total_projects * 100) if total_projects > 0 else 0
    dept_stats.append({
        'Department': dept,
        'FF Projects': ff_projects,
        'Total Projects': total_projects,
        'FF Percentage': ff_pct
    })

dept_df = pd.DataFrame(dept_stats)
dept_df = dept_df.sort_values('FF Projects', ascending=False)
n_depts = 6
top_depts = dept_df.head(n_depts)

# Overall statistics for projects
total_projects = dept_df['Total Projects'].sum()
ff_projects = dept_df['FF Projects'].sum()
ff_projects_pct = (ff_projects / total_projects * 100) if total_projects > 0 else 0

st.write(f"Total Projects: {total_projects:,.0f}")
st.write(f"Fossil Fuel Projects: {ff_projects:,.0f}")
st.write(f"Percentage from Fossil Fuel Projects: {ff_projects_pct:.1f}%")

# Visualizations
st.header('Visualizations')

# Filter the departments where FF Projects is greater than 0
dept_df_nonzero_ff = dept_df[dept_df['FF Projects'] > 0]

# Top departments bar chart (based on FF project count)
fig_bar = px.bar(
    dept_df_nonzero_ff,  # Use the filtered dataframe
    x='FF Percentage',
    y='Department',
    orientation='h',
    title=f'Top {n_depts} Departments by FF Project Percentage',
    color_discrete_sequence=['#ff9999']
)
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar)

# Show the department project breakdown table
st.subheader('Department Project Breakdown (FF Projects > 0)')
st.dataframe(dept_df_nonzero_ff[['Department', 'Total Projects', 'FF Projects', 'FF Percentage']])

# Table of Fossil-Funded PIs and their Project Counts
st.header('Fossil-Funded PIs and their Projects')

# Calculate the number of projects for each PI involved in FF-funded projects
ff_funded_pis = projects['Principal Investigator'].value_counts()

# Create a DataFrame for PIs and their project counts
pi_projects_df = pd.DataFrame({
    'Principal Investigator': ff_funded_pis.index,
    'Number of Projects': ff_funded_pis.values
})

st.dataframe(pi_projects_df)

# Add interactivity: allow user to select a PI
selected_pi = st.selectbox('Select a Principal Investigator', pi_projects_df['Principal Investigator'])

# Show the sponsors for the selected PI
st.subheader(f'Sponsors for {selected_pi}')
sponsors_for_pi = awarded_projects[awarded_projects['Principal Investigator'] == selected_pi]['Sponsor/Party'].unique()

# Display the sponsors
if len(sponsors_for_pi) > 0:
    st.write(", ".join(sponsors_for_pi))
else:
    st.write("No sponsors found for this PI.")
