import streamlit as st
import pandas as pd
from utils.project_db import get_projects_by_pd, get_users_by_role, assign_pm_to_project

def project_pd_page():
    # Ensure the user is logged in and has 'PD' role
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_role = st.session_state.get('role', '')
        # Allow only 'PD' to access the page
        if user_role != 'PD':
            st.warning("Anda tidak memiliki akses ke halaman Project.")
            return
    else:
        st.warning("Anda harus login terlebih dahulu.")
        return

    st.title("Kelola Project untuk Project Director")

    # Get the logged-in PD's name and fetch the projects assigned to them
    pd_name = st.session_state['name']
    projects = get_projects_by_pd(pd_name)  # Fetch projects assigned to this PD

    if projects:
        # Prepare data for display in a structured table
        project_data = []
        for project in projects:
            project_name = project[1]
            start_month = project[3]
            pm_name = project[4] if project[4] else "Belum ada PM"
            project_data.append([project_name, start_month, pm_name])

        # Create DataFrame with proper column headers
        project_df = pd.DataFrame(project_data, columns=["Project Name", "Start Month", "PM"])

        # Display the project data in a neat table
        st.write("Project yang ditugaskan kepada Anda:")
        st.dataframe(project_df)  # Display projects as a DataFrame table

        # Select project to assign PM
        project_names = [project[1] for project in projects]  # List of project names
        selected_project_name = st.selectbox("Pilih Project yang akan ditugaskan PM", project_names)

        # Get the selected project details
        selected_project = next(project for project in projects if project[1] == selected_project_name)
        selected_project_id = selected_project[0]  # Project ID
        current_pm = selected_project[4] if selected_project[4] else "None"  # Existing PM (if any)

        # Check if PM is already assigned
        if current_pm != "None":
            st.warning(f"Project Manager sudah ditetapkan untuk proyek {selected_project_name}: {current_pm}")

        # Get list of users with role 'PM'
        pm_users = get_users_by_role('PM')
        pm_name = st.selectbox("Pilih Project Manager (PM)", pm_users, index=pm_users.index(current_pm) if current_pm != "None" else 0)

        # Button to assign PM to selected project
        if st.button("Assign PM"):
            if pm_name:
                try:
                    # Assign the selected PM to the project
                    if current_pm != "None":
                        st.warning(f"PM sudah ditetapkan untuk proyek {selected_project_name}: {current_pm}")
                    else:
                        assign_pm_to_project(selected_project_id, pm_name)
                        st.success(f"Project Manager {pm_name} berhasil ditugaskan untuk project {selected_project_name}.")
                except Exception as e:
                    st.error(f"Gagal menetapkan PM: {e}")
            else:
                st.warning("Anda harus memilih Project Manager terlebih dahulu.")
    else:
        st.write("Tidak ada project yang ditugaskan untuk Anda saat ini.")