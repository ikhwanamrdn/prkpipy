import mysql.connector
from db.connection import get_connection

def create_mcs_roi_table():
    """
    Membuat atau memperbarui tabel `mcs_roi` untuk input baru.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Membuat tabel `mcs_roi`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcs_roi (
                id INT AUTO_INCREMENT PRIMARY KEY,         -- ID unik untuk setiap record
                project_id VARCHAR(20) NOT NULL,           -- ID Proyek (relasi ke projects)
                indicator VARCHAR(255) NOT NULL,           -- Nama indikator
                uom VARCHAR(50) NOT NULL,                  -- Unit of Measure (satuan)
                target FLOAT NOT NULL CHECK (target >= 0), -- Target nilai indikator (tidak boleh negatif)
                status ENUM('On Going', 'Achieved') DEFAULT 'On Going', -- Status indikator
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Waktu pembuatan
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Waktu pembaruan
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE  -- Relasi ke tabel projects
            )
        """)
        conn.commit()
        print("Tabel 'mcs_roi' berhasil dibuat atau diperbarui.")
    except mysql.connector.Error as err:
        print(f"Error creating 'mcs_roi' table: {err}")
    finally:
        cursor.close()
        conn.close()

def get_mcs_roi_by_status(project_id, status):
    """
    Mengambil data MCS ROI berdasarkan project_id dan status tertentu.
    
    Args:
        project_id (str): ID proyek.
        status (str): Status MCS yang ingin diambil ('On Going', 'Achieved').
    
    Returns:
        list of tuple: Data MCS ROI yang ditemukan.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT 
                id, indicator, uom, target, status, created_at, updated_at
            FROM 
                mcs_roi
            WHERE 
                project_id = %s AND status = %s
        """
        cursor.execute(query, (project_id, status))
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error fetching MCS ROI for project {project_id} with status {status}: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def achieve_mcs(mcs_id):
    """
    Mengubah status MCS menjadi 'Achieved' untuk indikator yang sedang berjalan.
    
    Args:
        mcs_id (int): ID dari MCS ROI yang ingin diubah statusnya.
    
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Perbarui status menjadi 'Achieved'
        query = """
            UPDATE mcs_roi
            SET status = 'Achieved', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'On Going'
        """
        cursor.execute(query, (mcs_id,))
        conn.commit()

        if cursor.rowcount == 0:
            print(f"MCS dengan ID {mcs_id} tidak ditemukan atau statusnya sudah 'Achieved'.")
            return False

        print(f"MCS dengan ID {mcs_id} berhasil diubah menjadi 'Achieved'.")
        return True

    except mysql.connector.Error as err:
        print(f"Error achieving MCS {mcs_id}: {err}")
        return False

    finally:
        cursor.close()
        conn.close()