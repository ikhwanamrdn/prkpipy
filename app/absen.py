import streamlit as st
from utils.absen_db import create_absen_table, save_check_in, save_check_out, is_absen_exists
import datetime  # Impor modul datetime

def absen_page():
    # Pastikan tabel absen dibuat sebelum melanjutkan
    create_absen_table()

    # Halaman absen
    st.title("Halaman Absen")
    st.write("Gunakan fitur ini untuk mencatat waktu kehadiran Anda.")
    
    # Gunakan datetime.date untuk tanggal
    selected_date = st.date_input("Pilih Tanggal Absen", value=datetime.date(2025, 1, 1))  # Gunakan datetime.date untuk tanggal
    name = st.session_state.get('name', 'Unknown User')

    # Button untuk check-in
    if st.button("Check In"):
        if is_absen_exists(name, selected_date):
            st.warning(f"Anda sudah absen pada tanggal {selected_date}. Tidak bisa check-in lagi.")
        else:
            save_check_in(name, selected_date)
            st.success(f"Check In berhasil pada {selected_date}")
    
    # Button untuk check-out
    if st.button("Check Out"):
        if not is_absen_exists(name, selected_date):
            st.warning(f"Belum ada check-in pada tanggal {selected_date}. Tidak bisa check-out.")
        else:
            save_check_out(name, selected_date)
            st.success(f"Check Out berhasil pada {selected_date}")