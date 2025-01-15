import mysql.connector
import datetime

# Fungsi untuk menghubungkan ke database
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
                project_id VARCHAR(10) NOT NULL,
                session_id INT NOT NULL,
                check_in TIME,
                check_out TIME,
                date DATE NOT NULL,
                UNIQUE (name, date, project_id)  -- Hanya bisa absen sekali per proyek per hari
            )
        """)
        conn.commit()
        print("Tabel 'absen' berhasil dibuat (jika belum ada).")
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan saat membuat tabel absen: {err}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan session_id terakhir berdasarkan nama, tanggal, dan proyek
def get_last_session_id(name, selected_date, project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT session_id FROM absen 
            WHERE name = %s AND date = %s AND project_id = %s
            ORDER BY session_id DESC LIMIT 1
        """
        cursor.execute(query, (name, selected_date, project_id))
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

# Fungsi untuk memeriksa apakah sudah ada absen untuk nama, tanggal, dan proyek tertentu
def is_absen_exists(name, date, project_id):
    from utils.project_db import calculate_mandays_og  # Lazy import
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT 1 FROM absen WHERE name = %s AND date = %s AND project_id = %s
        """
        cursor.execute(query, (name, date, project_id))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking absen existence: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menyimpan data check-in
def save_check_in(name, selected_date, project_id):
    if is_absen_exists(name, selected_date, project_id):
        print(f"Anda sudah absen pada tanggal {selected_date}. Tidak bisa check-in lagi.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Menyimpan data check-in
        current_time = datetime.datetime.now().time()  # Menggunakan waktu saat ini
        query = """
            INSERT INTO absen (name, session_id, check_in, date, project_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, 1, current_time, selected_date, project_id))  # Misalnya session_id default = 1
        conn.commit()

        print(f"Check In berhasil untuk {name} pada tanggal {selected_date}.")
    except Exception as e:
        print(f"Error saving check-in: {e}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menyimpan data check-out
def save_check_out(name, selected_date, project_id):
    if not is_absen_exists(name, selected_date, project_id):
        print(f"Belum ada check-in pada tanggal {selected_date}. Tidak bisa check-out.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Menyimpan data check-out
        current_time = datetime.datetime.now().time()  # Menggunakan waktu saat ini
        query = """
            UPDATE absen
            SET check_out = %s
            WHERE name = %s AND date = %s AND project_id = %s
        """
        cursor.execute(query, (current_time, name, selected_date, project_id))
        conn.commit()

        print(f"Check Out berhasil untuk {name} pada tanggal {selected_date}.")
    except Exception as e:
        print(f"Error saving check-out: {e}")
    finally:
        cursor.close()
        conn.close()