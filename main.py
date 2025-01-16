import streamlit as st
from app.login import login_page
from app.dashboard import dashboard_page
from app.absen import absen_page
from app.project import project_page  # DirOps project management page
from app.project_pd import project_pd_page  # PD project management page
from app.project_pm import project_pm_page  # PM project management page
from app.kpi_pd import kpi_pd_page  # KPI PD management page
from utils.mcs_roi_db import create_mcs_roi_table
from utils.pm_req_db import create_pm_requests_table
from utils.project_db import create_projects_table  # Import create_projects_table function
from utils.kpi_pd_db import create_kpi_pd_table  # Import create_kpi_pd_table function

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['page'] = "login"
        st.session_state['role'] = None  # Tambahkan peran default None

    # Pastikan tabel projects dibuat terlebih dahulu
    create_projects_table()

    # Lalu buat tabel yang bergantung pada tabel projects
    create_mcs_roi_table()
    create_pm_requests_table()
    create_kpi_pd_table()

    # Use st.query_params to get the page (defaults to "login")
    page = st.query_params.get("page", ["login"])[0]

    # Check if the user is logged in
    if st.session_state['logged_in']:
        # Filter menu berdasarkan peran pengguna
        menu_options = ["Dashboard", "Absen"]
        role = st.session_state.get('role')

        if role == "DirOps":
            menu_options.append("Project (DirOps)")
        if role == "PD":
            menu_options.extend(["Project (PD)", "KPI (PD)"])
        if role == "PM":
            menu_options.append("Project (PM)")

        # Tampilkan menu di sidebar
        menu = st.sidebar.radio("Pilih Halaman", menu_options)

        # Tentukan halaman berdasarkan pilihan menu
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
        elif menu == "KPI (PD)":
            st.session_state['page'] = "kpi_pd"

        # Tampilkan halaman sesuai pilihan
        if st.session_state['page'] == "dashboard":
            dashboard_page()
        elif st.session_state['page'] == "absen":
            absen_page()
        elif st.session_state['page'] == "project" and role == "DirOps":
            project_page()  # DirOps can manage projects here
        elif st.session_state['page'] == "project_pd" and role == "PD":
            project_pd_page()  # PD can manage projects here
        elif st.session_state['page'] == "project_pm" and role == "PM":
            project_pm_page()  # PM can manage project assignments here
        elif st.session_state['page'] == "kpi_pd" and role == "PD":
            kpi_pd_page()  # PD can manage KPI here
        else:
            st.warning("Anda tidak memiliki akses ke halaman ini.")
    
    else:
        # Show login page if the user is not logged in
        login_page()

if __name__ == "__main__":
    main()