import streamlit as st
from config.absen_config import save_absen
from config.project_config import get_all_locations, get_projects_by_location
import datetime
from db.connection import get_connection

def absen_page():
    st.title("Halaman Absen Karyawan")

    # Validasi apakah pengguna sudah login
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Silakan login terlebih dahulu untuk mengakses halaman ini.")
        return

    # Ambil employee_id dari sesi login
    employee_id = st.session_state.get('employee_id')

    # Dropdown untuk lokasi training (wajib dipilih)
    locations = get_all_locations()
    location_options = [(loc['id'], loc['name']) for loc in locations]

    if location_options:
        selected_location = st.selectbox(
            "Pilih Lokasi Training (Wajib)",
            location_options,
            format_func=lambda x: x[1]
        )
        selected_location_id = selected_location[0]
    else:
        st.warning("Tidak ada lokasi training yang tersedia.")
        return  # Tidak bisa melanjutkan tanpa lokasi training

    # Dropdown untuk ID training (opsional)
    project_ids = get_projects_by_location(selected_location_id)
    if project_ids:
        selected_project_id = st.selectbox(
            "Pilih Nama Training (Opsional)",
            [None] + [proj['id'] for proj in project_ids],
            format_func=lambda x: x if x else "Belum Memilih Nama Training"
        )
    else:
        st.info("Lokasi ini belum memiliki project terdaftar. Anda tetap dapat melakukan absen.")
        selected_project_id = None  # Tidak ada training yang tersedia

    # Date input untuk memilih tanggal absen
    selected_date = st.date_input("Pilih Tanggal Absen", datetime.date.today())
    selected_date_str = selected_date.strftime("%d-%m-%Y")

    # Check In button
    if st.button("Check In"):
        if employee_id and selected_location_id:  # Lokasi wajib dipilih
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            success, message = save_absen(
                employee_id=employee_id,
                present_id=1,
                location_id=selected_location_id,  # Lokasi tetap dicatat
                training_name=selected_project_id,  # Nama training opsional
                presence_date=selected_date,
                time_in=current_time
            )
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.warning("Silakan pilih lokasi training untuk melakukan Check In.")

    # Check Out button
    if st.button("Check Out"):
        if employee_id and selected_location_id:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            success, message = save_absen(
                employee_id=employee_id,
                present_id=2,
                location_id=selected_location_id,  # Lokasi tetap dicatat
                training_name=selected_project_id,  # Nama training opsional
                presence_date=selected_date,
                time_out=current_time
            )
            if success:
                st.success("Check Out berhasil")  # Hanya tampilkan pesan "Check Out berhasil"
            else:
                st.error(message)
        else:
            st.warning("Silakan pilih lokasi training untuk melakukan Check Out.")