import mysql.connector
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Ganti dengan host MySQL Anda
        user="root",       # Ganti dengan user MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="kpix"    # Ganti dengan nama database Anda
    )

# Fungsi untuk membuat tabel absen (jika belum ada)
def create_absen_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query untuk membuat tabel absen jika belum ada
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS absen (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                session_id INT NOT NULL,
                check_in TIME,
                check_out TIME,
                date DATE NOT NULL,
                project_id INT,  -- Menambahkan project_id untuk mengaitkan absensi dengan proyek
                UNIQUE (name, date, project_id)  -- Hanya bisa absen sekali per hari untuk setiap proyek
            )
        """)
        conn.commit()
        print("Tabel 'absen' berhasil dibuat (jika belum ada).")
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan saat membuat tabel absen: {err}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk memeriksa apakah absen sudah ada
def is_absen_exists(name, selected_date, project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT * FROM absen WHERE name = %s AND date = %s AND project_id = %s
        """
        cursor.execute(query, (name, selected_date, project_id))
        result = cursor.fetchone()

        return result is not None  # Jika sudah ada absen, kembalikan True
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan saat memeriksa absen: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menyimpan data check-in
# Fungsi untuk menyimpan data check-in
def save_check_in(name, selected_date, project_id):
    if is_absen_exists(name, selected_date, project_id):
        print(f"Anda sudah absen pada tanggal {selected_date}. Tidak bisa check-in lagi.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Cek apakah mandays_og sudah melebihi anggaran_mandays
    cursor.execute("""
        SELECT mandays_og, anggaran_mandays FROM projects WHERE id = %s
    """, (project_id,))
    mandays_data = cursor.fetchone()

    if mandays_data:
        mandays_og, anggaran_mandays = mandays_data
        if mandays_og >= anggaran_mandays:
            # Jika mandays_og sudah melebihi anggaran_mandays, tampilkan peringatan
            st.warning(f"Perhatian! Mandays untuk proyek ini telah melebihi batas anggaran ({anggaran_mandays}) dengan jumlah mandays yang terpakai saat ini ({mandays_og}).")

    # Menyimpan data check-in
    current_time = '10:00:00'  # Contoh waktu check-in, ganti sesuai dengan implementasi
    last_session_id = get_last_session_id(name, selected_date)
    session_id = last_session_id + 1 if last_session_id else 1  # Tentukan session_id berikutnya

    query = """
        INSERT INTO absen (name, session_id, check_in, date, project_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, session_id, current_time, selected_date, project_id))
    conn.commit()

    cursor.close()
    conn.close()

# Fungsi untuk menyimpan data check-out dan memperbarui mandays_og
def save_check_out(name, selected_date, project_id):
    if not is_absen_exists(name, selected_date, project_id):
        print(f"Belum ada check-in pada tanggal {selected_date}. Tidak bisa check-out.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Menyimpan data check-out
        current_time = '12:00:00'  # Contoh waktu check-out, ganti sesuai dengan implementasi
        query = """
            UPDATE absen
            SET check_out = %s
            WHERE name = %s AND date = %s AND project_id = %s
        """
        cursor.execute(query, (current_time, name, selected_date, project_id))
        conn.commit()

        # Update mandays_og di tabel projects
        query_update_mandays = """
            UPDATE projects
            SET mandays_og = mandays_og + 1
            WHERE id = %s
        """
        cursor.execute(query_update_mandays, (project_id,))
        conn.commit()

        # Cek apakah mandays_og sudah melebihi anggaran_mandays
        cursor.execute("""
            SELECT mandays_og, anggaran_mandays FROM projects WHERE id = %s
        """, (project_id,))
        mandays_data = cursor.fetchone()

        if mandays_data:
            mandays_og, anggaran_mandays = mandays_data
            if mandays_og > anggaran_mandays:
                st.warning(f"Perhatian! Mandays untuk proyek ini telah melebihi batas anggaran ({anggaran_mandays}) dengan jumlah mandays yang terpakai saat ini ({mandays_og}).")

        print(f"Check-out berhasil dan mandays_og untuk proyek {project_id} bertambah 1.")
    except mysql.connector.Error as e:
        print(f"Error saat melakukan check-out: {e}")
        conn.rollback()  # Rollback jika ada error
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan session_id terakhir berdasarkan nama dan tanggal
def get_last_session_id(name, selected_date):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT session_id FROM absen 
            WHERE name = %s AND date = %s 
            ORDER BY session_id DESC LIMIT 1
        """
        cursor.execute(query, (name, selected_date))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return None  # Jika tidak ada session sebelumnya
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan saat mengambil session_id terakhir: {err}")
        return None
    finally:
        cursor.close()
        conn.close()