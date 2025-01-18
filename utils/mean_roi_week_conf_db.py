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

# Fungsi untuk membuat tabel Mean ROI Week
def create_mean_roi_week_table():
    """
    Membuat tabel `mean_roi_week` untuk menyimpan data ROI mingguan.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mean_roi_week (
                id INT AUTO_INCREMENT PRIMARY KEY,       -- ID unik untuk setiap record
                mcs_roi_id INT NOT NULL,                 -- Foreign key ke mcs_roi
                start_date DATE NOT NULL,                -- Tanggal mulai
                end_date DATE NOT NULL,                  -- Tanggal akhir
                bulan INT NOT NULL,                      -- Bulan otomatis dihitung
                pekan INT NOT NULL,                      -- Pekan ke (1-4)
                nilai FLOAT NOT NULL,                    -- Nilai pekan (boleh negatif)
                rata_rata FLOAT DEFAULT NULL,            -- Rata-rata nilai per pekan
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Waktu pembuatan
                FOREIGN KEY (mcs_roi_id) REFERENCES mcs_roi(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("Tabel `mean_roi_week` berhasil dibuat atau diperbarui.")
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

# Fungsi untuk mengambil indikator dari tabel `mcs_roi`
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

def calculate_month_on_going(mcs_roi_id, start_date):
    """
    Menghitung bulan berjalan berdasarkan data yang sudah ada untuk indikator tertentu.
    Jika bulan tidak berurutan, bulan dihitung berdasarkan jumlah bulan unik sebelumnya.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil semua bulan unik berdasarkan tanggal mulai sebelumnya
        cursor.execute("""
            SELECT DISTINCT DATE_FORMAT(start_date, '%Y-%m') AS bulan_unik
            FROM mean_roi_week
            WHERE mcs_roi_id = %s
            ORDER BY bulan_unik
        """, (mcs_roi_id,))
        unique_months = [row[0] for row in cursor.fetchall()]

        # Konversi start_date ke format 'YYYY-MM'
        current_month = start_date.strftime('%Y-%m')

        if current_month in unique_months:
            # Jika bulan sudah ada, gunakan indeks bulan
            return unique_months.index(current_month) + 1
        else:
            # Jika bulan baru, tambahkan ke daftar dan hitung indeks
            return len(unique_months) + 1
    except mysql.connector.Error as e:
        print(f"Error calculating month on going: {e}")
        return 1  # Default bulan pertama jika terjadi error
    finally:
        cursor.close()
        conn.close()

def calculate_week_on_going(mcs_roi_id, start_date):
    """
    Menghitung pekan berjalan dalam bulan berdasarkan data yang sudah ada.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil bulan berjalan untuk indikator tertentu
        cursor.execute("""
            SELECT bulan
            FROM mean_roi_week
            WHERE mcs_roi_id = %s
            ORDER BY bulan DESC
            LIMIT 1
        """, (mcs_roi_id,))
        current_month = cursor.fetchone()

        if current_month:
            # Jika ada bulan yang sama, hitung pekan berdasarkan entri di bulan tersebut
            cursor.execute("""
                SELECT COUNT(*)
                FROM mean_roi_week
                WHERE mcs_roi_id = %s AND bulan = %s
            """, (mcs_roi_id, current_month[0]))
            week_count = cursor.fetchone()[0]
            return week_count + 1 if week_count < 4 else 1  # Pekan berjalan (maks 4)
        else:
            # Jika tidak ada data sama sekali, mulai dari pekan 1
            return 1
    except mysql.connector.Error as e:
        print(f"Error calculating week on going: {e}")
        return 1  # Default pekan pertama jika terjadi error
    finally:
        cursor.close()
        conn.close()

def save_mean_roi_week(mcs_roi_id, start_date, end_date, nilai):
    """
    Menyimpan data ke tabel `mean_roi_week` dengan perhitungan rata-rata yang akurat
    dan memastikan bulan dan pekan terhitung dengan benar.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil data terakhir dari tabel
        cursor.execute("""
            SELECT MAX(bulan), MAX(pekan), MAX(end_date)
            FROM mean_roi_week
            WHERE mcs_roi_id = %s
        """, (mcs_roi_id,))
        result = cursor.fetchone()
        last_bulan, last_pekan, last_end_date = result if result else (None, None, None)

        # Hitung bulan berjalan
        month_on_going = calculate_month_on_going(mcs_roi_id, start_date)

        # Hitung pekan berjalan
        if last_bulan is None or month_on_going > last_bulan:
            # Jika bulan baru, reset pekan ke 1
            week_on_going = 1
        else:
            # Jika masih di bulan yang sama, tambahkan pekan
            cursor.execute("""
                SELECT MAX(pekan)
                FROM mean_roi_week
                WHERE mcs_roi_id = %s AND bulan = %s
            """, (mcs_roi_id, month_on_going))
            max_pekan_bulan = cursor.fetchone()[0] or 0
            week_on_going = max_pekan_bulan + 1 if max_pekan_bulan < 4 else 4

        # Cek jika ada data dengan range tanggal yang sama
        cursor.execute("""
            SELECT 1 FROM mean_roi_week 
            WHERE mcs_roi_id = %s AND start_date = %s AND end_date = %s
        """, (mcs_roi_id, start_date, end_date))
        existing_entry = cursor.fetchone()

        if existing_entry:
            return False, "Data dengan range tanggal yang sama sudah ada."

        # Simpan data ke tabel
        cursor.execute("""
            INSERT INTO mean_roi_week (mcs_roi_id, start_date, end_date, bulan, pekan, nilai)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (mcs_roi_id, start_date, end_date, month_on_going, week_on_going, nilai))

        # Hitung rata-rata nilai untuk bulan tersebut
        cursor.execute("""
            SELECT AVG(nilai) AS rata_rata
            FROM mean_roi_week
            WHERE mcs_roi_id = %s AND bulan = %s
        """, (mcs_roi_id, month_on_going))
        rata_rata = cursor.fetchone()[0]

        if rata_rata is not None:
            # Update rata-rata di semua entri bulan tersebut
            cursor.execute("""
                UPDATE mean_roi_week
                SET rata_rata = %s
                WHERE mcs_roi_id = %s AND bulan = %s
            """, (rata_rata, mcs_roi_id, month_on_going))

        conn.commit()
        return True, f"Data berhasil disimpan. Rata-rata bulan {month_on_going} diperbarui menjadi {rata_rata:.2f}."
    except mysql.connector.Error as e:
        return False, f"Error saving data to `mean_roi_week`: {e}"
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk menampilkan data Mean ROI Week
def get_mean_roi_week_data(project_id=None):
    """
    Mengambil data dari `mean_roi_week` berdasarkan project_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if project_id:
            query = """
                SELECT 
                    mr.indicator,
                    mw.start_date,
                    mw.end_date,
                    mw.bulan,
                    mw.pekan,
                    mw.nilai,
                    mw.rata_rata,
                    mw.created_at
                FROM mean_roi_week mw
                JOIN mcs_roi mr ON mw.mcs_roi_id = mr.id
                WHERE mr.project_id = %s
                ORDER BY mw.start_date
            """
            cursor.execute(query, (project_id,))
        else:
            query = """
                SELECT 
                    mr.indicator,
                    mw.start_date,
                    mw.end_date,
                    mw.bulan,
                    mw.pekan,
                    mw.nilai,
                    mw.rata_rata,
                    mw.created_at
                FROM mean_roi_week mw
                JOIN mcs_roi mr ON mw.mcs_roi_id = mr.id
                ORDER BY mw.start_date
            """
            cursor.execute(query)

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

def check_existing_date_range(mcs_roi_id, start_date, end_date):
    """
    Memeriksa apakah sudah ada data dengan rentang tanggal yang sama dalam tabel `mean_roi_week`.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT 1
            FROM mean_roi_week
            WHERE mcs_roi_id = %s AND (
                (start_date <= %s AND end_date >= %s) OR
                (start_date <= %s AND end_date >= %s)
            )
        """
        cursor.execute(query, (mcs_roi_id, start_date, start_date, end_date, end_date))
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error as e:
        print(f"Error checking date range in `mean_roi_week`: {e}")
        return False
    finally:
        cursor.close()
        conn.close()