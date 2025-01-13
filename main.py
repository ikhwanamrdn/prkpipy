import streamlit as st
from app.login import login_page
from app.dashboard import dashboard_page
from app.absen import absen_page
from app.project import project_page  # DirOps project management page
from app.project_pd import project_pd_page  # PD project management page
from app.project_pm import project_pm_page  # PM project management page
from utils.auth import create_users_table, get_user_role
from utils.project_db import create_projects_table  # Import create_projects_table function

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['page'] = "login"

    # Ensure the projects table exists
    create_projects_table()

    create_users_table()

    # Use st.query_params to get the page (defaults to "login")
    page = st.query_params.get("page", ["login"])[0]

    # Check if the user is logged in
    if st.session_state['logged_in']:
        # After login, users are directed to the dashboard page
        menu = st.sidebar.radio("Pilih Halaman", ["Dashboard", "Absen", "Project (DirOps)", "Project (PD)", "Project (PM)"])

        if menu == "Dashboard":
            st.session_state['page'] = "dashboard"
        elif menu == "Absen":
            st.session_state['page'] = "absen"
        elif menu == "Project (DirOps)":
            st.session_state['page'] = "project"
        elif menu == "Project (PD)":
            st.session_state['page'] = "project_pd"
        elif menu == "Project (PM)":
            st.session_state['page'] = "project_pm"

        # Display the Page Based on the Selection
        if st.session_state['page'] == "dashboard":
            dashboard_page()
        elif st.session_state['page'] == "absen":
            absen_page()
        elif st.session_state['page'] == "project" and st.session_state['role'] == 'DirOps':
            project_page()  # DirOps can manage projects here
        elif st.session_state['page'] == "project_pd" and st.session_state['role'] == 'PD':
            project_pd_page()  # PD can manage projects here
        elif st.session_state['page'] == "project_pm" and st.session_state['role'] == 'PM':
            project_pm_page()  # PM can manage project assignments here
        else:
            st.warning("Anda tidak memiliki akses ke halaman ini.")
    
    else:
        # Show login page if the user is not logged in
        login_page()

if __name__ == "__main__":
    main()