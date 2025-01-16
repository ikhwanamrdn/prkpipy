import mysql.connector
from db.connection import get_connection


def create_mcs_requests_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcs_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id VARCHAR(20) NOT NULL,       -- ID proyek
                indicator VARCHAR(255) NOT NULL,      -- Indikator
                uom VARCHAR(50) NOT NULL,             -- Unit of Measurement
                target FLOAT NOT NULL,                -- Target indikator
                status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending', -- Status MCS
                rejection_message TEXT NULL,          -- Pesan penolakan
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

def submit_mcs_request(project_id, indicators):
    """
    Menyimpan pengajuan MCS ke tabel `mcs_requests`.
    Args:
        project_id (str): ID proyek.
        indicators (list of dict): List indikator MCS dengan format:
            [
                {"indicator": "Profit Margin", "uom": "%", "target": 20.0},
                {"indicator": "Customer Satisfaction", "uom": "Score", "target": 85.0}
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
        print(f"Pengajuan MCS untuk proyek {project_id} berhasil disimpan.")
        return True
    except mysql.connector.Error as err:
        print(f"Error saat menyimpan pengajuan MCS: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_mcs_requests_by_project(project_id):
    """
    Mengambil data MCS berdasarkan project_id dari tabel `mcs_requests`.
    Args:
        project_id (str): ID proyek.
    Returns:
        list of tuple: Data MCS untuk proyek tertentu.
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
    Menyetujui permintaan MCS dan memperbarui status menjadi 'Approved'.
    Args:
        mcs_id (int): ID permintaan MCS.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query untuk memperbarui status menjadi 'Approved'
        query = """
            UPDATE mcs_requests
            SET status = 'Approved', rejection_message = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        cursor.execute(query, (mcs_id,))
        conn.commit()
        print(f"Permintaan MCS dengan ID {mcs_id} berhasil disetujui.")
        return True
    except mysql.connector.Error as err:
        print(f"Error approving MCS request {mcs_id}: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def reject_mcs_request(mcs_id, rejection_message):
    """
    Menolak permintaan MCS dengan alasan.
    Args:
        mcs_id (int): ID permintaan MCS.
        rejection_message (str): Alasan penolakan.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query untuk memperbarui status menjadi 'Rejected' dan menambahkan pesan penolakan
        query = """
            UPDATE mcs_requests
            SET status = 'Rejected', rejection_message = %s, updated_at = CURRENT_TIMESTAMP
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
        # Query untuk memperbarui status menjadi 'Rejected' dan menambahkan pesan penolakan
        query = """
            UPDATE mcs_requests
            SET status = 'Rejected', rejection_message = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        cursor.execute(query, (rejection_message, mcs_id))
        conn.commit()
        print(f"Permintaan MCS dengan ID {mcs_id} telah ditolak dengan pesan: {rejection_message}")
        return True
    except mysql.connector.Error as err:
        print(f"Error rejecting MCS request {mcs_id}: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def edit_mcs_request(mcs_id, indicator, uom, target):
    """
    Mengedit permintaan MCS berdasarkan ID.
    Args:
        mcs_id (int): ID permintaan MCS.
        indicator (str): Indikator baru.
        uom (str): Unit of Measurement baru.
        target (float): Target baru.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE mcs_requests
            SET indicator = %s, uom = %s, target = %s,
                status = 'Pending', rejection_message = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        cursor.execute(query, (indicator, uom, target, mcs_id))
        conn.commit()
        print(f"Permintaan MCS dengan ID {mcs_id} berhasil diperbarui dan diajukan ulang.")
        return True
    except mysql.connector.Error as err:
        print(f"Error editing MCS request {mcs_id}: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def approve_mcs_request(mcs_id):
    """
    Menyetujui permintaan MCS dan memperbarui status menjadi 'On Going'.
    Args:
        mcs_id (int): ID permintaan MCS.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Perbarui status ke 'On Going'
        cursor.execute("""
            UPDATE mcs_roi
            SET status = 'On Going', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'On Going'
        """, (mcs_id,))
        conn.commit()

        if cursor.rowcount == 0:
            print(f"MCS dengan ID {mcs_id} tidak ditemukan atau sudah 'Achieved'.")
            return False

        print(f"MCS dengan ID {mcs_id} berhasil disetujui dan status menjadi 'On Going'.")
        return True

    except mysql.connector.Error as err:
        print(f"Error approving MCS request {mcs_id}: {err}")
        return False

    finally:
        cursor.close()
        conn.close()

def get_mcs_roi_by_project(project_id):
    """
    Mengambil data MCS ROI berdasarkan project_id.

    Args:
        project_id (str): ID proyek yang datanya ingin diambil.

    Returns:
        list of tuple: Data MCS ROI yang ditemukan untuk project_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

def get_approved_mcs_by_project(project_id):
    """
    Mengambil data MCS yang sudah disetujui untuk proyek tertentu dari tabel mcs_roi.
    Args:
        project_id (str): ID proyek.
    Returns:
        list of tuple: Data MCS yang sudah disetujui.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT project_id, indicator, uom, target, created_at, updated_at
            FROM mcs_roi
            WHERE project_id = %s
        """
        cursor.execute(query, (project_id,))
        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        print(f"Error fetching approved MCS for project {project_id}: {err}")
        return []

    finally:
        cursor.close()
        conn.close()

def save_to_mcs_roi(project_id, indicator, uom, target):
    """
    Menyimpan data ke tabel `mcs_roi` untuk MCS yang diterima.
    
    Args:
        project_id (str): ID proyek yang terkait.
        indicator (str): Nama indikator.
        uom (str): Unit of Measurement (satuan).
        target (float): Target nilai indikator.

    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert data ke tabel `mcs_roi`
        query = """
            INSERT INTO mcs_roi (project_id, indicator, uom, target, status)
            VALUES (%s, %s, %s, %s, 'On Going')
        """
        cursor.execute(query, (project_id, indicator, uom, target))
        conn.commit()

        print(f"Data MCS dengan indikator '{indicator}' berhasil disimpan ke tabel `mcs_roi`.")
        return True
    except mysql.connector.Error as err:
        print(f"Error saving MCS ROI: {err}")
        return False
    finally:
        cursor.close()
        conn.close()