import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data
# ChatGPT utilized for initial code generation + adapting to streamlit
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

# Filter the list of Principal Investigators based on those who appear in the projects dataset
active_pis = projects['Principal Investigator'].unique()  # Get all PIs from the projects dataset
available_pis = unique_pis[unique_pis['Principal Investigator'].isin(active_pis)]  # Filter the unique PIs based on those in projects

# Select a PI (faculty member)
st.header('Select a Principal Investigator (PI)')
selected_pi = st.selectbox('Select a Principal Investigator', available_pis['Principal Investigator'])

# Retrieve the projects for the selected PI from the active_projects_by_faculty dictionary
selected_projects = []
sponsors_with_projects = []  # To keep track of sponsors that have more than 0 projects for the selected PI

for sponsor, faculty_dict in active_projects_by_faculty.items():
    if selected_pi in faculty_dict:
        faculty_projects = faculty_dict[selected_pi]
        selected_projects.append(faculty_projects)
        
        # Track sponsors where the selected PI has more than 0 projects
        if (faculty_projects > 0).any():  # If there are any years where the PI has more than 0 projects for this sponsor
            sponsors_with_projects.append(sponsor)

# Combine the yearly counts for the selected PI across all sponsors
if selected_projects:
    # Create a DataFrame to hold the data for plotting
    yearly_data = pd.DataFrame(selected_projects).transpose()

    # Transpose and clean up the data to have years as rows and sponsors as columns
    yearly_data = yearly_data.rename_axis('Year').reset_index()

    # Filter the sponsors where the number of projects is > 0 for the selected PI
    filtered_yearly_data = yearly_data[['Year'] + sponsors_with_projects]

    # Plot the line chart
    st.subheader(f'Projects Per Year for {selected_pi} by Sponsor')
    fig = go.Figure()

    # Plot each sponsor as a separate line if they have more than 0 projects
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
