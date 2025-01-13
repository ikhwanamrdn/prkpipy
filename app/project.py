import streamlit as st
from utils.project_db import save_project, create_projects_table
from utils.auth import get_user_role, get_pd_users

def project_page():
    # Ensure the 'projects' table is created
    create_projects_table()  # This will create the table if it doesn't exist

    # Ensure the user is logged in and has 'DirOps' role
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_role = get_user_role(st.session_state['name'])
        if user_role != 'DirOps':
            st.warning("Anda tidak memiliki akses ke halaman Project.")
            return
    else:
        st.warning("Anda harus login terlebih dahulu.")
        return

    st.title("Tambah Project untuk DirOps")
    
    # Input for project name
    project_name = st.text_input("Nama Project")
    
    # Get users with 'PD' role for the PD field dropdown
    pd_users = get_pd_users()  # Fetch users with role 'PD'
    pd_name = st.selectbox("Nama PD (Project Director)", pd_users)
    
    # Input for allocated mandays
    anggaran_mandays = st.number_input("Anggaran Mandays", min_value=1)
    
    # Add start month selector
    start_month = st.selectbox("Pilih Bulan Mulai", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

    # Map month names to numbers (1-12)
    month_mapping = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5,
        "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    start_month_num = month_mapping.get(start_month, 1)  # Default to January if something goes wrong

    if st.button("Submit"):
        if project_name and pd_name:
            # Save project with the start month and allocated mandays
            save_project(project_name, pd_name, anggaran_mandays, start_month_num)
            st.success(f"Project '{project_name}' berhasil ditambahkan!")
        else:
            st.error("Semua field harus diisi.")