# Import standar Python
import datetime

# Import pustaka pihak ketiga
import pandas as pd
import streamlit as st

# Import modul internal (utils)
from utils.project_db import (
    create_projects_table,
    get_connection,
    get_projects_by_role,
    save_project,
    update_project_data,
    assign_pm_to_project,
    
)
from utils.me_conf_db import (
    assign_me_to_project,
    remove_me_from_project,
    get_assigned_mes,
)

from utils.pm_req_db import (
    get_pm_requests,
    approve_pm_request,
    reject_pm_request_with_message
)

from utils.auth import (
    get_user_role,
    get_pd_users,
    get_users_by_role
)


def project_page():
    # Pastikan tabel 'projects' dibuat
    create_projects_table()

    # Pastikan pengguna sudah login dan memiliki role 'DirOps'
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_role = get_user_role(st.session_state['name'])
        if user_role != 'DirOps':
            st.warning("Anda tidak memiliki akses ke halaman Project.")
            return
    else:
        st.warning("Anda harus login terlebih dahulu.")
        return

    st.title("Kelola Project untuk DirOps")

    # Tampilkan notifikasi permintaan PM
    st.subheader("Notifikasi Permintaan PM")
    pm_requests = get_pm_requests()

    if pm_requests:
        for request in pm_requests:
            request_id, project_id, pm_name, pd_name, status, created_at = request

            with st.expander(f"Permintaan untuk Proyek ID: {project_id} oleh PD: {pd_name}"):
                st.write(f"**PM yang Diajukan**: {pm_name}")
                st.write(f"**Tanggal Pengajuan**: {created_at}")
                st.write(f"**Status**: {status}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Terima (ID: {request_id})", key=f"approve_{request_id}"):
                        try:
                            approve_pm_request(request_id)
                            st.success(f"Permintaan untuk proyek {project_id} telah diterima. PM {pm_name} ditetapkan.")
                        except Exception as e:
                            st.error(f"Gagal menerima permintaan: {e}")

                with col2:
                    rejection_message = st.text_input(f"Pesan Penolakan untuk {pd_name}", key=f"rejection_message_{request_id}")
                    if st.button(f"Tolak (ID: {request_id})", key=f"reject_{request_id}"):
                        try:
                            if not rejection_message:
                                st.warning("Silakan masukkan pesan penolakan sebelum menolak.")
                            else:
                                reject_pm_request_with_message(request_id, rejection_message)
                                st.warning(f"Permintaan untuk proyek {project_id} telah ditolak. Pesan dikirim ke {pd_name}.")
                        except Exception as e:
                            st.error(f"Gagal menolak permintaan: {e}")
    else:
        st.write("Tidak ada permintaan PM yang tertunda.")

    # Toggle form visibility untuk menambahkan proyek
    if 'show_form' not in st.session_state:
        st.session_state['show_form'] = False

    if st.button("Tambah Project"):
        st.session_state['show_form'] = not st.session_state['show_form']

    if st.session_state['show_form']:
        project_name = st.text_input("Nama Project")
        pd_users = get_pd_users()
        pd_name = st.selectbox("Nama PD (Project Director)", pd_users)
        anggaran_mandays = st.number_input("Anggaran Mandays", min_value=1)
        start_date = st.date_input("Pilih Tanggal Mulai")
        end_date = st.date_input("Pilih Tanggal Selesai")
        project_type = st.selectbox("Pilih Jenis Proyek", ["Pendampingan", "Semi Pendampingan", "Mentoring", "Prepetuation"])
        nilai_kontrak = st.number_input("Nilai Kontrak (IDR)", min_value=1)
        roi_percent = st.number_input("ROI (%)", min_value=150.0, step=0.1)

        if roi_percent < 100:
            st.error("ROI (%) harus lebih dari atau sama dengan 100.")
            return

        if start_date > end_date:
            st.error("Tanggal mulai tidak boleh setelah tanggal selesai.")
            return

        if st.button("Submit"):
            if project_name and pd_name and project_type:
                try:
                    save_project(project_name, pd_name, anggaran_mandays, start_date, end_date, project_type, nilai_kontrak, roi_percent)
                    st.success(f"Project '{project_name}' berhasil ditambahkan!")
                    st.session_state['show_form'] = False
                except ValueError as ve:
                    st.warning(str(ve))
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
            else:
                st.error("Semua field harus diisi.")

    # Toggle daftar proyek
    if 'show_project_list' not in st.session_state:
        st.session_state['show_project_list'] = False

    if st.button("Tampilkan Daftar Project"):
        st.session_state['show_project_list'] = not st.session_state['show_project_list']

    if st.session_state['show_project_list']:
        st.subheader("Daftar Project yang Tersedia")
        projects = get_projects_by_role(st.session_state['name'], 'DirOps')

        if projects:
            project_data = []
            for project in projects:
                try:
                    project_id = project[0]
                    project_name = project[1]
                    pd_name = project[2] if project[2] else "-"
                    anggaran_mandays = int(project[3]) if project[3] is not None else 0
                    start_date = project[4] if project[4] else "-"
                    end_date = project[5] if project[5] else "-"
                    pm_name = project[6] if project[6] else "Belum ada PM"
                    mandays_og = int(project[7]) if project[7] is not None else 0
                    project_type = project[8] if project[8] else "-"
                    nilai_kontrak = f"{project[9]:,}" if project[9] is not None else "0"
                    roi_percent = project[10] if project[10] is not None else 0
                    roi_idr = f"{project[11]:,}" if project[11] is not None else "0"

                    me_names = get_assigned_mes(project_id)
                    me_names_str = ', '.join(me_names) if me_names else "Belum ada ME"

                    project_data.append([
                        project_id, project_name, pd_name, anggaran_mandays, start_date, end_date,
                        pm_name, mandays_og, project_type, nilai_kontrak, roi_percent, roi_idr, me_names_str
                    ])

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses data proyek: {e}")
                    continue

            project_df = pd.DataFrame(project_data, columns=[
                "ID", "Project Name", "PD", "Anggaran Mandays", "Start Date", "End Date",
                "PM", "Mandays OG", "Project Type", "Nilai Kontrak (IDR)", "ROI (%)", "ROI (IDR)", "ME"
            ])

            st.write("Aktivitas Proyek yang Tersedia:")
            st.dataframe(project_df)


            if 'show_edit_form' not in st.session_state:
                st.session_state['show_edit_form'] = False

            if st.button("Edit Project"):
                st.session_state['show_edit_form'] = not st.session_state['show_edit_form']

            if st.session_state['show_edit_form']:
                selected_project_id = st.selectbox("Pilih Proyek untuk Edit", [project[0] for project in projects], key="edit_project_selectbox")

                selected_project = next((project for project in projects if project[0] == selected_project_id), None)

                if selected_project:
                    project_name_edit = st.text_input("Nama Project", selected_project[1], key="edit_project_name")
                    pd_name_edit = st.selectbox("Nama PD (Project Director)", [selected_project[2]], key="edit_pd_name")
                    anggaran_mandays_edit = st.number_input(
                        "Anggaran Mandays",
                        min_value=1,
                        value=int(selected_project[3]) if isinstance(selected_project[3], (int, float)) else 1,  # Periksa tipe data numerik
                        key="edit_anggaran_mandays"
                    )

                    pm_users = get_users_by_role('PM')
                    me_users = get_users_by_role('ME')

                    selected_pm_index = pm_users.index(selected_project[6]) if selected_project[6] in pm_users else 0
                    selected_pm = st.selectbox("Pilih Project Manager (PM)", pm_users, index=selected_pm_index, key="edit_pm_selectbox")

                    st.subheader("Pilih Manager Engineer (ME) untuk Project")
                    assigned_mes = get_assigned_mes(selected_project[0])
                    selected_me = st.selectbox("Tambah ME", me_users, index=0, key="edit_me_selectbox")
                    add_me_button, remove_me_button = st.columns(2)

                    with add_me_button:
                        if st.button("Tambah ME ke Project"):
                            if selected_me:
                                try:
                                    assign_me_to_project(selected_project[0], selected_me)
                                    st.success(f"ME {selected_me} berhasil ditambahkan ke proyek {selected_project[1]}.")
                                except Exception as e:
                                    st.error(f"Error adding ME: {e}")

                    with remove_me_button:
                        if st.button("Hapus ME dari Project"):
                            if selected_me in assigned_mes:
                                try:
                                    remove_me_from_project(selected_project[0], selected_me)
                                    st.success(f"ME {selected_me} berhasil dihapus dari proyek {selected_project[1]}.")
                                except Exception as e:
                                    st.error(f"Error removing ME: {e}")
                            else:
                                st.error(f"ME {selected_me} tidak terdaftar di proyek ini.")

                    if st.button("Update Project"):
                        if project_name_edit and pd_name_edit:
                            try:
                                update_project_data(
                                    selected_project[0],  # project_id
                                    project_name_edit,    # project_name
                                    pd_name_edit,         # pd_name
                                    anggaran_mandays_edit,# anggaran_mandays
                                    selected_project[4],  # start_date
                                    selected_project[5]   # end_date
                                )
                                assign_pm_to_project(selected_project[0], selected_pm)
                                st.success(f"Project '{project_name_edit}' berhasil diperbarui dengan PM '{selected_pm}'!")
                            except Exception as e:
                                st.error(f"Gagal memperbarui proyek: {e}")
                        else:
                            st.error("Semua field harus diisi.")
                else:
                    st.error("Proyek yang dipilih tidak ditemukan.")
    else:
        st.write("Tidak ada project yang ditemukan.")