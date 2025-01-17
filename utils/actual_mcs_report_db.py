import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="kpix"
    )

def create_aktual_mcs_roi_report_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Membuat atau memperbarui tabel aktual_mcs_roi_report
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aktual_mcs_roi_report (
                id INT AUTO_INCREMENT PRIMARY KEY,
                indicator VARCHAR(255) NOT NULL,
                bulan INT NOT NULL,
                m1 FLOAT DEFAULT NULL,
                m2 FLOAT DEFAULT NULL,
                m3 FLOAT DEFAULT NULL,
                m4 FLOAT DEFAULT NULL,
                target FLOAT NOT NULL,
                rata_rata FLOAT DEFAULT NULL,
                uom VARCHAR(50) DEFAULT NULL
            )
        """)
        conn.commit()
        print("Tabel `aktual_mcs_roi_report` berhasil dibuat atau diperbarui.")
    except mysql.connector.Error as e:
        print(f"Error creating `aktual_mcs_roi_report` table: {e}")
    finally:
        cursor.close()
        conn.close()


def get_aktual_mcs_roi_report():
    conn = get_connection()
    try:
        query = """
            SELECT indicator, bulan, m1, m2, m3, m4, target, rata_rata, uom
            FROM aktual_mcs_roi_report
            ORDER BY bulan, indicator
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except mysql.connector.Error as e:
        print(f"Error fetching data from `aktual_mcs_roi_report`: {e}")
        return []
    finally:
        conn.close()

def fetch_mean_roi_week_data(mcs_roi_id, bulan):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT pekan, nilai
            FROM mean_roi_week
            WHERE mcs_roi_id = %s AND bulan = %s
        """
        cursor.execute(query, (mcs_roi_id, bulan))
        data = cursor.fetchall()
        print(f"Data dari mean_roi_week untuk mcs_roi_id {mcs_roi_id} dan bulan {bulan}: {data}")
        return {row[0]: row[1] for row in data}  # Pekan sebagai key, nilai sebagai value
    except mysql.connector.Error as e:
        print(f"Error fetching mean ROI week data: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()

def insert_or_update_aktual_mcs_roi_report(mcs_roi_id, bulan, target):
    conn = get_connection()
    try:
        # Fetch indikator dan uom dari mcs_roi
        with conn.cursor() as cursor:
            cursor.execute("SELECT indicator, uom FROM mcs_roi WHERE id = %s", (mcs_roi_id,))
            result = cursor.fetchone()
            if not result:
                print(f"Indicator with mcs_roi_id {mcs_roi_id} not found.")
                return False
            indicator, uom = result

        # Fetch mean_roi_week data
        mean_roi_data = fetch_mean_roi_week_data(mcs_roi_id, bulan)
        rata_rata = (
            sum(mean_roi_data.values()) / len(mean_roi_data) if mean_roi_data else 0
        )

        # Check if data already exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM aktual_mcs_roi_report WHERE indicator = %s AND bulan = %s",
                (indicator, bulan),
            )
            row = cursor.fetchone()

            if row:  # Update existing row
                report_id = row[0]
                updates = []
                params = []
                for pekan, nilai in mean_roi_data.items():
                    updates.append(f"m{pekan} = %s")
                    params.append(nilai)
                params.extend([rata_rata, report_id])  # Add rata-rata and ID to params

                query = f"""
                    UPDATE aktual_mcs_roi_report
                    SET {', '.join(updates)}, rata_rata = %s
                    WHERE id = %s
                """
                cursor.execute(query, params)
            else:  # Insert new row
                cursor.execute(
                    """
                    INSERT INTO aktual_mcs_roi_report (indicator, bulan, m1, m2, m3, m4, target, rata_rata, uom)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        indicator,
                        bulan,
                        mean_roi_data.get(1, None),  # M1
                        mean_roi_data.get(2, None),  # M2
                        mean_roi_data.get(3, None),  # M3
                        mean_roi_data.get(4, None),  # M4
                        target,
                        rata_rata,
                        uom
                    ),
                )

        conn.commit()
        print("Data berhasil diperbarui di aktual_mcs_roi_report.")
        return True
    except mysql.connector.Error as e:
        print(f"Error updating data in aktual_mcs_roi_report: {e}")
        return False
    finally:
        conn.close()

def save_mean_roi_week(mcs_roi_id, bulan, pekan, nilai):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Simpan atau perbarui data di mean_roi_week
        cursor.execute("""
            INSERT INTO mean_roi_week (mcs_roi_id, bulan, pekan, nilai)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nilai = VALUES(nilai)
        """, (mcs_roi_id, bulan, pekan, nilai))

        # Ambil target dari tabel mcs_roi
        cursor.execute("""
            SELECT target
            FROM mcs_roi
            WHERE id = %s
        """, (mcs_roi_id,))
        target = cursor.fetchone()
        if not target:
            print(f"Target tidak ditemukan untuk mcs_roi_id {mcs_roi_id}.")
            return False
        target = target[0]

        # Panggil fungsi untuk memperbarui aktual_mcs_roi_report
        insert_or_update_aktual_mcs_roi_report(mcs_roi_id, bulan, target)

        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error saving data to `mean_roi_week`: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_target_from_mcs_roi(mcs_roi_id):
    conn = get_connection()
    try:
        query = """
            SELECT target
            FROM mcs_roi
            WHERE id = %s
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (mcs_roi_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Error fetching target from mcs_roi: {e}")
        return None
    finally:
        conn.close()