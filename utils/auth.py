import mysql.connector
from mysql.connector import Error
from hashlib import sha256

# Fungsi untuk menghubungkan ke database
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Ganti dengan host MySQL Anda
            user="root",       # Ganti dengan user MySQL Anda
            password="",       # Ganti dengan password MySQL Anda
            database="kpix"    # Ganti dengan nama database Anda
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Terjadi kesalahan saat menghubungkan ke database: {e}")
        return None

# Fungsi untuk mendapatkan role pengguna berdasarkan username
def get_user_role(name):
    conn = get_connection()
    if conn is None:
        return None  # Jika tidak ada koneksi, kembalikan None

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT role FROM users WHERE name = %s
        """, (name,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Mengembalikan role pengguna
        else:
            return 'user'  # Default role adalah 'user'
    except Error as e:
        print(f"Terjadi kesalahan saat mengambil role pengguna: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk membuat tabel users (jika belum ada)
def create_users_table():
    conn = get_connection()
    if conn is None:
        return  # Jika koneksi gagal, tidak perlu lanjutkan

    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(255) DEFAULT 'user',
                UNIQUE (name)
            )
        """)
        conn.commit()
        print("Tabel 'users' berhasil dibuat (jika belum ada).")
    except Error as e:
        print(f"Terjadi kesalahan saat membuat tabel: {e}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendaftar pengguna baru
def register_user(name, password, role='user'):
    conn = get_connection()
    if conn is None:
        return  # Jika koneksi gagal, tidak perlu lanjutkan

    cursor = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()  # Hash password menggunakan sha256

    try:
        cursor.execute("""
            INSERT INTO users (name, password, role)
            VALUES (%s, %s, %s)
        """, (name, hashed_password, role))
        conn.commit()
        print(f"Pengguna {name} berhasil didaftarkan dengan role {role}.")
    except Error as e:
        print(f"Terjadi kesalahan saat mendaftar pengguna: {e}")
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk login pengguna
def login_user(name, password):
    conn = get_connection()
    if conn is None:
        return False  # Jika koneksi gagal, return False

    cursor = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()

    try:
        cursor.execute("""
            SELECT * FROM users WHERE name = %s AND password = %s
        """, (name, hashed_password))
        result = cursor.fetchone()
        return True if result else False
    except Error as e:
        print(f"Terjadi kesalahan saat login: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan nama pengguna berdasarkan username
def get_user_name(name):
    conn = get_connection()
    if conn is None:
        return None  # Jika tidak ada koneksi, kembalikan None

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name FROM users WHERE name = %s
        """, (name,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Mengembalikan nama pengguna
        else:
            return None  # Jika pengguna tidak ditemukan
    except Error as e:
        print(f"Terjadi kesalahan saat mengambil nama pengguna: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan daftar pengguna dengan role 'PD'
def get_pd_users():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query untuk mengambil pengguna dengan role 'PD'
        cursor.execute("SELECT name FROM users WHERE role = 'PD'")
        result = cursor.fetchall()
        return [user[0] for user in result]  # Mengembalikan list nama pengguna
    except Error as e:
        print(f"Terjadi kesalahan saat mengambil pengguna PD: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mendapatkan daftar pengguna berdasarkan role (misalnya 'PM' atau 'PD')
def get_users_by_role(role):
    """
    Mengambil daftar pengguna berdasarkan peran tertentu.

    Args:
        role (str): Peran pengguna (contoh: 'ME', 'PM').

    Returns:
        list: Daftar dictionary pengguna dengan format {"id": id, "name": name}.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query untuk mengambil pengguna berdasarkan peran
        query = "SELECT id, name FROM users WHERE role = %s"
        cursor.execute(query, (role,))
        users = cursor.fetchall()

        # Validasi hasil query
        if not users:
            print(f"Tidak ada pengguna ditemukan untuk peran '{role}'.")
            return []

        # Filter hasil query untuk memastikan ID dan nama valid
        valid_users = [{"id": user[0], "name": user[1]} for user in users if user[0] and user[1]]

        if not valid_users:
            print(f"Tidak ada pengguna dengan ID dan nama valid untuk peran '{role}'.")
            return []

        return valid_users
    except mysql.connector.Error as e:
        print(f"Error fetching users by role '{role}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()