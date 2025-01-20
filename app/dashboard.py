import streamlit as st

def dashboard_page():
    """
    Halaman dashboard untuk pengguna yang sudah login.
    """
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.title(f"Selamat Datang, {st.session_state['name']}")
        st.write(f"ID Pegawai Anda: {st.session_state['employee_id']}")
        st.write(f"Role Anda: {st.session_state['role']}")
    else:
        st.warning("Silakan login terlebih dahulu.")