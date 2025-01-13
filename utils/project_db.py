import datetime
import streamlit as st
import mysql.connector
from mysql.connector import Error

# Fungsi untuk menghubungkan ke database
def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Ganti dengan host MySQL Anda
        user="root",       # Ganti dengan user MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="kpix"    # Ganti dengan nama database Anda
    )

# Fungsi untuk membuat tabel projects (jika belum ada) dan menambahkan kolom mandays_og dan me_id
def create_projects_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Menambahkan kolom mandays_og dan me_id untuk menghubungkan pegawai biasa (ME) ke proyek
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                pd INT,
                anggaran_mandays INT NOT NULL,
                start_month INT,
                pm_id INT,
                mandays_og INT DEFAULT 0,  -- Kolom mandays_og untuk menghitung mandays berjalan
                FOREIGN KEY (pd) REFERENCES users(id),
                FOREIGN KEY (pm_id) REFERENCES users(id)
            )
        """)
        # Creating the 'project_me' table to handle the many-to-many relationship between projects and MEs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_me (
                project_id INT,
                me_id INT,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (me_id) REFERENCES users(id),
                PRIMARY KEY (project_id, me_id)  -- Ensure project_id and me_id are unique pairs
            )
        """)

        conn.commit()
        print("Table 'projects' and 'project_me' have been created or updated.")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menyimpan data project baru
def save_project(project_name, pd_name, anggaran_mandays, start_month):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Periksa apakah proyek dengan nama yang sama sudah ada
        cursor.execute("SELECT id FROM projects WHERE name = %s", (project_name,))
        existing_project = cursor.fetchone()

        if existing_project:
            raise ValueError(f"Proyek dengan nama '{project_name}' sudah ada.")

        # Jika proyek tidak ada, lanjutkan untuk menyimpan proyek baru
        cursor.execute("SELECT id FROM users WHERE name = %s", (pd_name,))
        pd_id = cursor.fetchone()

        if pd_id is None:
            raise ValueError("Project Director not found")

        query = """
        INSERT INTO projects (name, pd, anggaran_mandays, start_month, mandays_og)
        VALUES (%s, %s, %s, %s, 0)  -- mandays_og diinisialisasi ke 0
        """
        cursor.execute(query, (project_name, pd_id[0], anggaran_mandays, start_month))
        conn.commit()
        print(f"Project '{project_name}' has been saved.")
    except mysql.connector.Error as err:
        print(f"Error saving project: {err}")
    except ValueError as ve:
        print(ve)  # Ini akan ditangkap oleh project_page untuk menampilkan peringatan
        raise ve  # Re-raise error untuk ditangani di project_page
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menghitung mandays_og berdasarkan absensi pegawai dan PM
def calculate_mandays_og(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Menghitung jumlah mandays berdasarkan absensi pegawai yang berhubungan dengan proyek
        cursor.execute("""
            SELECT COUNT(DISTINCT name) FROM absen
            WHERE project_id = %s
        """, (project_id,))
        mandays_count = cursor.fetchone()[0]

        # Update kolom mandays_og di tabel projects
        cursor.execute("""
            UPDATE projects
            SET mandays_og = %s
            WHERE id = %s
        """, (mandays_count, project_id))
        conn.commit()
        print(f"Mandays berjalan (mandays_og) untuk proyek {project_id} telah dihitung dan diperbarui.")
    except Error as e:
        print(f"Error calculating mandays_og for project {project_id}: {e}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan daftar project yang ditugaskan kepada PD tertentu
# Fungsi untuk mendapatkan daftar project yang ditugaskan kepada PD tertentu
def get_projects_by_pd(pd_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.id, p.name, u.name AS pd_name, p.start_month, pm.name AS pm_name, p.mandays_og, p.anggaran_mandays
            FROM projects p
            JOIN users u ON p.pd = u.id
            LEFT JOIN users pm ON p.pm_id = pm.id
            WHERE u.role = 'PD' AND u.name = %s
        """, (pd_name,))
        result = cursor.fetchall()

        # Debugging: Periksa apakah proyek ditemukan
        if result:
            print(f"Proyek ditemukan untuk PD '{pd_name}':", result)
        else:
            print(f"Tidak ada proyek yang ditemukan untuk PD '{pd_name}'")
        
        return result if result else []  # Kembalikan list kosong jika tidak ada proyek yang ditemukan
        
    except Error as e:
        print(f"Error fetching projects for PD '{pd_name}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan daftar pengguna berdasarkan role (misalnya 'PM' atau 'PD')
def get_users_by_role(role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM users WHERE role = %s", (role,))
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching users by role '{role}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan daftar project yang ditugaskan kepada PM tertentu
def get_projects_by_pm(pm_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.id, p.name, u.name AS pd_name, p.start_month, pm.name AS pm_name, p.mandays_og, p.anggaran_mandays
            FROM projects p
            JOIN users u ON p.pd = u.id
            LEFT JOIN users pm ON p.pm_id = pm.id
            WHERE pm.name = %s
        """, (pm_name,))
        result = cursor.fetchall()

        print(f"Projects found for PM {pm_name}: {result}")  # Debugging: log the result

        return result if result else []  # Kembalikan list kosong jika tidak ada proyek yang ditemukan

    except Error as e:
        print(f"Error fetching projects for PM '{pm_name}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan daftar project berdasarkan peran (DirOps, PM, PD, ME)
def get_projects_by_role(name, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if role == "DirOps":
            # DirOps can access all projects, including all columns (id, name, pd_name, etc.)
            cursor.execute("""
                SELECT p.id, p.name, u.name AS pd_name, p.start_month, pm.name AS pm_name, p.mandays_og, p.anggaran_mandays
                FROM projects p
                JOIN users u ON p.pd = u.id
                LEFT JOIN users pm ON p.pm_id = pm.id
            """)
        elif role == "PM":
            cursor.execute("""
                SELECT p.id, p.name FROM projects p
                WHERE p.pm_id IN (SELECT id FROM users WHERE name = %s AND role = 'PM')
            """, (name,))
        elif role == "PD":
            cursor.execute("""
                SELECT p.id, p.name FROM projects p
                WHERE p.pd IN (SELECT id FROM users WHERE name = %s AND role = 'PD')
            """, (name,))
        elif role == "ME":
            cursor.execute("""
                SELECT p.id, p.name FROM projects p
                JOIN project_me pm ON p.id = pm.project_id
                JOIN users u ON pm.me_id = u.id
                WHERE u.name = %s AND u.role = 'ME'
            """, (name,))

        return cursor.fetchall()

    except Error as e:
        print(f"Error fetching projects for role '{role}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan daftar pegawai biasa (non-PM dan non-PD)
def get_regular_employees():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM users WHERE role NOT IN ('PM', 'PD')")
        return [row[0] for row in cursor.fetchall()]  # Mengembalikan daftar nama pengguna
    except Error as e:
        print(f"Error fetching regular employees: {e}")
        return []  # Jika terjadi kesalahan, kembalikan list kosong
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menetapkan PM ke proyek tertentu
def assign_pm_to_project(project_id, pm_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'PM'", (pm_name,))
        pm_id = cursor.fetchone()

        if pm_id is None:
            raise ValueError("PM not found or user is not a PM")

        cursor.execute("SELECT pm_id FROM projects WHERE id = %s", (project_id,))
        existing_pm = cursor.fetchone()
        if existing_pm and existing_pm[0] is not None:
            raise ValueError("This project already has a PM assigned")

        query = """
        UPDATE projects
        SET pm_id = %s
        WHERE id = %s
        """
        cursor.execute(query, (pm_id[0], project_id))
        conn.commit()
        print(f"PM {pm_name} has been assigned to project ID {project_id}")
    except Error as e:
        print(f"Error assigning PM to project: {e}")
    except ValueError as ve:
        print(ve)
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk memeriksa apakah mandays telah tercapai
def check_mandays_limit(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT mandays_og, anggaran_mandays FROM projects WHERE id = %s
        """, (project_id,))
        mandays_data = cursor.fetchone()

        if mandays_data:
            mandays_og, anggaran_mandays = mandays_data
            if mandays_og >= anggaran_mandays:
                return True  # Mandays telah tercapai
            else:
                return False  # Mandays belum tercapai
    except Error as e:
        print(f"Error checking mandays limit for project {project_id}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk memperbarui data proyek
def update_project_data(project_id, project_name, pd_name, anggaran_mandays, start_month):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s", (pd_name,))
        pd_id = cursor.fetchone()

        if pd_id is None:
            raise ValueError("Project Director not found")

        query = """
        UPDATE projects
        SET name = %s, pd = %s, anggaran_mandays = %s, start_month = %s
        WHERE id = %s
        """
        cursor.execute(query, (project_name, pd_id[0], anggaran_mandays, start_month, project_id))
        conn.commit()
        print(f"Project '{project_name}' has been updated.")
    except mysql.connector.Error as err:
        print(f"Error updating project: {err}")
    except ValueError as ve:
        print(ve)
    finally:
        cursor.close()
        conn.close()

# Function to remove ME from project
# Function to remove ME from project
def remove_me_from_project(project_id, me_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'ME'", (me_name,))
        me_id = cursor.fetchone()

        if me_id is None:
            raise ValueError(f"Manager Engineer '{me_name}' not found or user is not a Manager Engineer")

        # Remove ME from the project
        cursor.execute("""
            DELETE FROM project_me WHERE project_id = %s AND me_id = %s
        """, (project_id, me_id[0]))
        conn.commit()

        print(f"ME {me_name} has been removed from project ID {project_id}")
    except Error as e:
        print(f"Error removing ME from project: {e}")
    except ValueError as ve:
        print(ve)
    finally:
        cursor.close()
        conn.close()

# Function to assign ME to a project
def assign_me_to_project(project_id, me_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'ME'", (me_name,))
        me_id = cursor.fetchone()

        if me_id is None:
            raise ValueError(f"Manager Engineer '{me_name}' not found or user is not a Manager Engineer")

        # Check if ME is already assigned to the project
        cursor.execute("""
            SELECT 1 FROM project_me WHERE project_id = %s AND me_id = %s
        """, (project_id, me_id[0]))
        if cursor.fetchone():
            raise ValueError(f"ME {me_name} is already assigned to this project.")

        # Insert into the project_me table to assign the ME to the project
        cursor.execute("""
            INSERT INTO project_me (project_id, me_id)
            VALUES (%s, %s)
        """, (project_id, me_id[0]))
        conn.commit()

        print(f"ME {me_name} has been assigned to project ID {project_id}")
    except Error as e:
        print(f"Error assigning ME to project: {e}")
    except ValueError as ve:
        print(ve)
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
        st.error(f"Error fetching assigned MEs: {e}")
        return []
    finally:
        cursor.close()
        conn.close()