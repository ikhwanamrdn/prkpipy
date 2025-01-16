import streamlit as st
import pandas as pd
from utils.kpi_pd_db import insert_kpi_pd, get_kpi_by_project

def kpi_pd_page():
    """
    Halaman untuk mengelola KPI PD.
    """
    st.title("Dashboard KPI PD")

    # Input ID proyek
    project_id = st.text_input("ID Proyek", value="")

    # Form untuk menambah KPI baru
    with st.form("add_kpi_form"):
        st.write("Tambah KPI Baru:")
        indicator = st.text_input("Indikator")
        uom = st.text_input("UOM (Unit of Measurement)")

        # Input level 1-10
        st.write("Isi nilai untuk setiap level (1-10):")
        levels = {}
        for i in range(1, 11):
            levels[f"level_{i}"] = st.number_input(f"Level {i}", key=f"level_{i}")

        # Input alasan
        alasan = st.text_area("Alasan")

        # Tombol submit
        add_button = st.form_submit_button("Ajukan KPI")

        if add_button:
            if project_id and indicator and uom and alasan:
                if insert_kpi_pd(project_id, indicator, uom, levels, alasan):
                    st.success("KPI berhasil diajukan.")
                else:
                    st.error("Gagal mengajukan KPI.")
            else:
                st.error("Semua field harus diisi dengan lengkap.")

    # Tampilkan KPI terkait proyek
    st.subheader("Daftar KPI Terkait Proyek")
    if project_id:
        kpi_data = get_kpi_by_project(project_id)
        if kpi_data:
            kpi_df = pd.DataFrame(kpi_data, columns=[
                "ID", "Indicator", "UOM",
                "Level 1", "Level 2", "Level 3", "Level 4", "Level 5",
                "Level 6", "Level 7", "Level 8", "Level 9", "Level 10",
                "Progress", "Alasan", "Status", "Rejection Message", "Created At", "Updated At"
            ])
            st.dataframe(kpi_df)
        else:
            st.write("Tidak ada KPI terkait proyek ini.")