import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data
# ChatGPT utilized for initial code generation + adapting to streamlit
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    pi_project_count = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/pi_project_count.csv')
    projects = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/project_list_report_2005_2024_filtered.csv')
    unique_pis = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/unique_pis.csv')
    congo_companies = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/data/congo_sponsors.csv').iloc[:,0].tolist()
    fossil_companies = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/data/ff_sponsors.csv').iloc[:,0].tolist()
    bigtech_defense_companies = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/data/bigtech_defense_sponsors.csv').iloc[:,0].tolist()
    dept_counts = pd.read_csv('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/department_counts.csv')
    active_projects_by_faculty = pd.read_pickle('https://raw.githubusercontent.com/fffreestanford/stanford-sponsored-research/refs/heads/main/processed/active_projects_by_company_and_faculty.pkl')
    return pi_project_count, projects, unique_pis, congo_companies, fossil_companies, bigtech_defense_companies, dept_counts, active_projects_by_faculty

pi_project_count, projects, unique_pis, congo_companies, fossil_companies, bigtech_defense_companies, dept_counts, active_projects_by_faculty = load_data()

st.title('Stanford Fossil Fuel and Big Tech Funding')

# Add a selectbox to choose the sponsor type
sponsor_type = st.selectbox(
    'Select Sponsor Type',
    ['Fossil Fuel Sponsors', 'Big Tech / Defense Sponsors']
)

# Filter departments based on selected sponsor type
if sponsor_type == 'Fossil Fuel Sponsors':
    sponsor_list = fossil_companies
    sponsor_label = "Fossil Fuel Sponsors"
else:
    sponsor_list = bigtech_defense_companies
    sponsor_label = "Big Tech / Defense Sponsors"

# Filter departments where FF Projects is greater than 0 and sponsored by the selected sponsor type
dept_df_nonzero_ff = dept_counts[dept_counts['FF Projects'] > 0]

# Create a new column to identify which sponsor categories are in each department
dept_df_nonzero_ff['Sponsored by Fossil Fuel or Big Tech/Defense'] = dept_df_nonzero_ff['Sponsor'].apply(
    lambda sponsor: sponsor in sponsor_list
)

# Filter departments where the selected sponsor type is present
filtered_dept_df = dept_df_nonzero_ff[dept_df_nonzero_ff['Sponsored by Fossil Fuel or Big Tech/Defense']]

# Create the bar chart for departments with projects sponsored by the selected sponsor type
fig_bar = px.bar(
    filtered_dept_df,
    x='FF Percentage',
    y='Department',
    orientation='h',
    title=f'Department Projects Sponsored by {sponsor_label}'
)

# Show the department project breakdown table
st.plotly_chart(fig_bar)

# Show the department project breakdown table
st.subheader(f'Department Project Breakdown for {sponsor_label}')
st.dataframe(filtered_dept_df[['Department', 'Total Projects', 'FF Projects', 'FF Percentage']])


# Filter the list of Principal Investigators based on those who appear in the projects dataset
active_pis = projects['Principal Investigator'].unique()
available_pis = unique_pis[unique_pis['Principal Investigator'].isin(active_pis)]

# Select a PI (faculty member)
st.header('Select a Principal Investigator (PI)')
selected_pi = st.selectbox('Select a Principal Investigator', available_pis['Principal Investigator'])

# Retrieve the projects for the selected PI from the active_projects_by_faculty dictionary
selected_projects = []
sponsors_with_projects = []

for sponsor, faculty_dict in active_projects_by_faculty.items():
    if selected_pi in faculty_dict:
        faculty_projects = faculty_dict[selected_pi]
        if isinstance(faculty_projects, list) or isinstance(faculty_projects, dict):
            faculty_projects = pd.Series(faculty_projects)
        selected_projects.append(faculty_projects)
        
        if faculty_projects.sum() > 0:
            sponsors_with_projects.append(sponsor)

# Combine the yearly counts for the selected PI across all sponsors
if selected_projects:
    yearly_data = pd.DataFrame(selected_projects).transpose()
    yearly_data = yearly_data.rename_axis('Year').reset_index()

    # Filter where the number of projects is > 0 for the selected PI
    filtered_yearly_data = yearly_data[['Year'] + sponsors_with_projects]
    
    st.subheader(f'Projects Per Year for {selected_pi} by Sponsor')
    fig = go.Figure()

    # Plot each sponsor if they have more than 0 projects
    for sponsor in sponsors_with_projects:
        fig.add_trace(go.Scatter(
            x=filtered_yearly_data['Year'],
            y=filtered_yearly_data[sponsor],
            mode='lines+markers',
            name=sponsor
        ))

    fig.update_layout(
        title=f'Projects Per Year for {selected_pi} by Sponsor',
        xaxis_title='Year',
        yaxis_title='Number of Projects',
        showlegend=True
    )
    st.plotly_chart(fig)
else:
    st.write("No projects found for the selected PI.")
