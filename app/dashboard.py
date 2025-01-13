import streamlit as st

def dashboard_page():
    st.title("Dashboard")
    st.write(f"Selamat datang, {st.session_state['name']}!")

    # Menambahkan tombol logout
    if st.button("Logout"):
        # Menghapus session login
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.session_state['name'] = None
        st.session_state['page'] = "login"  # Arahkan kembali ke halaman login
        st.success("Anda telah logout.")
        
        # Clear session state
        st.session_state.clear()  # Clear the session state
        # Optionally set page to "login"
        st.session_state['page'] = "login"  # Set the page to "login"