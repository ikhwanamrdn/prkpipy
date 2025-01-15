import streamlit as st
import pandas as pd
from utils.absen_db import create_absen_table, save_check_in, save_check_out, is_absen_exists
from utils.project_db import get_projects_by_role  # Fungsi untuk mengambil proyek berdasarkan role
import datetime  # Impor modul datetime

def absen_page():
    # Pastikan tabel absen dibuat sebelum melanjutkan
    create_absen_table()

    # Halaman absen
    st.title("Halaman Absen Karyawan")

    # Periksa peran pengguna
    user_role = st.session_state.get('role', 'Unknown')
    if user_role not in ['DirOps', 'PM', 'PD', 'ME']:
        st.warning("Anda tidak memiliki akses untuk melakukan absen.")
        return

    # Pilih tanggal absen tanpa default ke tanggal saat ini
    selected_date = st.date_input("Pilih Tanggal Absen")
    selected_date_str = selected_date.strftime('%Y-%m-%d') if selected_date else None  # Pastikan format tanggal sesuai SQL
    name = st.session_state.get('name', 'Unknown User')

    if not selected_date:
        st.warning("Silakan pilih tanggal untuk melanjutkan.")
        return

    # Mendapatkan daftar proyek yang ditugaskan kepada pengguna sesuai dengan peran
    projects = get_projects_by_role(name, user_role)  # Fungsi untuk mengambil proyek berdasarkan role

    # Jika tidak ada proyek yang ditugaskan
    if not projects:
        st.warning(f"Tidak ada proyek yang ditugaskan kepada Anda pada tanggal {selected_date_str}.")
        return

    # Menampilkan dropdown proyek dengan nama proyek yang tersedia
    project_names = [project[1] for project in projects]  # Ambil nama proyek dari hasil query
    project_ids = [project[0] for project in projects]  # Ambil ID proyek yang terkait

    selected_project_name = st.selectbox("Pilih Proyek Anda", project_names)
    selected_project_id = project_ids[project_names.index(selected_project_name)]  # Ambil project_id berdasarkan nama yang dipilih

    # Memeriksa jika proyek yang dipilih sesuai dengan yang telah ditugaskan
    if selected_project_id not in [project[0] for project in projects]:
        st.error(f"Anda tidak ditugaskan ke proyek {selected_project_name} pada tanggal {selected_date_str}. Tidak bisa melakukan absen di proyek ini.")
        return

    # Menampilkan tombol Check-In dan Check-Out
    if st.button("Check In"):
        if is_absen_exists(name, selected_date_str, selected_project_id):
            st.warning(f"Anda sudah check-in pada tanggal {selected_date_str} untuk proyek {selected_project_name}. Tidak bisa check-in lagi.")
        else:
            save_check_in(name, selected_date_str, selected_project_id)
            st.success(f"Check In berhasil pada {selected_date_str} untuk proyek {selected_project_name}")

    if st.button("Check Out"):
        if not is_absen_exists(name, selected_date_str, selected_project_id):
            st.warning(f"Belum ada check-in pada tanggal {selected_date_str} untuk proyek {selected_project_name}. Tidak bisa check-out.")
        else:
            save_check_out(name, selected_date_str, selected_project_id)
            st.success(f"Check Out berhasil pada {selected_date_str} untuk proyek {selected_project_name}")

