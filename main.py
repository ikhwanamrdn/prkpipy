import streamlit as st
from app.login_register import login_page
from app.absen import absen_page
from app.project import project_page
from app.kelola_project import kelola_project_page
from app.project_pd import project_pd_page  # Import halaman Project (PD)

def main():
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['page'] = "login"
        st.session_state['name'] = None
        st.session_state['role'] = None  # Default None untuk role

    # Jika pengguna belum login, tampilkan halaman login
    if not st.session_state['logged_in']:
        login_page()
    else:
        # Jika sudah login, tampilkan sidebar dan halaman utama
        st.sidebar.markdown(f"""
        <style>
        .sidebar-container {{
            padding: 0;
            margin: 0;
            width: 100%;
            background-color: transparent;
        }}
        .menu-item {{
            text-align: center;
            padding: 20px 0;
            font-size: 18px;
            font-weight: bold;
            color: #ecf0f1;
            text-decoration: none;
            display: block;
            cursor: pointer;
        }}
        .menu-item:hover {{
            color: #3498db;
        }}
        .menu-item.active {{
            color: #3498db;
            border-left: 5px solid #3498db;
            background-color: #34495e;
        }}
        </style>
        """, unsafe_allow_html=True)

        # Custom CSS for sidebar buttons
        st.markdown(
            """
            <style>
            .stButton>button {
                width: 100%;
                text-align: center;
                padding: 10px 0;
                font-size: 16px;
                font-weight: bold;
                color: #ecf0f1;
                background-color: transparent;
                border: none;
                cursor: pointer;
                margin: 2px auto;
                transition: background-color 0.3s, color 0.3s;
            }
            .stButton>button:hover {
                color: #3498db;
                background-color: #34495e;
            }
            .stButton>button:focus {
                outline: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Sidebar menu with Streamlit buttons
        if st.sidebar.button('Absen'):
            st.session_state['page'] = 'absen'
            st.rerun()

        # Hanya DirOps yang dapat melihat menu Project (DirOps)
        if st.session_state['role'] == 14:  # Role 14 untuk DirOps
            if st.sidebar.button('Project (DirOps)'):
                st.session_state['page'] = 'project'
                st.rerun()

        # Hanya Project Director yang dapat melihat menu Project (PD)
        if st.session_state['role'] == 17:  # Role 16 untuk Project Director
            if st.sidebar.button('Project (PD)'):
                st.session_state['page'] = 'project_pd'
                st.rerun()

        # Hanya DirOps yang dapat mengakses Kelola Project
        if st.session_state['role'] == 14:
            if st.sidebar.button('Kelola Project'):
                st.session_state['page'] = 'kelola_project'
                st.rerun()

        # Tombol Logout
        if st.sidebar.button('Logout'):
            st.session_state.clear()
            st.rerun()

        # Navigasi berdasarkan session state
        if st.session_state['page'] == "logout":
            st.session_state.clear()
            st.rerun()
        elif st.session_state['page'] == "absen":
            absen_page()
        elif st.session_state['page'] == "project":
            if st.session_state['role'] == 14:  # Validasi tambahan untuk DirOps
                project_page()
            else:
                st.error("Anda tidak memiliki akses ke halaman ini.")
        elif st.session_state['page'] == "project_pd":
            if st.session_state['role'] == 17:  # Validasi tambahan untuk Project Director
                project_pd_page()
            else:
                st.error("Anda tidak memiliki akses ke halaman ini.")
        elif st.session_state['page'] == "kelola_project":
            if st.session_state['role'] == 14:  # Validasi tambahan untuk DirOps
                kelola_project_page()
            else:
                st.error("Anda tidak memiliki akses ke halaman ini.")

if __name__ == "__main__":
    main()