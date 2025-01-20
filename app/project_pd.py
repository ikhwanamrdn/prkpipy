import streamlit as st
import pandas as pd
from config.auth import get_employee_name
from config.project_config import get_projects_by_pd


def project_pd_page():
    """
    Halaman Project (PD) yang hanya dapat diakses oleh Project Director (position_id = 16).
    """
    st.title("Halaman Project (PD)")

    # Validasi apakah pengguna sudah login
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Silakan login terlebih dahulu untuk mengakses halaman ini.")
        return

    # Validasi apakah role pengguna adalah PROJECT DIRECTOR
    if st.session_state.get('role') != 17:  # Role ID untuk PROJECT DIRECTOR adalah 16
        st.error("Anda tidak memiliki akses ke halaman ini.")
        return

    # Ambil employee_id dari sesi login
    employee_id = st.session_state.get('employee_id')

    # Ambil data proyek berdasarkan pd_id
    data = get_projects_by_pd(employee_id)

    # Tampilkan tabel proyek
    st.subheader("Daftar Proyek yang Ditugaskan")

    if data:
        # List untuk menyimpan data proyek
        project_data = []

        # Loop untuk menambahkan data proyek ke dalam list
        for row in data:
            # Ambil nama PD dan PM dari database
            pd_name = get_employee_name(row["pd"]) if row["pd"] else "Tidak Ada"
            pm_name = get_employee_name(row["pm"]) if row["pm"] else "Tidak Ada"

            project_data.append(
                [
                    row["id"],  # Project ID
                    row["lokasi_id"],  # Lokasi ID
                    pd_name,  # Nama Project Director
                    pm_name,  # Nama Project Manager
                    row["start_date"],  # Start Date
                    row["end_date"],  # End Date
                    row["project_type"],  # Project Type
                    row["nilai_kontrak"],  # Contract Value
                    row["roi_percent"],  # ROI (%)
                    row["roi_idr"],  # ROI Value
                    row["anggaran_mandays"],  # Anggaran Mandays
                    row["anggaran_mandays_berjalan"],  # Anggaran Mandays Berjalan
                    row["mandays_berjalan"],  # Mandays Berjalan
                    row["bulan_berjalan"],  # Bulan Berjalan
                    "Aktif" if row["status"] == 1 else "Nonaktif",  # Status
                ]
            )

        # Membuat DataFrame untuk menampilkan proyek
        project_df = pd.DataFrame(
            project_data,
            columns=[
                "Project ID",
                "Lokasi ID",
                "Project Director",
                "Project Manager",
                "Start Date",
                "End Date",
                "Project Type",
                "Contract Value",
                "ROI (%)",
                "ROI Value",
                "Anggaran Mandays",
                "Anggaran Mandays Berjalan",
                "Mandays Berjalan",
                "Bulan Berjalan",
                "Status",
            ],
        )

        # Tampilkan tabel dengan format Streamlit
        st.dataframe(project_df)
    else:
        st.info("Tidak ada proyek yang ditugaskan kepada Anda.")