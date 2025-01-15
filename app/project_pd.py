import streamlit as st
import pandas as pd

from utils.auth import get_users_by_role
from utils.me_conf_db import assign_me_to_project, get_assigned_mes
from utils.pm_req_db import create_pm_requests_table, get_pm_requests_by_pd, submit_pm_request
from utils.project_db import get_projects_by_pd

# Pastikan tabel `pm_requests` dibuat
create_pm_requests_table()

def project_pd_page():
    # Pastikan pengguna sudah login dan memiliki role 'PD'
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_role = st.session_state.get('role', '')
        # Hanya PD yang dapat mengakses halaman ini
        if user_role != 'PD':
            st.warning("Anda tidak memiliki akses ke halaman Project.")
            return
    else:
        st.warning("Anda harus login terlebih dahulu.")
        return

    st.title("Kelola Project untuk PD")

    # Ambil nama PD yang sedang login dan proyek yang ditugaskan
    pd_name = st.session_state['name']
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
            mandays_og = project[5]
            anggaran_mandays = project[6]
            project_type = project[7]
            nilai_kontrak = project[8]
            roi_percent = project[9]
            roi_idr = project[10]
            assigned_mes = get_assigned_mes(project_id)
            me_names = ", ".join(assigned_mes) if assigned_mes else "Belum ada ME"

            project_data.append([
                project_id, project_name, start_date, end_date, pm_name, mandays_og,
                anggaran_mandays, project_type, nilai_kontrak, roi_percent, roi_idr, me_names
            ])

        # Membuat DataFrame untuk menampilkan proyek
        project_df = pd.DataFrame(project_data, columns=[
            "Project ID", "Project Name", "Start Date", "End Date", "PM", "Mandays OG",
            "Anggaran Mandays", "Project Type", "Nilai Kontrak (IDR)", "ROI (%)", "ROI (IDR)", "ME"
        ])
        st.write("Project yang ditugaskan kepada Anda:")
        st.dataframe(project_df)

        # Pilih proyek untuk mengelola ME dan PM
        project_names = [project[1] for project in projects]  # Daftar nama proyek
        selected_project_name = st.selectbox("Pilih Proyek", project_names)

        # Ambil detail proyek yang dipilih
        selected_project = next((project for project in projects if project[1] == selected_project_name), None)
        if not selected_project:
            st.error("Proyek yang dipilih tidak ditemukan.")
            return

        selected_project_id = selected_project[0]  # Project ID

        st.write(f"Proyek yang dipilih: **{selected_project_name}**")

        # Bagian untuk mengelola ME
        st.subheader("Kelola Manager Engineer (ME)")

        # Pilih ME untuk ditambahkan
        me_users = get_users_by_role('ME')
        selected_me = st.selectbox("Pilih Manager Engineer (ME) untuk ditambahkan", me_users)

        # Tombol untuk menambahkan ME
        if st.button("Tambah ME"):
            if selected_me:
                try:
                    if selected_me in get_assigned_mes(selected_project_id):
                        st.warning(f"ME {selected_me} sudah ditugaskan ke proyek {selected_project_name}.")
                    else:
                        assign_me_to_project(selected_project_id, selected_me)
                        st.success(f"ME {selected_me} berhasil ditambahkan ke proyek {selected_project_name}.")
                except Exception as e:
                    st.error(f"Gagal menambahkan ME: {e}")
            else:
                st.warning("Anda harus memilih ME terlebih dahulu.")

        # Bagian untuk pengajuan PM
        st.subheader("Ajukan Project Manager (PM)")

        # Pilih PM yang akan diajukan
        pm_users = get_users_by_role('PM')
        selected_pm = st.selectbox("Pilih Project Manager (PM) untuk diajukan", pm_users)

        # Tombol untuk mengajukan PM
        if st.button("Ajukan PM"):
            if selected_pm:
                try:
                    submit_pm_request(selected_project_id, selected_pm, pd_name)
                    st.success(f"Pengajuan PM {selected_pm} untuk proyek {selected_project_name} berhasil diajukan.")
                except Exception as e:
                    st.error(f"Gagal mengajukan PM: {e}")
            else:
                st.warning("Anda harus memilih PM terlebih dahulu.")

        # Bagian untuk menampilkan status permintaan PM
        st.subheader("Status Permintaan Project Manager (PM)")

        # Ambil permintaan PM berdasarkan nama PD yang sedang login
        pm_requests = get_pm_requests_by_pd(pd_name)

        if pm_requests:
            # Siapkan data untuk tabel
            request_data = []
            for request in pm_requests:
                request_id, project_id, pm_name, status, rejection_message, created_at = request
                request_data.append([request_id, project_id, pm_name, status, rejection_message, created_at])

            # Buat DataFrame untuk menampilkan permintaan
            request_df = pd.DataFrame(request_data, columns=[
                "Request ID", "Project ID", "PM Name", "Status", "Rejection Message", "Created At"
            ])
            st.write("Riwayat Permintaan PM Anda:")
            st.dataframe(request_df)
        else:
            st.write("Tidak ada permintaan PM yang diajukan.")
    else:
        st.write("Tidak ada proyek yang ditugaskan kepada Anda saat ini.")