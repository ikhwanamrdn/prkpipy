from binascii import Error
import mysql
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Ganti dengan host MySQL Anda
        user="root",       # Ganti dengan user MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="kpix"    # Ganti dengan nama database Anda
    )

# Function to assign ME to a project
def assign_me_to_project(project_id, me_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'ME'", (me_name,))
        me_id = cursor.fetchone()

        if me_id is None:
            st.warning(f"Manager Engineer '{me_name}' tidak ditemukan atau bukan ME.")
            return

        # Check if ME is already assigned to the project
        cursor.execute("""
            SELECT 1 FROM project_me WHERE project_id = %s AND me_id = %s
        """, (project_id, me_id[0]))
        if cursor.fetchone():
            st.warning(f"ME {me_name} sudah ditugaskan ke proyek ini.")
            return

        # Assign the ME to the project
        cursor.execute("""
            INSERT INTO project_me (project_id, me_id)
            VALUES (%s, %s)
        """, (project_id, me_id[0]))
        conn.commit()
        st.success(f"ME {me_name} berhasil ditugaskan ke proyek ID {project_id}.")
    except Error as e:
        st.error(f"Error saat menambahkan ME ke proyek: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to get the list of MEs assigned to a project
def get_assigned_mes(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.name FROM users u
            JOIN project_me pm ON u.id = pm.me_id
            WHERE pm.project_id = %s
        """, (project_id,))
        assigned_mes = [me[0] for me in cursor.fetchall()]
        return assigned_mes
    except mysql.connector.Error as e:
        st.error(f"Error saat mengambil daftar ME yang ditugaskan: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Function to get the list of available MEs not assigned to a project
def get_unassigned_mes(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.name FROM users u
            WHERE u.role = 'ME' AND u.id NOT IN (
                SELECT me_id FROM project_me WHERE project_id = %s
            )
        """, (project_id,))
        available_mes = [me[0] for me in cursor.fetchall()]
        return available_mes
    except mysql.connector.Error as e:
        st.error(f"Error saat mengambil daftar ME yang tersedia: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Function to remove ME from project
def remove_me_from_project(project_id, me_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'ME'", (me_name,))
        me_id = cursor.fetchone()

        if me_id is None:
            st.warning(f"Manager Engineer '{me_name}' tidak ditemukan atau bukan ME.")
            return

        # Remove ME from the project
        cursor.execute("""
            DELETE FROM project_me WHERE project_id = %s AND me_id = %s
        """, (project_id, me_id[0]))
        conn.commit()
        st.success(f"ME {me_name} berhasil dihapus dari proyek ID {project_id}.")
    except Error as e:
        st.error(f"Error saat menghapus ME dari proyek: {e}")
    finally:
        cursor.close()
        conn.close()