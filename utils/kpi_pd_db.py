import mysql.connector
from db.connection import get_connection

def create_kpi_pd_table():
    """
    Membuat tabel `kpi_pd` jika belum ada.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_pd (
                id INT AUTO_INCREMENT PRIMARY KEY,         -- ID unik untuk setiap KPI
                project_id VARCHAR(20) NOT NULL,           -- ID Proyek (relasi ke projects)
                indicator VARCHAR(255) NOT NULL,           -- Nama indikator KPI
                uom VARCHAR(50) NOT NULL,                  -- Unit of Measure (satuan)
                level_1 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 1
                level_2 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 2
                level_3 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 3
                level_4 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 4
                level_5 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 5
                level_6 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 6
                level_7 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 7
                level_8 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 8
                level_9 FLOAT NOT NULL DEFAULT 0,          -- Nilai level 9
                level_10 FLOAT NOT NULL DEFAULT 0,         -- Nilai level 10
                progress FLOAT NOT NULL DEFAULT 0,         -- Progress pencapaian (0-100%)
                alasan TEXT NULL,                          -- Alasan dari PD
                status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending', -- Status pengajuan
                rejection_message TEXT NULL,               -- Alasan penolakan (jika ada)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Waktu pembuatan
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Waktu pembaruan
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE  -- Relasi ke tabel projects
            )
        """)
        conn.commit()
        print("Tabel `kpi_pd` berhasil dibuat atau diperbarui.")
    except mysql.connector.Error as err:
        print(f"Error creating `kpi_pd` table: {err}")
    finally:
        cursor.close()
        conn.close()

def insert_kpi_pd(project_id, indicator, uom, levels, alasan):
    """
    Menambahkan KPI baru ke tabel `kpi_pd` beserta alasan.
    Args:
        project_id (str): ID proyek.
        indicator (str): Nama indikator KPI.
        uom (str): Unit of Measurement.
        levels (dict): Nilai level 1-10.
        alasan (str): Alasan dari PD.
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO kpi_pd (
                project_id, indicator, uom,
                level_1, level_2, level_3, level_4, level_5,
                level_6, level_7, level_8, level_9, level_10,
                alasan, status, progress
            )
            VALUES (%s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, 'Pending', 0)
        """
        cursor.execute(query, (
            project_id, indicator, uom,
            levels.get("level_1", 0), levels.get("level_2", 0), levels.get("level_3", 0),
            levels.get("level_4", 0), levels.get("level_5", 0), levels.get("level_6", 0),
            levels.get("level_7", 0), levels.get("level_8", 0), levels.get("level_9", 0),
            levels.get("level_10", 0), alasan
        ))
        conn.commit()
        print(f"KPI untuk proyek {project_id} berhasil ditambahkan dengan alasan.")
        return True
    except mysql.connector.Error as err:
        print(f"Error inserting KPI PD: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_kpi_by_project(project_id):
    """
    Mengambil semua KPI terkait proyek tertentu.
    Args:
        project_id (str): ID proyek.
    Returns:
        list of tuple: Daftar KPI terkait proyek.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT id, indicator, uom,
                   level_1, level_2, level_3, level_4, level_5,
                   level_6, level_7, level_8, level_9, level_10,
                   progress, alasan, status, rejection_message, created_at, updated_at
            FROM kpi_pd
            WHERE project_id = %s
        """
        cursor.execute(query, (project_id,))
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error fetching KPI for project ID {project_id}: {err}")
        return []
    finally:
        cursor.close()
        conn.close()