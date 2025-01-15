# Import standar Python
import datetime

# Import pustaka pihak ketiga
import pandas as pd
import streamlit as st

# Import modul internal (utils)
from utils.mcs_req_db import (
    create_mcs_requests_table,
    get_approved_mcs_by_project,
    get_mcs_requests_by_project,
    submit_mcs_request,
)
from utils.project_db import (
    create_projects_table,
    get_projects_by_pm,
)

# Pastikan tabel mcs_requests dibuat
create_mcs_requests_table()


def project_pm_page():
    # Pastikan tabel 'projects' ada
    create_projects_table()

    # Halaman untuk Project Manager (PM)
    st.title("Dashboard Project PM")

    # Mendapatkan proyek yang ditugaskan ke PM
    pm_name = st.session_state.get("name", "Unknown")
    projects = get_projects_by_pm(pm_name)

    if not projects:
        st.warning("Tidak ada proyek yang ditugaskan kepada Anda.")
        return

    # Menampilkan proyek yang tersedia
    project_names = [project[1] for project in projects]
    selected_project_name = st.selectbox("Pilih Proyek", project_names)

    # Mengambil ID proyek yang dipilih
    selected_project = next(
        project for project in projects if project[1] == selected_project_name
    )
    selected_project_id = selected_project[0]

    st.subheader(f"MCS untuk Proyek: {selected_project_name}")

    # Inisialisasi session state untuk menyimpan indikator
    if "indicators" not in st.session_state:
        st.session_state["indicators"] = []

    # Form untuk menambah indikator baru
    with st.form("add_indicator_form"):
        st.write("Tambah Indikator Baru:")
        indikator = st.text_input("Indikator")
        uom = st.text_input("UOM (Unit of Measurement)")

        # Input untuk level (1-10)
        st.write("Isi nilai untuk setiap level (1-10):")
        levels = {}
        for i in range(1, 11):
            levels[f"level_{i}"] = st.number_input(f"Level {i}", key=f"level_{i}")

        add_button = st.form_submit_button("Tambah Indikator")

        if add_button:
            if indikator and uom and all(value is not None for value in levels.values()):
                st.session_state["indicators"].append(
                    {"indicator": indikator, "uom": uom, "levels": levels}
                )
                st.success("Indikator berhasil ditambahkan.")
            else:
                st.error("Semua field harus diisi dengan benar.")

    # Tampilkan daftar indikator yang sudah ditambahkan
    if st.session_state["indicators"]:
        st.subheader("Daftar Indikator")
        indicators_df = pd.DataFrame(
            [
                {
                    "Indicator": ind["indicator"],
                    "UOM": ind["uom"],
                    **ind["levels"],
                }
                for ind in st.session_state["indicators"]
            ]
        )
        st.dataframe(indicators_df)

    # Tombol submit untuk mengajukan data indikator ke PD
    if st.button("Ajukan MCS ke PD"):
        if st.session_state["indicators"]:
            try:
                # Kirim data indikator ke tabel mcs_requests untuk diajukan ke PD
                if submit_mcs_request(
                    selected_project_id, st.session_state["indicators"]
                ):
                    st.success("MCS berhasil diajukan ke PD.")
                    st.session_state["indicators"] = []  # Reset indikator setelah submit
                else:
                    st.error("Gagal mengajukan MCS ke PD.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat mengajukan MCS: {e}")
        else:
            st.error("Tidak ada indikator untuk diajukan.")

    # Bagian untuk menampilkan status pengajuan MCS
    st.subheader("Status Permintaan MCS")

    # Ambil permintaan MCS berdasarkan proyek yang dipilih
    mcs_requests = get_mcs_requests_by_project(selected_project_id)

    if mcs_requests:
        # Siapkan data untuk tabel
        request_data = []
        for mcs in mcs_requests:
            (
                mcs_id,
                indicator,
                uom,
                level_1,
                level_2,
                level_3,
                level_4,
                level_5,
                level_6,
                level_7,
                level_8,
                level_9,
                level_10,
                status,
                rejection_message,
                created_at,
                updated_at,
            ) = mcs

            request_data.append(
                [
                    mcs_id,
                    indicator,
                    uom,
                    level_1,
                    level_2,
                    level_3,
                    level_4,
                    level_5,
                    level_6,
                    level_7,
                    level_8,
                    level_9,
                    level_10,
                    status,
                    rejection_message,
                    created_at,
                    updated_at,
                ]
            )

        # Buat DataFrame untuk menampilkan permintaan
        request_df = pd.DataFrame(
            request_data,
            columns=[
                "Request ID",
                "Indicator",
                "UOM",
                "Level 1",
                "Level 2",
                "Level 3",
                "Level 4",
                "Level 5",
                "Level 6",
                "Level 7",
                "Level 8",
                "Level 9",
                "Level 10",
                "Status",
                "Rejection Message",
                "Created At",
                "Updated At",
            ],
        )
        st.write("Riwayat Permintaan MCS Anda:")
        st.dataframe(request_df)
    else:
        st.write("Tidak ada permintaan MCS yang diajukan untuk proyek ini.")

    # Bagian untuk menampilkan MCS yang sudah disetujui
    st.subheader("MCS yang Sudah Disetujui")

    # Ambil data MCS yang sudah diapprove
    approved_mcs = get_approved_mcs_by_project(selected_project_id)

    if approved_mcs:
        # Siapkan data untuk tabel
        approved_data = []
        for mcs in approved_mcs:
            (
                project_id,
                indicator,
                uom,
                level_1,
                level_2,
                level_3,
                level_4,
                level_5,
                level_6,
                level_7,
                level_8,
                level_9,
                level_10,
                progress,
                created_at,
            ) = mcs

            approved_data.append(
                [
                    project_id,
                    indicator,
                    uom,
                    level_1,
                    level_2,
                    level_3,
                    level_4,
                    level_5,
                    level_6,
                    level_7,
                    level_8,
                    level_9,
                    level_10,
                    progress,
                    created_at,
                ]
            )

        # Buat DataFrame untuk menampilkan data
        approved_df = pd.DataFrame(
            approved_data,
            columns=[
                "Project ID",
                "Indicator",
                "UOM",
                "Level 1",
                "Level 2",
                "Level 3",
                "Level 4",
                "Level 5",
                "Level 6",
                "Level 7",
                "Level 8",
                "Level 9",
                "Level 10",
                "Progress",
                "Created At",
            ],
        )
        st.write("MCS yang sudah di-approve:")
        st.dataframe(approved_df)
    else:
        st.write("Tidak ada MCS yang disetujui untuk proyek ini.")