# Import standar Python
import datetime

# Import pustaka pihak ketiga
import pandas as pd
import streamlit as st

# Import modul internal (utils)
from utils.mcs_roi_db import (
    save_mcs_to_database,
    create_mcs_roi_table
)
from utils.project_db import (
    create_projects_table,
    get_projects_by_pm
    
)

create_mcs_roi_table()

def project_pm_page():
    # Pastikan tabel 'projects' ada
    create_projects_table()

    # Halaman untuk Project Manager (PM)
    st.title("Dashboard Project PM")

    # Mendapatkan proyek yang ditugaskan ke PM
    pm_name = st.session_state.get('name', 'Unknown')
    projects = get_projects_by_pm(pm_name)

    if not projects:
        st.warning("Tidak ada proyek yang ditugaskan kepada Anda.")
        return

    # Menampilkan proyek yang tersedia
    project_names = [project[1] for project in projects]
    selected_project_name = st.selectbox("Pilih Proyek", project_names)

    # Mengambil ID proyek yang dipilih
    selected_project = next(project for project in projects if project[1] == selected_project_name)
    selected_project_id = selected_project[0]

    st.subheader(f"MCS untuk Proyek: {selected_project_name}")

    # Inisialisasi session state untuk menyimpan indikator
    if 'indicators' not in st.session_state:
        st.session_state['indicators'] = []

    # Form untuk menambah indikator baru
    with st.form("add_indicator_form"):
        st.write("Tambah Indikator Baru:")
        indikator = st.text_input("Indikator")
        uom = st.text_input("UOM (Unit of Measurement)")
        target = st.number_input("Target", min_value=0.0, format="%.2f")

        add_button = st.form_submit_button("Tambah Indikator")

        if add_button:
            if indikator and uom and target > 0:
                st.session_state['indicators'].append({"indicator": indikator, "uom": uom, "target": target})
                st.success("Indikator berhasil ditambahkan.")
            else:
                st.error("Semua field harus diisi dengan benar.")

    # Tampilkan daftar indikator yang sudah ditambahkan
    if st.session_state['indicators']:
        st.subheader("Daftar Indikator")
        indicators_df = pd.DataFrame(st.session_state['indicators'])
        st.dataframe(indicators_df)

    # Tombol submit untuk mengirim data indikator ke database
    if st.button("Submit MCS"):
        if st.session_state['indicators']:
            try:
                # Simpan data indikator ke tabel mcs_roi
                if save_mcs_to_database(selected_project_id, st.session_state['indicators']):
                    st.success("MCS berhasil disimpan ke database.")
                    st.session_state['indicators'] = []  # Reset indikator setelah submit
                else:
                    st.error("Gagal menyimpan MCS ke database.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menyimpan MCS: {e}")
        else:
            st.error("Tidak ada indikator untuk disubmit.")