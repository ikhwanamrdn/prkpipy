import streamlit as st
import pandas as pd

from utils.auth import get_users_by_role
from utils.me_conf_db import assign_me_to_project, get_assigned_mes
from utils.pm_req_db import (
    create_pm_requests_table,
    get_pm_requests_by_pd,
    submit_pm_request,
)
from utils.project_db import get_projects_by_pd
from utils.mcs_req_db import (
    create_mcs_requests_table,
    get_mcs_requests_by_project,
    reject_mcs_request_with_message,
    save_to_mcs_roi,
    get_approved_mcs_by_project,
)

# Pastikan tabel `pm_requests` dan `mcs_requests` dibuat
create_pm_requests_table()
create_mcs_requests_table()


def project_pd_page():
    # Pastikan pengguna sudah login dan memiliki role 'PD'
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        user_role = st.session_state.get("role", "")
        # Hanya PD yang dapat mengakses halaman ini
        if user_role != "PD":
            st.warning("Anda tidak memiliki akses ke halaman Project.")
            return
    else:
        st.warning("Anda harus login terlebih dahulu.")
        return

    st.title("Kelola Project untuk PD")

    # Ambil nama PD yang sedang login dan proyek yang ditugaskan
    pd_name = st.session_state["name"]
    projects = get_projects_by_pd(pd_name)  # Ambil proyek yang ditugaskan kepada PD ini

    if projects:
        # Menyiapkan data proyek untuk ditampilkan dalam tabel
        project_data = []
        for project in projects:
            if len(project) < 11:  # Pastikan tuple memiliki elemen yang cukup
                st.error(f"Data proyek tidak lengkap: {project}")
                continue

            project_id = project[0]
            project_name = project[1]
            start_date = project[2]
            end_date = project[3]
            pm_name = project[4] if project[4] else "Belum ada PM"
            assigned_mes = get_assigned_mes(project_id)
            me_names = ", ".join(assigned_mes) if assigned_mes else "Belum ada ME"

            project_data.append(
                [
                    project_id,
                    project_name,
                    start_date,
                    end_date,
                    pm_name,
                    me_names,
                ]
            )

        # Membuat DataFrame untuk menampilkan proyek
        project_df = pd.DataFrame(
            project_data,
            columns=[
                "Project ID",
                "Project Name",
                "Start Date",
                "End Date",
                "PM",
                "ME",
            ],
        )
        st.write("Project yang ditugaskan kepada Anda:")
        st.dataframe(project_df)

        # Pilih proyek untuk mengelola MCS
        project_names = [project[1] for project in projects]  # Daftar nama proyek
        selected_project_name = st.selectbox("Pilih Proyek", project_names)

        # Ambil detail proyek yang dipilih
        selected_project = next(
            (project for project in projects if project[1] == selected_project_name), None
        )
        if not selected_project:
            st.error("Proyek yang dipilih tidak ditemukan.")
            return

        selected_project_id = selected_project[0]  # Project ID

        st.write(f"Proyek yang dipilih: **{selected_project_name}**")

        # Bagian untuk menerima dan menolak MCS
        st.subheader("Permintaan MCS")

        # Ambil permintaan MCS berdasarkan proyek yang dipilih
        mcs_requests = get_mcs_requests_by_project(selected_project_id)

        # Simpan status pengolahan permintaan di session_state
        if "processed_requests" not in st.session_state:
            st.session_state["processed_requests"] = {}

        if mcs_requests:
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

                if st.session_state["processed_requests"].get(mcs_id):
                    continue  # Jangan tampilkan jika sudah diproses

                with st.expander(f"Indikator: {indicator} (Status: {status})"):
                    st.write(f"**UOM**: {uom}")
                    st.write(f"**Target**: {target}")
                    st.write(f"**Tanggal Permintaan**: {created_at}")
                    st.write(
                        f"**Tanggal Pembaruan Terakhir**: {updated_at if updated_at else 'Belum ada'}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(f"Terima (ID: {mcs_id})", key=f"approve_mcs_{mcs_id}"):
                            try:
                                if save_to_mcs_roi(selected_project_id, indicator, uom, target):
                                    st.session_state["processed_requests"][mcs_id] = True
                                    st.success(
                                        f"Permintaan MCS untuk indikator '{indicator}' berhasil diterima dan disimpan ke ROI."
                                    )
                                else:
                                    st.error(
                                        f"Gagal menyimpan MCS untuk indikator '{indicator}' ke ROI."
                                    )
                            except Exception as e:
                                st.error(f"Gagal menerima permintaan MCS: {e}")
                    with col2:
                        rejection_message = st.text_input(
                            f"Pesan Penolakan (ID: {mcs_id})", key=f"rejection_message_{mcs_id}"
                        )
                        if st.button(f"Tolak (ID: {mcs_id})", key=f"reject_mcs_{mcs_id}"):
                            try:
                                if not rejection_message:
                                    st.warning(
                                        "Silakan masukkan pesan penolakan sebelum menolak."
                                    )
                                else:
                                    reject_mcs_request_with_message(
                                        mcs_id, rejection_message
                                    )
                                    st.session_state["processed_requests"][mcs_id] = True
                                    st.warning(
                                        f"Permintaan MCS untuk indikator '{indicator}' telah ditolak."
                                    )
                            except Exception as e:
                                st.error(f"Gagal menolak permintaan MCS: {e}")
        else:
            st.write("Tidak ada permintaan MCS yang diajukan untuk proyek ini.")

        # Bagian untuk menampilkan riwayat MCS yang disetujui
        st.subheader("Riwayat MCS Approval")

        approved_mcs = get_approved_mcs_by_project(selected_project_id)

        if approved_mcs:
            approved_data = []
            for mcs in approved_mcs:
                (
                    mcs_id,
                    indicator,
                    uom,
                    target,
                    created_at,
                    updated_at,
                ) = mcs

                approved_data.append(
                    [
                        mcs_id,
                        indicator,
                        uom,
                        target,
                        created_at,
                        updated_at,
                    ]
                )

            approved_df = pd.DataFrame(
                approved_data,
                columns=[
                    "MCS ID",
                    "Indicator",
                    "UOM",
                    "Target",
                    "Created At",
                    "Updated At",
                ],
            )
            st.write("Riwayat MCS yang telah disetujui:")
            st.dataframe(approved_df)
        else:
            st.write("Belum ada MCS yang disetujui untuk proyek ini.")

        # Bagian untuk menambahkan ME ke proyek
        st.subheader("Tambah ME ke Proyek")

        # Ambil semua ME yang tersedia dari sistem
        all_mes = get_users_by_role("ME")  # Pastikan hanya mengembalikan daftar nama

        if not all_mes:
            st.warning("Tidak ada ME yang tersedia untuk ditambahkan.")
        else:
            # Pilihan dropdown hanya menampilkan nama ME
            selected_me_name = st.selectbox("Pilih ME", [me['name'] for me in all_mes])

            # Tombol untuk menambahkan ME ke proyek
            if st.button("Tambahkan ME"):
                try:
                    # Assign ME ke proyek
                    assign_me_to_project(selected_project_id, selected_me_name)
                except ValueError as ve:
                    st.warning(str(ve))  # Tangani kesalahan validasi
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menambahkan ME: {e}")

        # Bagian untuk mengelola PM
        st.subheader("Ajukan PM ke DirOps")

        # Ambil semua pengguna dengan role 'PM'
        all_pms = get_users_by_role("PM")
        if not all_pms:
            st.warning("Tidak ada PM tersedia.")
        else:
            # Ambil hanya nama PM
            available_pm_names = [pm["name"] for pm in all_pms]
            selected_pm_name = st.selectbox("Pilih PM untuk diajukan", available_pm_names)

            if st.button("Ajukan PM"):
                try:
                    # Kirim permintaan PM ke DirOps
                    submit_pm_request(selected_project_id, selected_pm_name, pd_name)
                    st.success(f"PM '{selected_pm_name}' berhasil diajukan ke DirOps.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat mengajukan PM: {e}")

        # Tambahkan bagian untuk menampilkan status request PM
        st.subheader("Status Request PM ke DirOps")

        # Ambil semua request PM yang diajukan oleh PD ini
        pm_requests = get_pm_requests_by_pd(pd_name)

        if pm_requests:
            # Format data untuk ditampilkan dalam tabel
            pm_request_data = []
            for request in pm_requests:
                request_id, project_id, pm_name, status, rejection_message, created_at = request
                pm_request_data.append(
                    [
                        request_id,
                        project_id,
                        pm_name,
                        status,
                        rejection_message if rejection_message else "-",  # "-" jika tidak ada pesan
                        created_at,
                    ]
                )

            # Tampilkan tabel status request PM
            pm_request_df = pd.DataFrame(
                pm_request_data,
                columns=[
                    "Request ID",
                    "Project ID",
                    "PM Name",
                    "Status",
                    "Rejection Message",
                    "Created At",
                ],
            )
            st.write("Status request PM yang diajukan:")
            st.dataframe(pm_request_df)
        else:
            st.write("Belum ada request PM yang diajukan.")