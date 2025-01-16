import datetime
import streamlit as st
import mysql.connector
from mysql.connector import Error
import datetime


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
        # Membuat tabel projects dengan id sebagai VARCHAR
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id VARCHAR(20) PRIMARY KEY,                 -- ID Proyek
                name VARCHAR(255) NOT NULL,                 -- Nama Proyek
                pd INT,                                     -- PD (Project Director)
                anggaran_mandays INT NOT NULL,              -- Anggaran Mandays
                start_date DATE,                            -- Tanggal Mulai
                end_date DATE,                              -- Tanggal Selesai
                pm_id INT,                                  -- PM (Project Manager)
                mandays_og INT DEFAULT 0,                   -- Mandays OG
                project_type VARCHAR(255),                 -- Tipe Proyek
                nilai_kontrak BIGINT,                       -- Nilai Kontrak dalam IDR
                roi_percent FLOAT,                          -- ROI (%)
                roi_idr BIGINT,                             -- ROI dalam IDR
                FOREIGN KEY (pd) REFERENCES users(id) ON DELETE SET NULL,  -- Relasi ke PD
                FOREIGN KEY (pm_id) REFERENCES users(id) ON DELETE SET NULL -- Relasi ke PM
            )
        """)

        # Membuat tabel project_me untuk relasi many-to-many antara proyek dan ME (Manager Engineer)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_me (
                project_id VARCHAR(20) NOT NULL,            -- ID proyek
                me_id INT NOT NULL,                         -- ID Manager Engineer (ME)
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (me_id) REFERENCES users(id) ON DELETE CASCADE,
                PRIMARY KEY (project_id, me_id)             -- Kombinasi unik project_id dan me_id
            )
        """)

        conn.commit()
        print("Tables 'projects' and 'project_me' have been created or updated successfully.")
    except mysql.connector.Error as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()

def create_project_me_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_me (
                project_id VARCHAR(10) NOT NULL,
                me_id INT NOT NULL,
                PRIMARY KEY (project_id, me_id),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (me_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("Tabel 'project_me' berhasil dibuat atau sudah ada.")
    except Exception as e:
        print(f"Error creating 'project_me' table: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_project_id(project_type):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Fetch the last project ID for the given project_type
        cursor.execute("""
            SELECT id FROM projects
            WHERE project_type = %s
            ORDER BY id DESC LIMIT 1
        """, (project_type,))

        last_project = cursor.fetchone()

        if last_project:
            # Extract the numeric part and increment it
            last_id_number = int(last_project[0][2:])  # Remove prefix and convert to int
            new_id_number = last_id_number + 1
        else:
            # Start with 1 if no project exists for the given project type
            new_id_number = 1

        # Format the new project ID with the project type prefix
        project_id = f"{project_type[:2].upper()}{str(new_id_number).zfill(2)}"
        return project_id

    except Error as e:
        print(f"Error generating project ID: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Fungsi untuk menyimpan data project baru
def save_project(project_name, pd_name, anggaran_mandays, start_date, end_date, project_type, nilai_kontrak, roi_percent):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if project already exists
        cursor.execute("SELECT id FROM projects WHERE name = %s", (project_name,))
        existing_project = cursor.fetchone()

        if existing_project:
            raise ValueError(f"Proyek dengan nama '{project_name}' sudah ada.")

        # Fetch the PD (Project Director) ID
        cursor.execute("SELECT id FROM users WHERE name = %s", (pd_name,))
        pd_id = cursor.fetchone()

        if pd_id is None:
            raise ValueError("Project Director not found")

        # Determine the prefix based on project type
        if project_type == "Pendampingan":
            prefix = "PD"
        elif project_type == "Semi Pendampingan":
            prefix = "SP"
        elif project_type == "Mentoring":
            prefix = "MT"
        elif project_type == "Prepetuation":
            prefix = "PP"
        else:
            prefix = "XX"  # Default prefix if project type is unknown

        # Get the latest project number for this type (PDXX, SPXX, etc.)
        cursor.execute(f"SELECT MAX(CAST(SUBSTRING(id, 3) AS UNSIGNED)) FROM projects WHERE id LIKE '{prefix}%'")
        max_number = cursor.fetchone()[0]

        if max_number is None:
            new_project_id = f"{prefix}01"  # First project of this type
        else:
            new_project_id = f"{prefix}{max_number + 1:02d}"  # Increment the number

        # Insert the project into the database
        query = """
        INSERT INTO projects (id, name, pd, anggaran_mandays, start_date, end_date, project_type, nilai_kontrak, roi_percent, roi_idr)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        roi_idr = nilai_kontrak * (roi_percent / 100)
        cursor.execute(query, (new_project_id, project_name, pd_id[0], anggaran_mandays, start_date, end_date, project_type, nilai_kontrak, roi_percent, roi_idr))
        conn.commit()
        print(f"Project '{project_name}' has been saved with ID: {new_project_id}")
    except mysql.connector.Error as err:
        print(f"Error saving project: {err}")
    except ValueError as ve:
        print(ve)
        raise ve
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


def calculate_anggaran_mandays(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil start_date dan anggaran_mandays dari proyek
        cursor.execute("""
            SELECT start_date, anggaran_mandays FROM projects WHERE id = %s
        """, (project_id,))
        project_data = cursor.fetchone()

        if not project_data:
            raise ValueError(f"Proyek dengan ID {project_id} tidak ditemukan.")

        start_date, anggaran_mandays = project_data

        # Hitung jumlah bulan berjalan
        current_date = datetime.date.today()
        months_elapsed = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month) + 1

        # Hitung total anggaran mandays
        total_anggaran_mandays = anggaran_mandays * months_elapsed

        # Update anggaran_mandays di database
        cursor.execute("""
            UPDATE projects
            SET anggaran_mandays = %s
            WHERE id = %s
        """, (total_anggaran_mandays, project_id))
        conn.commit()

        print(f"Anggaran Mandays untuk proyek {project_id} telah diperbarui menjadi: {total_anggaran_mandays}")
        return total_anggaran_mandays
    except Error as e:
        print(f"Error menghitung anggaran mandays untuk proyek {project_id}: {e}")
        return None
    except ValueError as ve:
        print(ve)
        return None
    finally:
        cursor.close()
        conn.close()


# Fungsi untuk mendapatkan daftar project yang ditugaskan kepada PD tertentu
def get_projects_by_pd(pd_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.id, p.name, p.start_date, p.end_date, pm.name AS pm_name, 
                   p.mandays_og, p.anggaran_mandays, p.project_type, 
                   p.nilai_kontrak, p.roi_percent, p.roi_idr
            FROM projects p
            LEFT JOIN users pm ON p.pm_id = pm.id
            WHERE p.pd = (SELECT id FROM users WHERE name = %s)
        """, (pd_name,))
        result = cursor.fetchall()

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

# Fungsi untuk mendapatkan daftar project yang ditugaskan kepada PM tertentu
def get_projects_by_pm(pm_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ganti `p.start_month` dengan `p.start_date` atau kolom lain yang sesuai
        cursor.execute("""
            SELECT p.id, p.name, p.pd, p.start_date, p.end_date, pm.name AS pm_name
            FROM projects p
            JOIN users pm ON p.pm_id = pm.id
            WHERE pm.name = %s
        """, (pm_name,))

        return cursor.fetchall()

    except mysql.connector.Error as e:
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
            # DirOps dapat melihat semua proyek
            cursor.execute("""
                SELECT 
                    p.id,                 -- Project ID
                    p.name,               -- Project Name
                    u.name AS pd_name,    -- PD Name
                    p.anggaran_mandays,   -- Anggaran Mandays
                    DATE_FORMAT(p.start_date, '%Y-%m-%d') AS start_date,  -- Formatted Start Date
                    DATE_FORMAT(p.end_date, '%Y-%m-%d') AS end_date,      -- Formatted End Date
                    pm.name AS pm_name,   -- PM Name
                    p.mandays_og,         -- Mandays OG
                    p.project_type,       -- Project Type
                    p.nilai_kontrak,      -- Nilai Kontrak
                    p.roi_percent,        -- ROI Percent
                    p.roi_idr             -- ROI IDR
                FROM projects p
                JOIN users u ON p.pd = u.id
                LEFT JOIN users pm ON p.pm_id = pm.id
            """)
        elif role == "PM":
            cursor.execute("""
                SELECT p.id, p.name 
                FROM projects p
                WHERE p.pm_id IN (
                    SELECT id FROM users WHERE name = %s AND role = 'PM'
                )
            """, (name,))
        elif role == "PD":
            cursor.execute("""
                SELECT p.id, p.name 
                FROM projects p
                WHERE p.pd IN (
                    SELECT id FROM users WHERE name = %s AND role = 'PD'
                )
            """, (name,))
        elif role == "ME":
            cursor.execute("""
                SELECT p.id, p.name 
                FROM projects p
                JOIN project_me pm ON p.id = pm.project_id
                JOIN users u ON pm.me_id = u.id
                WHERE u.name = %s AND u.role = 'ME'
            """, (name,))

        # Return results
        return cursor.fetchall()

    except mysql.connector.Error as e:
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
def update_project_data(project_id, project_name, pd_name, anggaran_mandays, start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s", (pd_name,))
        pd_id = cursor.fetchone()

        if pd_id is None:
            raise ValueError("Project Director not found")

        query = """
        UPDATE projects
        SET name = %s, pd = %s, anggaran_mandays = %s, start_date = %s, end_date = %s
        WHERE id = %s
        """
        cursor.execute(query, (project_name, pd_id[0], anggaran_mandays, start_date, end_date, project_id))
        conn.commit()
        print(f"Project '{project_name}' has been updated.")
    except mysql.connector.Error as err:
        print(f"Error updating project: {err}")
    except ValueError as ve:
        print(ve)
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk memperbarui anggaran mandays proyek berdasarkan tanggal absen
def update_anggaran_mandays_on_absen(project_id, absen_date):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil tanggal mulai proyek
        cursor.execute("""
            SELECT start_date, anggaran_mandays FROM projects WHERE id = %s
        """, (project_id,))
        project_data = cursor.fetchone()

        if not project_data:
            print(f"Proyek dengan ID {project_id} tidak ditemukan.")
            return

        start_date, original_anggaran_mandays = project_data

        if not start_date:
            print(f"Tanggal mulai proyek {project_id} tidak ditemukan.")
            return

        # Hitung selisih bulan antara start_date dan absen_date
        start_month = start_date.year * 12 + start_date.month
        absen_month = absen_date.year * 12 + absen_date.month
        selisih_bulan = absen_month - start_month + 1

        if selisih_bulan > 0:
            # Perbarui anggaran mandays
            updated_anggaran_mandays = original_anggaran_mandays * selisih_bulan

            cursor.execute("""
                UPDATE projects
                SET anggaran_mandays = %s
                WHERE id = %s
            """, (updated_anggaran_mandays, project_id))
            conn.commit()
            print(f"Anggaran Mandays proyek {project_id} telah diperbarui menjadi {updated_anggaran_mandays}.")
        else:
            print(f"Tidak ada perubahan anggaran mandays untuk proyek {project_id}.")
    except Exception as e:
        print(f"Error updating anggaran mandays: {e}")
    finally:
        cursor.close()
        conn.close()