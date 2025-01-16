import mysql.connector

# Fungsi untuk menghubungkan ke database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port= 3308,
        user="root",
        password="",  # Sesuaikan password MySQL Anda
        database="kpix"
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
                UNIQUE (name, date)  -- Hanya bisa absen sekali per hari
            )
        """)
        conn.commit()
        print("Tabel 'absen' berhasil dibuat (jika belum ada).")
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan saat membuat tabel absen: {err}")
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

# Fungsi untuk memeriksa apakah sudah ada absen untuk tanggal tersebut
def is_absen_exists(name, selected_date):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT * FROM absen WHERE name = %s AND date = %s
        """
        cursor.execute(query, (name, selected_date))
        result = cursor.fetchone()
        
        return result is not None  # Jika sudah ada absen, kembalikan True
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan saat memeriksa absen: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menyimpan data check-in
def save_check_in(name, selected_date):
    if is_absen_exists(name, selected_date):
        print(f"Anda sudah absen pada tanggal {selected_date}. Tidak bisa check-in lagi.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Menyimpan data check-in
    current_time = '10:00:00'  # Contoh waktu check-in, ganti sesuai dengan implementasi
    last_session_id = get_last_session_id(name, selected_date)
    session_id = last_session_id + 1 if last_session_id else 1  # Tentukan session_id berikutnya

    query = """
        INSERT INTO absen (name, session_id, check_in, date)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (name, session_id, current_time, selected_date))
    conn.commit()

    cursor.close()
    conn.close()

# Fungsi untuk menyimpan data check-out
def save_check_out(name, selected_date):
    if not is_absen_exists(name, selected_date):
        print(f"Belum ada check-in pada tanggal {selected_date}. Tidak bisa check-out.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Menyimpan data check-out
    current_time = '12:00:00'  # Contoh waktu check-out, ganti sesuai dengan implementasi
    query = """
        UPDATE absen
        SET check_out = %s
        WHERE name = %s AND date = %s
    """
    cursor.execute(query, (current_time, name, selected_date))
    conn.commit()

    cursor.close()
    conn.close()