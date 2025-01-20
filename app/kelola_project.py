import streamlit as st
from config.project_config import (
    save_kelola_project, get_all_locations, get_all_roles, 
    get_last_project_id
)

def kelola_project_page():
    """
    Halaman untuk mengelola project berdasarkan tabel kelola_project.
    """
    st.title("Kelola Project")

    # Form untuk input data project
    with st.form("kelola_project_form"):
        # Dropdown untuk nama proyek (lokasi_project)
        project_locations = get_all_locations()  # Mengambil data dari tabel lokasi_project
        location_options = [(loc['id'], loc['name']) for loc in project_locations]
        location = st.selectbox("Nama Project", location_options, format_func=lambda x: x[1])
        selected_location_id = location[0]  # ID lokasi yang dipilih

        # Dropdown untuk jenis project
        project_type = st.selectbox("Jenis Project", ["Pendampingan", "Semi-Pendampingan", "Mentoring", "Prepetuation"])

        # Dropdown untuk PD (Project Director)
        pd_roles = get_all_roles(role_id=17)  # Ambil role dengan role_id = 17 (PROJECT DIRECTOR)
        pd_options = [(pd['id'], pd['name']) for pd in pd_roles]
        pd = st.selectbox("Pilih Project Director (PD)", pd_options, format_func=lambda x: x[1])

        # Dropdown untuk PM (Project Manager), opsional
        pm_roles = get_all_roles(role_id=16)  # Ambil role dengan role_id = 16 (PROJECT MANAGER)
        pm_options = [(pm['id'], pm['name']) for pm in pm_roles]
        pm = st.selectbox("Pilih Project Manager (PM) (Opsional)", [None] + pm_options, format_func=lambda x: x[1] if x else "Tidak Dipilih")

        # Input untuk anggaran mandays
        anggaran_mandays = st.number_input("Anggaran Mandays", min_value=0, step=1)

        # Input untuk tanggal mulai dan selesai
        start_date = st.date_input("Tanggal Mulai")
        end_date = st.date_input("Tanggal Selesai")

        # Input untuk nilai kontrak dan ROI percent
        nilai_kontrak = st.number_input("Nilai Kontrak (IDR)", min_value=0, step=1)
        roi_percent = st.number_input("ROI Percent (%)", min_value=150.0, step=0.01)  # Minimal 150.0

        # Hitungan otomatis untuk ROI IDR
        roi_idr = nilai_kontrak * (roi_percent / 100)
        st.write(f"ROI (IDR): {roi_idr}")

        # Tombol submit
        submitted = st.form_submit_button("Simpan Project")
        if submitted:
            # Validasi ROI percent
            if roi_percent < 150.0:
                st.error("ROI Percent harus minimal 150%.")
            else:
                # Auto-generate ID project
                last_id = get_last_project_id(project_type[:2].upper())
                auto_id = f"{project_type[:2].upper()}{last_id:02d}"  # Contoh: PD01, SP02, dll.

                # Simpan data ke database
                success = save_kelola_project(
                    project_id=auto_id,
                    pd_id=pd[0],
                    pm_id=pm[0] if pm else None,
                    anggaran_mandays=anggaran_mandays,
                    start_date=start_date,
                    end_date=end_date,
                    project_type=project_type,
                    nilai_kontrak=nilai_kontrak,
                    roi_percent=roi_percent,
                    roi_idr=roi_idr,
                    lokasi_id=selected_location_id  # Gunakan lokasi_id
                )

                if success:
                    st.success(f"Project berhasil disimpan dengan ID {auto_id}.")
                else:
                    st.error("Gagal menyimpan project. Silakan coba lagi.")