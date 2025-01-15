from binascii import Error
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Ganti dengan host MySQL Anda
        user="root",       # Ganti dengan user MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="kpix"    # Ganti dengan nama database Anda
    )

def create_mcs_roi_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Periksa apakah tabel 'projects' sudah dibuat
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'projects'
        """)
        projects_exists = cursor.fetchone()[0]

        if not projects_exists:
            raise ValueError("Tabel 'projects' belum dibuat. Pastikan tabel 'projects' sudah ada.")

        # Buat tabel 'mcs_roi' jika belum ada
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcs_roi (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id VARCHAR(20) NOT NULL,
                indicator VARCHAR(255) NOT NULL,
                uom VARCHAR(50) NOT NULL,
                target FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("Tabel 'mcs_roi' berhasil dibuat.")
    except mysql.connector.Error as err:
        print(f"Error creating 'mcs_roi' table: {err}")
    finally:
        cursor.close()
        conn.close()

def save_mcs_to_database(project_id, indicators):
    """
    Menyimpan indikator ke tabel `mcs_roi`.

    :param project_id: ID proyek
    :param indicators: List indikator (dictionary dengan kunci 'indicator', 'uom', dan 'target')
    :return: True jika berhasil, False jika gagal
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO mcs_roi (project_id, indicator, uom, target)
            VALUES (%s, %s, %s, %s)
        """
        for indicator in indicators:
            cursor.execute(query, (project_id, indicator['indicator'], indicator['uom'], indicator['target']))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error saat menyimpan data ke `mcs_roi`: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_mcs_by_project(project_id):
    """
    Mendapatkan daftar MCS berdasarkan ID proyek.

    :param project_id: ID proyek
    :return: List indikator dari tabel `mcs_roi`
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT id, indicator, uom, target, created_at
            FROM mcs_roi
            WHERE project_id = %s
        """
        cursor.execute(query, (project_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error saat mengambil data dari `mcs_roi`: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_mcs_by_id(mcs_id):
    """
    Menghapus MCS berdasarkan ID.

    :param mcs_id: ID MCS yang akan dihapus
    :return: True jika berhasil, False jika gagal
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM mcs_roi WHERE id = %s"
        cursor.execute(query, (mcs_id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error saat menghapus data dari `mcs_roi`: {e}")
        return False
    finally:
        cursor.close()
        conn.close()