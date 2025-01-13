import streamlit as st
from utils.auth import register_user, login_user, get_user_name, get_user_role

def login_page():
    st.title("Selamat Datang di Aplikasi")
    st.subheader("Silakan Login atau Register")

    menu = st.radio("Pilih Opsi:", ["Login", "Register"])
    
    if menu == "Login":
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                # Jika login berhasil, simpan informasi pengguna
                st.session_state['logged_in'] = True
                st.session_state['role'] = get_user_role(username)  # Get role of the user
                st.session_state['name'] = get_user_name(username)  # Get name of the user
                st.session_state['page'] = "dashboard"  # Arahkan ke dashboard
                st.success(f"Login berhasil! Selamat datang {st.session_state['name']}.")
            else:
                st.error("Username atau password salah!")
    
    elif menu == "Register":
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")
        
        # Added "ME" role to the registration options
        role = st.selectbox("Role", ["pegawai", "PD", "PM", "DirOps", "ME"], key="register_role")
        
        if st.button("Register"):
            try:
                register_user(username, password, role)
                st.success("Berhasil mendaftar! Silakan login.")
            except Exception as e:
                st.error("Gagal mendaftar: " + str(e))