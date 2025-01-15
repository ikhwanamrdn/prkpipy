import mysql.connector
from db.connection import get_connection

def create_mcs_requests_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Membuat tabel `mcs_requests` dengan kolom level_1 hingga level_10
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcs_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id VARCHAR(20) NOT NULL,
                indicator VARCHAR(255) NOT NULL,
                uom VARCHAR(50) NOT NULL,
                level_1 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 1
                level_2 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 2
                level_3 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 3
                level_4 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 4
                level_5 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 5
                level_6 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 6
                level_7 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 7
                level_8 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 8
                level_9 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 9
                level_10 FLOAT NOT NULL DEFAULT 0,        -- Nilai level 10
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
            (id, indicator, uom, level_1, ..., level_10, status, rejection_message, created_at, updated_at)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT id, indicator, uom,
                   level_1, level_2, level_3, level_4, level_5,
                   level_6, level_7, level_8, level_9, level_10,
                   status, rejection_message, created_at, updated_at
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

def approve_mcs_request(mcs_id, levels):
    """
    Menyetujui permintaan MCS dan menyimpannya ke tabel `mcs_roi`.
    Args:
        mcs_id (int): ID permintaan MCS.
        levels (dict): Level 1-10 untuk disimpan.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Update status permintaan MCS menjadi "Approved"
        cursor.execute("""
            UPDATE mcs_requests
            SET status = 'Approved', rejection_message = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (mcs_id,))
        conn.commit()

        # Ambil data MCS dari tabel `mcs_requests`
        cursor.execute("""
            SELECT project_id, indicator, uom
            FROM mcs_requests
            WHERE id = %s
        """, (mcs_id,))
        mcs_data = cursor.fetchone()

        if not mcs_data:
            print(f"Permintaan MCS dengan ID {mcs_id} tidak ditemukan.")
            return False

        project_id, indicator, uom = mcs_data

        # Simpan data ke tabel `mcs_roi`
        cursor.execute("""
            INSERT INTO mcs_roi (
                project_id, indicator, uom,
                level_1, level_2, level_3, level_4, level_5,
                level_6, level_7, level_8, level_9, level_10, progress
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """, (
            project_id, indicator, uom,
            levels["level_1"], levels["level_2"], levels["level_3"], levels["level_4"], levels["level_5"],
            levels["level_6"], levels["level_7"], levels["level_8"], levels["level_9"], levels["level_10"],
            0  # Progress awal = 0%
        ))
        conn.commit()

        print(f"MCS dengan ID {mcs_id} berhasil disimpan ke tabel `mcs_roi`.")
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
        indicators (list): Daftar indikator yang akan diajukan, setiap indikator berupa dictionary:
            [
                {"indicator": "Nama Indikator", "uom": "Unit"},
                ...
            ]
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Validasi input
        if not indicators or not isinstance(indicators, list):
            print("Error: 'indicators' harus berupa list dan tidak boleh kosong.")
            return False

        for indicator in indicators:
            if not all(key in indicator for key in ("indicator", "uom")):
                print(f"Error: Data indikator tidak lengkap: {indicator}")
                return False

            # Masukkan data ke tabel mcs_requests
            query = """
                INSERT INTO mcs_requests (project_id, indicator, uom)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (project_id, indicator["indicator"], indicator["uom"]))

        conn.commit()
        print(f"Pengajuan MCS untuk proyek {project_id} berhasil disimpan.")
        return True
    except mysql.connector.Error as err:
        print(f"Error saat menyimpan pengajuan MCS: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_approved_mcs_to_roi(mcs_id, levels):
    """
    Menyimpan data MCS yang disetujui ke tabel `mcs_roi`.
    Args:
        mcs_id (int): ID dari MCS yang disetujui.
        levels (dict): Data level (1-10) dalam format dictionary.
            Contoh: {"level_1": 10, "level_2": 20, ..., "level_10": 100}
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil data dari tabel `mcs_requests`
        cursor.execute("""
            SELECT project_id, indicator, uom
            FROM mcs_requests
            WHERE id = %s AND status = 'Approved'
        """, (mcs_id,))
        mcs_data = cursor.fetchone()

        if not mcs_data:
            print(f"MCS dengan ID {mcs_id} tidak ditemukan atau belum disetujui.")
            return False

        project_id, indicator, uom = mcs_data

        # Masukkan data ke tabel `mcs_roi`
        query = """
            INSERT INTO mcs_roi (
                project_id, indicator, uom,
                level_1, level_2, level_3, level_4, level_5,
                level_6, level_7, level_8, level_9, level_10, progress
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, 0
            )
        """
        cursor.execute(query, (
            project_id, indicator, uom,
            levels.get("level_1", 0), levels.get("level_2", 0), levels.get("level_3", 0),
            levels.get("level_4", 0), levels.get("level_5", 0), levels.get("level_6", 0),
            levels.get("level_7", 0), levels.get("level_8", 0), levels.get("level_9", 0),
            levels.get("level_10", 0)
        ))
        conn.commit()

        print(f"MCS untuk proyek {project_id} berhasil disimpan ke tabel `mcs_roi`.")
        return True
    except mysql.connector.Error as err:
        print(f"Error saving approved MCS to ROI: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def edit_mcs_request(mcs_id, indicator, uom, levels):
    """
    Mengedit permintaan MCS berdasarkan ID.
    Args:
        mcs_id (int): ID permintaan MCS.
        indicator (str): Indikator baru.
        uom (str): Unit of Measurement baru.
        levels (dict): Level 1-10 baru.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE mcs_requests
            SET indicator = %s, uom = %s,
                level_1 = %s, level_2 = %s, level_3 = %s, level_4 = %s, level_5 = %s,
                level_6 = %s, level_7 = %s, level_8 = %s, level_9 = %s, level_10 = %s,
                status = 'Pending', rejection_message = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        cursor.execute(query, (
            indicator, uom,
            levels["level_1"], levels["level_2"], levels["level_3"], levels["level_4"], levels["level_5"],
            levels["level_6"], levels["level_7"], levels["level_8"], levels["level_9"], levels["level_10"],
            mcs_id,
        ))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error editing MCS request {mcs_id}: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_approved_mcs_by_project(project_id):
    """
    Mengambil data MCS yang sudah diapprove untuk proyek tertentu dari tabel mcs_roi.
    Args:
        project_id (str): ID proyek.
    Returns:
        list of tuple: Data MCS yang sudah diapprove.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query untuk mengambil data MCS yang sudah diapprove
        query = """
            SELECT 
                project_id, indicator, uom,
                level_1, level_2, level_3, level_4, level_5,
                level_6, level_7, level_8, level_9, level_10,
                progress, created_at
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