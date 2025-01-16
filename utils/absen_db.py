import mysql.connector
import datetime

from utils.project_db import calculate_mandays_og

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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS absen (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                project_id VARCHAR(10) NOT NULL,
                session_id INT NOT NULL,
                check_in TIME,
                check_out TIME,
                date DATE NOT NULL,
                UNIQUE (name, date, project_id)  -- Mencegah duplikasi absen untuk proyek tertentu dalam satu hari
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
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan saat mengambil session_id terakhir: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk memeriksa apakah sudah ada absen untuk nama, tanggal, dan proyek tertentu
def is_absen_exists(name, date, project_id):
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
        current_time = datetime.datetime.now().time()
        # Jika session_id sudah ada, tambahkan 1, jika tidak, mulai dari 1
        last_session_id = get_last_session_id(name, selected_date, project_id)
        new_session_id = last_session_id + 1 if last_session_id else 1

        query = """
            INSERT INTO absen (name, session_id, check_in, date, project_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, new_session_id, current_time, selected_date, project_id))
        conn.commit()

        print(f"Check In berhasil untuk {name} pada tanggal {selected_date} dengan session ID {new_session_id}.")
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
        current_time = datetime.datetime.now().time()
        query = """
            UPDATE absen
            SET check_out = %s
            WHERE name = %s AND date = %s AND project_id = %s AND check_out IS NULL
        """
        cursor.execute(query, (current_time, name, selected_date, project_id))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Check Out berhasil untuk {name} pada tanggal {selected_date}.")
            # Hitung ulang mandays_og untuk proyek ini
            mandays_og = calculate_mandays_og(project_id)
            print(f"Mandays OG setelah Check Out: {mandays_og}")
        else:
            print(f"Check Out gagal: Anda mungkin sudah check-out sebelumnya.")
    except Exception as e:
        print(f"Error saving check-out: {e}")
    finally:
        cursor.close()
        conn.close()