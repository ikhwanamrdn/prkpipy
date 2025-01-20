import streamlit as st
from config.auth import register_user, login_user, get_user_name, get_user_role

# Daftar posisi berdasarkan tabel positions
POSITIONS = [
    (1, "STAFF"), (9, "DIREKTUR"), (14, "DIR OPERASIONAL"),
    (16, "PROJECT MANAGER"), (17, "PROJECT DIRECTOR"), (19, "ACCOUNTING/FINANCE/KASIR STAFF"),
    (22, "FAT MANAGER"), (23, "PROJECT SUPPORT"), (26, "TRAINING KORDINATOR"),
    (27, "TRAINING STAFF"), (28, "ENGINEER"), (37, "MC & TRAINER"),
    (38, "IT Magang"), (39, "FAT CONSULTANT"), (42, "MANAGEMENT ENGINEER")
]

def login_page():
    """
    Halaman login dan register pengguna.
    """
    st.title("Selamat Datang di Aplikasi")
    st.subheader("Silakan Login atau Register")

    # Pilihan menu Login atau Register
    menu = st.radio("Pilih Opsi:", ["Login", "Register"])
    
    if menu == "Login":
        login_section()
    elif menu == "Register":
        register_section()

def login_section():
    """
    Bagian untuk login pengguna.
    """
    st.subheader("Login")
    kode_pegawai = st.text_input("Kode Pegawai", key="login_kode_pegawai")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        user = login_user(kode_pegawai, password)
        if user:
            # Jika login berhasil, simpan informasi pengguna ke session_state
            st.session_state['logged_in'] = True
            st.session_state['employee_id'] = user['employees_id']  # Simpan ID pegawai
            st.session_state['role'] = user['position_id']  # Simpan role pegawai
            st.session_state['name'] = user['employees_name']  # Simpan nama pegawai
            st.session_state['page'] = "dashboard"  # Arahkan ke dashboard
            st.success(f"Login berhasil! Selamat datang {st.session_state['name']}.")
        else:
            st.error("Kode Pegawai atau password salah!")

def register_section():
    """
    Bagian untuk registrasi pengguna baru.
    """
    st.subheader("Register")
    kode_pegawai = st.text_input("Kode Pegawai", key="register_kode_pegawai")
    email = st.text_input("Email", key="register_email")
    nomor_hp = st.text_input("Nomor Telepon", key="register_nomor_hp")
    password = st.text_input("Password", type="password", key="register_password")
    nama_lengkap = st.text_input("Nama Lengkap", key="register_nama_lengkap")
    
    # Dropdown untuk memilih posisi
    position = st.selectbox("Pilih Posisi", POSITIONS, format_func=lambda x: x[1], key="register_position")
    position_id = position[0]  # Ambil ID dari posisi yang dipilih
    
    if st.button("Register"):
        try:
            # Registrasi pengguna baru
            result = register_user(
                kode_pegawai, email, nomor_hp, password, nama_lengkap, position_id
            )
            if result:
                st.success("Berhasil mendaftar! Silakan login.")
            else:
                st.error("Gagal mendaftar. Kode pegawai atau email mungkin sudah terdaftar.")
        except Exception as e:
            st.error(f"Gagal mendaftar: {e}")