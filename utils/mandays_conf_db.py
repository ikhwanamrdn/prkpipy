import mysql.connector
from datetime import datetime


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="kpix"
    )


def create_mandays_conf_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mandays_conf (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id VARCHAR(20) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                jumlah_bulan INT NOT NULL,
                bulan_absen_update VARCHAR(20),
                bulan_berjalan INT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("Tabel 'mandays_conf' berhasil dibuat.")
    except mysql.connector.Error as err:
        print(f"Error creating 'mandays_conf' table: {err}")
    finally:
        cursor.close()
        conn.close()


def update_mandays_conf():
    """
    Memperbarui tabel mandays_conf berdasarkan data absen dan proyek.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Ambil semua proyek
        cursor.execute("""
            SELECT id, start_date, end_date FROM projects
        """)
        projects = cursor.fetchall()

        for project in projects:
            project_id = project['id']
            start_date = project['start_date']
            end_date = project['end_date']

            # Hitung jumlah bulan dari start_date ke end_date
            if start_date and end_date:
                jumlah_bulan = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month + 1)
            else:
                jumlah_bulan = 0

            # Ambil tanggal terakhir dari absen untuk proyek ini
            cursor.execute("""
                SELECT MAX(date) AS last_absen_date 
                FROM absen
                WHERE project_id = %s
            """, (project_id,))
            last_absen_date_result = cursor.fetchone()
            last_absen_date = last_absen_date_result['last_absen_date'] if last_absen_date_result['last_absen_date'] else start_date

            # Hitung bulan berjalan berdasarkan absen terakhir
            if start_date and last_absen_date:
                bulan_berjalan = ((last_absen_date.year - start_date.year) * 12) + (last_absen_date.month - start_date.month + 1)
            else:
                bulan_berjalan = 0

            # Validasi agar bulan_berjalan tidak melebihi jumlah_bulan proyek
            if end_date and last_absen_date > end_date:
                bulan_berjalan = jumlah_bulan

            # Hitung bulan absen yang diperbarui
            cursor.execute("""
                SELECT DISTINCT MONTH(date) AS bulan_absen, YEAR(date) AS tahun_absen
                FROM absen
                WHERE project_id = %s
            """, (project_id,))
            bulan_absen_data = cursor.fetchall()
            bulan_absen_update = len(bulan_absen_data)

            # Periksa apakah data sudah ada di mandays_conf
            cursor.execute("""
                SELECT id FROM mandays_conf WHERE project_id = %s
            """, (project_id,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Update data jika sudah ada
                cursor.execute("""
                    UPDATE mandays_conf
                    SET start_date = %s, end_date = %s, jumlah_bulan = %s,
                        bulan_absen_update = %s, bulan_berjalan = %s
                    WHERE project_id = %s
                """, (start_date, end_date, jumlah_bulan, bulan_absen_update, bulan_berjalan, project_id))
            else:
                # Insert data baru jika belum ada
                cursor.execute("""
                    INSERT INTO mandays_conf (project_id, start_date, end_date, jumlah_bulan, bulan_absen_update, bulan_berjalan)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (project_id, start_date, end_date, jumlah_bulan, bulan_absen_update, bulan_berjalan))

        conn.commit()
        print("Tabel 'mandays_conf' berhasil diperbarui.")
    except Exception as e:
        print(f"Error updating mandays_conf: {e}")
    finally:
        cursor.close()
        conn.close()


def get_mandays_conf_by_project(project_id):
    """
    Mengambil data mandays_conf berdasarkan project_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM mandays_conf WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Error fetching mandays_conf for project {project_id}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()