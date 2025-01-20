from db.connection import get_connection
import mysql.connector

def register_user(kode_pegawai, email, nomor_hp, password, nama_lengkap, position_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Periksa apakah kode pegawai atau email sudah terdaftar
        cursor.execute("SELECT * FROM employees WHERE employees_code = %s OR employees_email = %s", (kode_pegawai, email))
        if cursor.fetchone():
            return False

        # Masukkan data ke tabel employees
        cursor.execute('''
            INSERT INTO employees (employees_code, employees_email, employees_hp, employees_password, employees_name, position_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (kode_pegawai, email, nomor_hp, password, nama_lengkap, position_id))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(kode_pegawai, password):
    """
    Fungsi untuk memverifikasi login berdasarkan kode pegawai dan password.
    Mengembalikan data lengkap pengguna jika berhasil, atau None jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verifikasi login dan ambil ID pengguna
        cursor.execute(
            """
            SELECT id AS employees_id, employees_name, position_id 
            FROM employees 
            WHERE employees_code = %s AND employees_password = %s
            """,
            (kode_pegawai, password)
        )
        return cursor.fetchone()  # Mengembalikan dictionary dengan data pengguna
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_name(employee_id):
    """
    Mengambil nama pengguna berdasarkan ID pegawai.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT employees_name FROM employees WHERE id = %s", (employee_id,))
        result = cursor.fetchone()
        return result['employees_name'] if result else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_role(employee_id):
    """
    Mengambil role pengguna berdasarkan ID pegawai.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT position_id FROM employees WHERE id = %s", (employee_id,))
        result = cursor.fetchone()
        return result['position_id'] if result else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

from db.connection import get_connection

def get_employee_name(employee_id):
    """
    Mengambil nama karyawan berdasarkan ID.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT employees_name FROM employees WHERE id = %s"
        cursor.execute(query, (employee_id,))
        result = cursor.fetchone()
        return result["employees_name"] if result else "Tidak Ada"
    except Exception as e:
        print(f"[ERROR] Gagal mengambil nama karyawan: {e}")
        return "Tidak Ada"
    finally:
        cursor.close()
        conn.close()