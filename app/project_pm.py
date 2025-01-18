# Import pustaka Python standar
import pandas as pd
import streamlit as st

# Import modul internal (utils)
from utils.mean_roi_week_conf_db import check_existing_date_range, get_mcs_roi_indicators, get_mean_roi_week_data, save_mean_roi_week

from utils.mcs_req_db import (
    create_mcs_requests_table,
    get_mcs_requests_by_project,
    submit_mcs_request,
    edit_mcs_request,
)
from utils.project_db import create_projects_table, get_projects_by_pm

# Pastikan tabel `mcs_requests` dibuat
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
        target = st.number_input("Target", min_value=0.0, format="%.2f")

        add_button = st.form_submit_button("Tambah Indikator")

        if add_button:
            if indikator and uom and target > 0:
                st.session_state["indicators"].append(
                    {
                        "indicator": indikator,
                        "uom": uom,
                        "target": target,
                    }
                )
                st.success("Indikator berhasil ditambahkan.")
            else:
                st.error("Semua field harus diisi dengan benar.")

    # Tampilkan daftar indikator yang sudah ditambahkan
    if st.session_state["indicators"]:
        st.subheader("Daftar Indikator")
        indicators_df = pd.DataFrame(st.session_state["indicators"])
        st.dataframe(indicators_df)

    # Tombol submit untuk mengajukan data indikator
    if st.button("Ajukan MCS"):
        if st.session_state["indicators"]:
            try:
                # Kirim data indikator ke tabel mcs_requests
                if submit_mcs_request(
                    selected_project_id, st.session_state["indicators"]
                ):
                    st.success("MCS berhasil diajukan.")
                    st.session_state["indicators"] = []  # Reset indikator setelah submit
                else:
                    st.error("Gagal mengajukan MCS.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat mengajukan MCS: {e}")
        else:
            st.error("Tidak ada indikator untuk diajukan.")

    # Bagian untuk menampilkan riwayat pengajuan MCS
    st.subheader("Riwayat Pengajuan MCS")

    # Ambil riwayat pengajuan MCS
    mcs_requests = get_mcs_requests_by_project(selected_project_id)

    if mcs_requests:
        # Siapkan data untuk tabel
        request_data = []
        for mcs in mcs_requests:
            (
                mcs_id,
                indicator,
                uom,
                target,
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
                    target,
                    status,
                    rejection_message if rejection_message else "-",  # Tampilkan "-" jika tidak ada rejection_message
                    created_at,
                    updated_at,
                ]
            )

        # Buat DataFrame untuk menampilkan riwayat
        request_df = pd.DataFrame(
            request_data,
            columns=[
                "Request ID",
                "Indicator",
                "UOM",
                "Target",
                "Status",
                "Rejection Message",
                "Created At",
                "Updated At",
            ],
        )
        st.write("Riwayat Pengajuan MCS Anda:")
        st.dataframe(request_df)

        # Bagian untuk mengedit MCS yang ditolak
        st.subheader("Edit dan Ajukan Ulang MCS yang Ditolak")
        rejected_mcs = [mcs for mcs in mcs_requests if mcs[4] == "Rejected"]

        if rejected_mcs:
            for mcs in rejected_mcs:
                (
                    mcs_id,
                    indicator,
                    uom,
                    target,
                    status,
                    rejection_message,
                    created_at,
                    updated_at,
                ) = mcs

                with st.expander(f"Edit MCS: {indicator} (ID: {mcs_id})"):
                    new_indicator = st.text_input(
                        f"Indikator (ID: {mcs_id})", value=indicator
                    )
                    new_uom = st.text_input(f"UOM (ID: {mcs_id})", value=uom)
                    new_target = st.number_input(
                        f"Target (ID: {mcs_id})", min_value=0.0, value=target, format="%.2f"
                    )

                    if st.button(
                        f"Ajukan Ulang (ID: {mcs_id})", key=f"resubmit_{mcs_id}"
                    ):
                        if new_indicator and new_uom and new_target > 0:
                            try:
                                if edit_mcs_request(
                                    mcs_id, new_indicator, new_uom, new_target
                                ):
                                    st.success(
                                        f"MCS untuk indikator '{new_indicator}' berhasil diajukan ulang."
                                    )
                                else:
                                    st.error(
                                        f"Gagal mengajukan ulang MCS untuk indikator '{new_indicator}'."
                                    )
                            except Exception as e:
                                st.error(
                                    f"Terjadi kesalahan saat mengajukan ulang MCS: {e}"
                                )
                        else:
                            st.error("Semua field harus diisi dengan benar.")
        else:
            st.write("Tidak ada MCS yang ditolak untuk proyek ini.")
    else:
        st.write("Belum ada MCS yang diajukan.")

    # Input MCS ROI Week
    st.subheader("Input Data Mean ROI Week")

    # Ambil indikator berdasarkan proyek yang dipilih
    indicators = get_mcs_roi_indicators(selected_project_id)

    if indicators:
        # Hanya buat form jika ada indikator
        with st.form("input_mean_roi_week_form"):
            indicator_map = {row[1]: row[0] for row in indicators}
            selected_indicator = st.selectbox("Pilih Indikator", list(indicator_map.keys()))
            mcs_roi_id = indicator_map[selected_indicator]

            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            nilai = st.number_input("Nilai (boleh negatif)", format="%.2f")

            # Tambahkan submit button hanya jika ada indikator
            submit_button = st.form_submit_button("Simpan Data")

            if submit_button:
                if end_date < start_date:
                    st.error("End Date tidak boleh lebih awal dari Start Date.")
                else:
                    success, message = save_mean_roi_week(mcs_roi_id, start_date, end_date, nilai)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    else:
        # Tampilkan pesan jika tidak ada indikator, tanpa membuat form
        st.warning("Tidak ada indikator untuk proyek ini.")


    # Tampilkan Data Mean ROI Week
    st.subheader("Data Mean ROI Week")
    data = get_mean_roi_week_data(project_id=selected_project_id)
    if data:
        df = pd.DataFrame(data, columns=[
            "Indicator", "Start Date", "End Date", "Bulan", "Pekan", "Nilai", "Rata-rata", "Created At"
        ])
        st.dataframe(df)
    else:
        st.write("Belum ada data di tabel Mean ROI Week.")