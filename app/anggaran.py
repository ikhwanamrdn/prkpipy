import streamlit as st
import os
from datetime import datetime
from utils.anggaran_db import create_reimbust_table, save_reimbursement, get_project_reimbursements, get_project_details, get_reimbust_data
from utils.auth import get_user_role

def reimbust_page():
    # Ensure the reimbust table exists
    create_reimbust_table()

    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Anda harus login terlebih dahulu.")
        return

    user_role = get_user_role(st.session_state['name'])
    st.title("Manajemen Reimbust")

    if user_role == 'DirOps':
        st.subheader("Reimbursement Semua Project")
        projects = get_project_details()
        if projects:
            for project in projects:
                project_id, project_name = project[0], project[1]
                reimbursements = get_project_reimbursements(project_id)

                if reimbursements:
                    with st.expander(f"{project_name}"):
                        # Render reimbursement table
                        table_rows = "".join(
                            f"""
                            <tr>
                                <td>{r[0]}</td>
                                <td>{r[1]}</td>
                                <td>{r[2]}</td>
                                <td>{r[3]}</td>
                                <td>{'<br>'.join([f'<a href="http://localhost:8502/File_reimbust/{file.strip()}" target="_blank">Buka File</a>' for file in r[6].split(',') if file.strip()])}</td>
                            </tr>
                            """ for r in reimbursements
                        )
                        st.markdown(
                            f"""
                            <table border="1" style="border-collapse: collapse; width: 100%;">
                                <thead>
                                    <tr>
                                        <th>Amount</th>
                                        <th>Date</th>
                                        <th>Jenis</th>
                                        <th>Rincian</th>
                                        <th>File</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {table_rows}
                                </tbody>
                            </table>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("Belum ada data reimbursement untuk project ini.")
        else:
            st.info("Tidak ada project yang tersedia.")

    elif user_role == 'PD':
        st.subheader("Reimbursement Project Anda")
        projects = get_project_details()
        if projects:
            for project in projects:
                project_id, project_name = project[0], project[1]
                reimbursements = get_project_reimbursements(project_id)

                if reimbursements:
                    with st.expander(f"{project_name}"):
                        table_rows = "".join(
                            f"""
                            <tr>
                                <td>{r[0]}</td>
                                <td>{r[1]}</td>
                                <td>{r[2]}</td>
                                <td>{r[3]}</td>
                                <td>{'<br>'.join([f'<a href="http://localhost:8502/File_reimbust/1{file.strip()}" target="_blank">Buka File</a>' for file in r[6].split(',') if file.strip()])}</td>
                            </tr>
                            """ for r in reimbursements
                        )
                        st.markdown(
                            f"""
                            <table border="1" style="border-collapse: collapse; width: 100%;">
                                <thead>
                                    <tr>
                                        <th>Amount</th>
                                        <th>Date</th>
                                        <th>Jenis</th>
                                        <th>Rincian</th>
                                        <th>File</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {table_rows}
                                </tbody>
                            </table>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("Belum ada data reimbursement untuk project ini.")
        else:
            st.info("Anda belum memiliki project.")

    st.subheader("Ajukan Reimbursement")
    with st.form("reimbursement_form"):
        st.write("Silakan isi form berikut untuk mengajukan reimbursement:")
        project_id = st.selectbox("Pilih Project", [(project[0], project[1]) for project in get_project_details()], format_func=lambda x: x[1])
        amount = st.number_input("Jumlah Reimbursement", min_value=0.01, format="%.2f")
        jenis = st.text_input("Jenis Reimbust")
        rincian = st.text_area("Rincian Kegiatan")

        uploaded_files = st.file_uploader(
            "Unggah Bukti Reimbursement (PDF/Gambar) (Maksimal 5 MB per file)", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True
        )

        submit_button = st.form_submit_button("Ajukan Reimbursement")
        if submit_button:
            saved_files = []
            folder = "File_reimbust"
            if not os.path.exists(folder):
                os.makedirs(folder)
            for uploaded_file in uploaded_files:
                filepath = os.path.join(folder, uploaded_file.name)
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(uploaded_file.name)
            save_reimbursement(project_id[0], amount, jenis, rincian, None, None, ",".join(saved_files))
            st.success("Reimbursement berhasil diajukan!")
