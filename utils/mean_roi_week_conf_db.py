import pandas as pd
from db.connection import get_connection
import mysql.connector
import streamlit as st

# Fungsi untuk menghubungkan ke database
def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Ganti dengan host MySQL Anda
        user="root",       # Ganti dengan user MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="kpix"    # Ganti dengan nama database Anda
    )

def create_mean_roi_week_table():
    """
    Membuat tabel `mean_roi_week` untuk menyimpan data ROI mingguan dengan kolom created_at.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Membuat tabel `mean_roi_week` dengan kolom created_at
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mean_roi_week (
                id INT AUTO_INCREMENT PRIMARY KEY,       -- ID unik untuk setiap record
                mcs_roi_id INT NOT NULL,                 -- Foreign key ke mcs_roi
                bulan INT NOT NULL,                      -- Bulan berjalan
                pekan INT NOT NULL,                      -- Pekan ke (1-4)
                nilai FLOAT NOT NULL,                    -- Nilai pekan (boleh negatif)
                rata_rata FLOAT DEFAULT NULL,            -- Rata-rata nilai per bulan
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Waktu pembuatan
                FOREIGN KEY (mcs_roi_id) REFERENCES mcs_roi(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("Tabel `mean_roi_week` berhasil dibuat atau diperbarui dengan kolom `created_at`.")
    except mysql.connector.Error as e:
        print(f"Error creating `mean_roi_week` table: {e}")
    finally:
        cursor.close()
        conn.close()


def get_mean_roi_week():
    """
    Mengambil semua data dari tabel `mean_roi_week`.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT indicator, bulan, pekan, nilai, rata_rata FROM mean_roi_week ORDER BY bulan, pekan")
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as e:
        print(f"Error fetching data from `mean_roi_week`: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mengambil data indikator dari tabel mcs_roi
def get_mcs_roi_indicators(project_id):
    conn = get_connection()
    try:
        query = """
            SELECT id, indicator
            FROM mcs_roi
            WHERE project_id = %s AND status = 'On Going'
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (project_id,))
            return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error fetching indicators from mcs_roi: {e}")
        return []
    finally:
        conn.close()

# Fungsi untuk menyimpan data ke tabel mean_roi_week
def save_mean_roi_week(indicator_id, bulan, pekan, nilai):
    if check_existing_entry(indicator_id, bulan, pekan):
        print(f"Data untuk Bulan {bulan} dan Pekan {pekan} sudah ada. Tidak bisa menyimpan.")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Simpan data ke tabel mean_roi_week
        cursor.execute("""
            INSERT INTO mean_roi_week (mcs_roi_id, bulan, pekan, nilai)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nilai = VALUES(nilai)
        """, (indicator_id, bulan, pekan, nilai))

        # Hitung rata-rata untuk bulan dan indikator
        cursor.execute("""
            SELECT AVG(nilai) AS rata_rata
            FROM mean_roi_week
            WHERE mcs_roi_id = %s AND bulan = %s
        """, (indicator_id, bulan))
        rata_rata = cursor.fetchone()[0]

        # Update rata-rata di tabel mean_roi_week
        cursor.execute("""
            UPDATE mean_roi_week
            SET rata_rata = %s
            WHERE mcs_roi_id = %s AND bulan = %s
        """, (rata_rata, indicator_id, bulan))

        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error saving data to `mean_roi_week`: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menampilkan data mean_roi_week
def get_mean_roi_week_data():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                mr.indicator, 
                mw.bulan, 
                mw.pekan, 
                mw.nilai, 
                mw.rata_rata,
                mw.created_at
            FROM mean_roi_week mw
            JOIN mcs_roi mr ON mw.mcs_roi_id = mr.id
            ORDER BY mw.bulan, mw.pekan
        """)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as e:
        print(f"Error fetching data from `mean_roi_week`: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def check_existing_entry(indicator_id, bulan, pekan):
    """
    Mengecek apakah data dengan bulan dan pekan tertentu sudah ada di tabel mean_roi_week.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 1
            FROM mean_roi_week
            WHERE mcs_roi_id = %s AND bulan = %s AND pekan = %s
        """, (indicator_id, bulan, pekan))
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error as e:
        print(f"Error checking data in `mean_roi_week`: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

