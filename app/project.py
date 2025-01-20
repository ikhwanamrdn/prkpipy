import streamlit as st
import pandas as pd
from config.project_config import get_all_locations, is_project_name_exists, save_project, get_kelola_project

def project_page():
    """
    Halaman untuk menampilkan dan mengelola proyek dari tabel lokasi_project.
    """
    st.title("Manajemen Proyek")
    st.subheader("Tambah Proyek Baru")

    # Form untuk menambah proyek baru
    with st.form("add_project_form"):
        project_name = st.text_input("Nama Proyek", placeholder="Masukkan nama proyek...")

        submitted = st.form_submit_button("Tambahkan Proyek")
        if submitted:
            if project_name.strip():  # Validasi input tidak kosong
                if is_project_name_exists(project_name):  # Periksa jika nama proyek sudah ada
                    st.warning("Nama proyek sudah ada. Silakan gunakan nama yang berbeda.")
                else:
                    if save_project(project_name):  # Simpan proyek ke database
                        st.success(f"Proyek '{project_name}' berhasil ditambahkan!")
                        
                        # Tandai bahwa proyek berhasil ditambahkan dan ubah query params
                        st.session_state["project_added"] = True  # Tandai status
                        st.query_params.update({"refresh": "true"})  # Perbarui query params
                    else:
                        st.error("Gagal menambahkan proyek. Silakan coba lagi.")
            else:
                st.warning("Nama proyek tidak boleh kosong.")

    # Cek apakah proyek baru berhasil ditambahkan
    if st.session_state.get("project_added"):
        st.session_state["project_added"] = False  # Reset status setelah refresh

    # Display the lokasi_project table
    st.title("Tabel Lokasi Project")

    # Fetch data from the lokasi_project table
    data = get_all_locations()  # Fungsi untuk mengambil data dari tabel lokasi_project

    # Check if data is available
    if data:
        # Customize column names for display
        df = pd.DataFrame(data)
        df.columns = ["Project ID", "Project Name"]  # Sesuaikan nama kolom untuk tampilan
        st.dataframe(df)
    else:
        st.write("No data available in the lokasi_project table.")