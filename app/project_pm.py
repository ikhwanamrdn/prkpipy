# Import pustaka Python standar
import pandas as pd
import streamlit as st

# Import modul internal (utils)
from utils.mcs_roi_db import get_mcs_roi_by_status, achieve_mcs
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

    # Bagian untuk menampilkan MCS yang sudah diapprove
    st.subheader("MCS yang Sudah Diapprove")

    # Ambil data MCS yang statusnya "On Going"
    ongoing_mcs = get_mcs_roi_by_status(selected_project_id, "On Going")

    if ongoing_mcs:
        # Tampilkan data On Going
        ongoing_data = []
        for mcs in ongoing_mcs:
            (
                mcs_id,
                indicator,
                uom,
                target,
                status,
                created_at,
                updated_at,
            ) = mcs

            ongoing_data.append(
                [
                    mcs_id,
                    indicator,
                    uom,
                    target,
                    status,
                    created_at,
                    updated_at,
                ]
            )

        ongoing_df = pd.DataFrame(
            ongoing_data,
            columns=[
                "MCS ID",
                "Indicator",
                "UOM",
                "Target",
                "Status",
                "Created At",
                "Updated At",
            ],
        )
        st.write("MCS dengan Status 'On Going':")
        st.dataframe(ongoing_df)

        # Tambahkan tombol Achieve untuk setiap indikator On Going
        for mcs in ongoing_mcs:
            (
                mcs_id,
                indicator,
                uom,
                target,
                status,
                created_at,
                updated_at,
            ) = mcs

            if status == "On Going":
                if st.button(f"Achieve (ID: {mcs_id})", key=f"achieve_{mcs_id}"):
                    try:
                        if achieve_mcs(mcs_id):
                            st.success(
                                f"MCS untuk indikator '{indicator}' berhasil diubah menjadi 'Achieved'."
                            )
                        else:
                            st.error(
                                f"Gagal mengubah status MCS untuk indikator '{indicator}'."
                            )
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat mengubah status MCS: {e}")
    else:
        st.write("Tidak ada MCS dengan status 'On Going'.")