import mysql.connector
from db.connection import get_connection

def create_mcs_requests_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Membuat tabel `mcs_requests` dengan kolom `updated_at`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcs_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id VARCHAR(20) NOT NULL,
                indicator VARCHAR(255) NOT NULL,
                uom VARCHAR(50) NOT NULL,
                target FLOAT NOT NULL,
                status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
                rejection_message TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("Tabel 'mcs_requests' berhasil dibuat atau sudah ada.")
    except mysql.connector.Error as err:
        print(f"Error creating 'mcs_requests' table: {err}")
    finally:
        cursor.close()
        conn.close()

def save_mcs_request(project_id, indicators):
    """
    Menyimpan permintaan MCS ke tabel mcs_requests.
    Args:
        project_id (str): ID proyek.
        indicators (list of dict): List indikator MCS dengan format:
            [
                {"indicator": "Profit Margin", "uom": "%", "target": 20.0},
                {"indicator": "Customer Satisfaction", "uom": "Score", "target": 85}
            ]
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for indicator in indicators:
            query = """
                INSERT INTO mcs_requests (project_id, indicator, uom, target)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (project_id, indicator["indicator"], indicator["uom"], indicator["target"]))
        
        conn.commit()
        print(f"Permintaan MCS untuk proyek {project_id} berhasil disimpan.")
        return True
    except mysql.connector.Error as err:
        print(f"Error saving MCS request: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_mcs_requests_by_project(project_id):
    """
    Mengambil log permintaan MCS berdasarkan proyek.
    Args:
        project_id (str): ID proyek.
    Returns:
        list of tuple: List permintaan MCS dengan format:
            (id, indicator, uom, target, status, rejection_message, created_at, updated_at)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT id, indicator, uom, target, status, rejection_message, created_at, updated_at
            FROM mcs_requests
            WHERE project_id = %s
        """
        cursor.execute(query, (project_id,))
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error fetching MCS requests for project {project_id}: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def approve_mcs_request(mcs_id):
    """
    Menyetujui permintaan MCS.
    Args:
        mcs_id (int): ID permintaan MCS.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE mcs_requests
            SET status = 'Approved', rejection_message = NULL
            WHERE id = %s
        """
        cursor.execute(query, (mcs_id,))
        conn.commit()
        print(f"Permintaan MCS dengan ID {mcs_id} telah disetujui.")
        return True
    except mysql.connector.Error as err:
        print(f"Error approving MCS request {mcs_id}: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def reject_mcs_request_with_message(mcs_id, rejection_message):
    """
    Menolak permintaan MCS dengan alasan penolakan.
    Args:
        mcs_id (int): ID permintaan MCS.
        rejection_message (str): Pesan alasan penolakan.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE mcs_requests
            SET status = 'Rejected', rejection_message = %s
            WHERE id = %s
        """
        cursor.execute(query, (rejection_message, mcs_id))
        conn.commit()
        print(f"Permintaan MCS dengan ID {mcs_id} telah ditolak.")
        return True
    except mysql.connector.Error as err:
        print(f"Error rejecting MCS request {mcs_id}: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_pending_mcs_requests():
    """
    Mengambil semua permintaan MCS berstatus 'Pending'.
    Returns:
        list of tuple: List permintaan MCS dengan format:
            (id, project_id, indicator, uom, target, status, rejection_message, created_at, updated_at)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT id, project_id, indicator, uom, target, status, rejection_message, created_at, updated_at
            FROM mcs_requests
            WHERE status = 'Pending'
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error fetching pending MCS requests: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def submit_mcs_request(project_id, indicators):
    """
    Menyimpan pengajuan MCS ke tabel mcs_requests.
    Args:
        project_id (str): ID proyek.
        indicators (list): Daftar indikator yang akan diajukan.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Masukkan setiap indikator ke tabel mcs_requests
        for indicator in indicators:
            query = """
                INSERT INTO mcs_requests (project_id, indicator, uom, target)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (project_id, indicator["indicator"], indicator["uom"], indicator["target"]))
        
        conn.commit()
        print(f"Pengajuan MCS untuk proyek {project_id} berhasil disimpan.")
        return True
    except mysql.connector.Error as err:
        print(f"Error saat menyimpan pengajuan MCS: {err}")
        return False
    finally:
        cursor.close()
        conn.close()