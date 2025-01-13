import mysql
import pandas as pd
import streamlit as st
from utils.project_db import create_projects_table, get_projects_by_role, save_project, update_project_data, assign_pm_to_project, assign_me_to_project, remove_me_from_project, get_assigned_mes
from utils.auth import get_user_role, get_pd_users, get_users_by_role

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

    st.title("Kelola Project untuk DirOps")

    # Toggle the visibility of the form using session_state
    if 'show_form' not in st.session_state:
        st.session_state['show_form'] = False

    # Button to show/hide the project form
    if st.button("Tambah Project"):
        st.session_state['show_form'] = not st.session_state['show_form']

    if st.session_state['show_form']:
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
                try:
                    # Save project with the start month and allocated mandays
                    save_project(project_name, pd_name, anggaran_mandays, start_month_num)
                    st.success(f"Project '{project_name}' berhasil ditambahkan!")
                    # Hide the form after submission
                    st.session_state['show_form'] = False
                except ValueError as ve:
                    # If project already exists, show a warning
                    st.warning(str(ve))  # Tampilkan pesan peringatan jika proyek sudah ada
            else:
                st.error("Semua field harus diisi.")

    # Toggle the visibility of the project list using session_state
    if 'show_project_list' not in st.session_state:
        st.session_state['show_project_list'] = True

    # Button to show/hide the project list
    if st.button("Tampilkan/Hapus Daftar Project"):
        st.session_state['show_project_list'] = not st.session_state['show_project_list']

    if st.session_state['show_project_list']:
        # Add section to display project activity (mandays_og and other details)
        st.subheader("Daftar Project yang Tersedia")
        # Fetch projects available for DirOps (all projects, as DirOps can access all)
        projects = get_projects_by_role(st.session_state['name'], 'DirOps')

        if projects:
            project_data = []
            for project in projects:
                project_id = project[0]
                project_name = project[1]
                pd_name = project[2]
                start_month = project[3]
                pm_name = project[4] if project[4] else "Belum ada PM"
                mandays_og = project[5]
                
                # Get ME for the project
                try:
                    me_names = get_assigned_mes(project_id)
                    me_names_str = ', '.join(me_names) if me_names else "Belum ada ME"
                    
                    project_data.append([project_id, project_name, pd_name, project[6], start_month, pm_name, mandays_og, me_names_str])

                except mysql.connector.Error as e:
                    st.error(f"Error accessing ME data: {e}")
                    continue

            # Create DataFrame for displaying project activity
            project_df = pd.DataFrame(project_data, columns=["ID", "Project Name", "PD", "Anggaran Mandays", "Start Month", "PM", "Mandays OG", "ME"])

            st.write("Aktivitas Proyek yang Tersedia:")
            st.dataframe(project_df)  # Display projects activity as a DataFrame table

            # Allow editing a selected project
            selected_project_id = st.selectbox("Pilih Proyek untuk Edit", [project[1] for project in projects], key="edit_project_selectbox")

            # Fetch project details to display
            selected_project = next(project for project in projects if project[1] == selected_project_id)

            # Show current project details in the input form
            project_name_edit = st.text_input("Nama Project", selected_project[1], key="edit_project_name")
            pd_name_edit = st.selectbox("Nama PD (Project Director)", [selected_project[2]], key="edit_pd_name")
            anggaran_mandays_edit = st.number_input("Anggaran Mandays", min_value=1, value=selected_project[6], key="edit_anggaran_mandays")
            
            # Correctly map the month number to month names
            month_mapping = {
                1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 
                7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
            }
            
            # Ensure start_month_num is valid
            start_month_num_edit = selected_project[3]
            start_month_edit = month_mapping.get(start_month_num_edit, "Jan")
            
            start_month_edit = st.selectbox("Pilih Bulan Mulai", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], index=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(start_month_edit), key="edit_start_month")

            # Map month names to numbers (1-12)
            start_month_num_edit = month_mapping.get(start_month_edit, 1)  # Default to January if something goes wrong

            # Get list of PMs and MEs for selection
            pm_users = get_users_by_role('PM')
            me_users = get_users_by_role('ME')

            # Select PM for the project
            if selected_project[4] != "None" and selected_project[4] in pm_users:
                selected_pm_index = pm_users.index(selected_project[4])
            else:
                selected_pm_index = 0  # Default to first PM if not found
            selected_pm = st.selectbox("Pilih Project Manager (PM)", pm_users, index=selected_pm_index, key="edit_pm_selectbox")

            # Move ME to a separate section
            st.subheader("Pilih Manager Engineer (ME) untuk Project")
            assigned_mes = get_assigned_mes(selected_project[0])  # Get assigned MEs for the selected project
            selected_me = st.selectbox("Pilih Manager Engineer (ME)", me_users, index=0, key="edit_me_selectbox")
            
            # Add option to add/remove ME from the project
            add_me_button, remove_me_button = st.columns([1, 1])

            with add_me_button:
                if st.button("Tambah ME ke Project"):
                    # Add selected ME to the project
                    if selected_me:
                        try:
                            assign_me_to_project(selected_project[0], selected_me)
                            st.success(f"ME {selected_me} berhasil ditambahkan ke proyek {selected_project[1]}.")
                        except Exception as e:
                            st.error(f"Error adding ME: {e}")
                    else:
                        st.error("Pilih ME yang ingin ditambahkan.")

            with remove_me_button:
                if st.button("Hapus ME dari Project"):
                    # Remove selected ME from the project
                    if selected_me in assigned_mes:
                        try:
                            remove_me_from_project(selected_project[0], selected_me)
                            st.success(f"ME {selected_me} berhasil dihapus dari proyek {selected_project[1]}.")
                        except Exception as e:
                            st.error(f"Error removing ME: {e}")
                    else:
                        st.error(f"ME {selected_me} tidak terdaftar di proyek ini.")

            # Update project button
            if st.button("Update Project"):
                if project_name_edit and pd_name_edit:
                    try:
                        # Update project with new values
                        update_project_data(selected_project[0], project_name_edit, pd_name_edit, anggaran_mandays_edit, start_month_num_edit)
                        
                        # Assign the selected PM to the project
                        assign_pm_to_project(selected_project[0], selected_pm)

                        st.success(f"Project '{project_name_edit}' berhasil diperbarui dengan PM '{selected_pm}'!")
                    except Exception as e:
                        st.error(f"Gagal memperbarui proyek: {e}")
                else:
                    st.error("Semua field harus diisi.")
    else:
        st.write("Tidak ada project yang ditemukan.")