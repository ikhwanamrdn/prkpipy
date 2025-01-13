import streamlit as st
import pandas as pd
from utils.project_db import create_projects_table, get_connection, get_projects_by_pm, get_users_by_role, assign_me_to_project

def project_pm_page():
    # Ensure the table 'projects' exists before proceeding
    create_projects_table()

    # Halaman untuk mengelola Project Manager (PM)
    st.title("Assign Manager Engineer (ME) ke Proyek")
    st.write("Gunakan fitur ini untuk menetapkan Manager Engineer (ME) ke dalam proyek.")

    # Mendapatkan proyek yang sudah ditugaskan kepada PM
    pm_name = st.session_state['name']  # Ambil PM dari session state
    projects = get_projects_by_pm(pm_name)  # Mengambil proyek yang sudah ditugaskan ke PM oleh PD

    if not projects:
        st.warning("Tidak ada proyek yang ditugaskan kepada Anda.")
        return

    # Menampilkan proyek dalam bentuk DataFrame
    project_data = []
    for project in projects:
        project_name = project[1]  # Nama proyek
        start_month = project[3]  # Bulan mulai
        pm_name = project[4] if project[4] else "Belum ada PM"  # Nama PM jika ada

        # Mendapatkan daftar Manager Engineers (MEs) yang ditugaskan pada proyek ini
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.name FROM project_me pm
                    JOIN users u ON pm.me_id = u.id
                    WHERE pm.project_id = %s
                """, (project[0],))
                me_names = [row[0] for row in cursor.fetchall()]

        # Menampilkan nama-nama ME atau "Belum ada ME"
        me_names = ', '.join(me_names) if me_names else "Belum ada ME"
        project_data.append([project_name, start_month, pm_name, me_names])

    # Membuat DataFrame dengan nama kolom yang sesuai
    project_df = pd.DataFrame(project_data, columns=["Project Name", "Start Month", "PM", "ME"])

    # Menampilkan data proyek dalam bentuk tabel yang rapi
    st.write("Project yang ditugaskan kepada Anda:")
    st.dataframe(project_df)  # Menampilkan proyek sebagai tabel DataFrame

    # Pilih proyek yang akan dikelola
    project_names = [project[1] for project in projects]  # Daftar nama proyek
    selected_project_name = st.selectbox("Pilih Proyek yang akan dikelola", project_names)

    # Mengambil detail proyek yang dipilih
    selected_project = next(project for project in projects if project[1] == selected_project_name)
    selected_project_id = selected_project[0]  # ID Proyek

    # Mendapatkan daftar pengguna dengan peran 'ME' (Manager Engineer)
    me_users = get_users_by_role('ME')  # 'ME' adalah role untuk Manager Engineer

    if me_users:
        selected_me = st.selectbox("Pilih Manager Engineer (ME)", me_users)

        # Tombol untuk menugaskan ME ke proyek
        if st.button("Assign ME"):
            try:
                # Menugaskan ME ke proyek
                assign_me_to_project(selected_project_id, selected_me)
                st.success(f"Manager Engineer {selected_me} berhasil ditugaskan ke proyek {selected_project_name}.")
            except Exception as e:
                st.error(f"Gagal menetapkan ME: {e}")
    else:
        st.warning("Tidak ada Manager Engineer (ME) yang tersedia.")