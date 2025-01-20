import datetime
from db.connection import get_connection

# Function to record attendance
import datetime
from db.connection import get_connection

# Function to record attendance
def save_absen(employee_id, present_id, location_id, training_name, presence_date, time_in=None, time_out=None):
    """
    Menyimpan data absen ke tabel presence berdasarkan tanggal yang dipilih.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if present_id == 1:  # Check In
            # Validasi: Cek apakah pengguna sudah Check In pada tanggal yang dipilih
            cursor.execute(
                "SELECT * FROM presence WHERE employees_id = %s AND presence_date = %s AND present_id = 1",
                (employee_id, presence_date)
            )
            existing_record = cursor.fetchone()

            if existing_record:
                return False, "Anda sudah melakukan Check In pada tanggal yang dipilih."

            # Insert data baru untuk Check In
            query = """
            INSERT INTO presence (employees_id, presence_date, time_in, present_id, lokasi_id, nama_training)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (employee_id, presence_date, time_in, 1, location_id, training_name))
            conn.commit()
            return True, "Check In berhasil."

        elif present_id == 2:  # Check Out
            # Validasi: Pastikan Check In sudah dilakukan dan belum ada Check Out
            cursor.execute(
                """
                SELECT * FROM presence 
                WHERE employees_id = %s AND presence_date = %s AND present_id = 1 AND time_out IS NULL
                """,
                (employee_id, presence_date)
            )
            existing_checkin = cursor.fetchone()

            if not existing_checkin:
                return False, "Anda belum melakukan Check In atau sudah melakukan Check Out."

            # Update data untuk Check Out
            query = """
            UPDATE presence
            SET time_out = %s
            WHERE employees_id = %s AND presence_date = %s AND present_id = 1 AND time_out IS NULL
            """
            cursor.execute(query, (time_out, employee_id, presence_date))
            conn.commit()

            if cursor.rowcount > 0:
                # Jika Check Out berhasil, hitung ulang mandays_berjalan berdasarkan entri dengan present_id = 1
                if training_name:
                    cursor.execute(
                        """
                        SELECT COUNT(*) AS total_checkin
                        FROM presence
                        WHERE nama_training = %s AND present_id = 1
                        """,
                        (training_name,)
                    )
                    result = cursor.fetchone()
                    total_checkin = result['total_checkin'] if result else 0

                    # Update mandays_berjalan di kelola_project
                    cursor.execute(
                        """
                        UPDATE kelola_project
                        SET mandays_berjalan = %s
                        WHERE id = %s
                        """,
                        (total_checkin, training_name)
                    )
                    conn.commit()
                return True, "Check Out berhasil dan mandays_berjalan diperbarui."
            else:
                return False, "Check Out gagal: Anda mungkin sudah melakukan Check Out sebelumnya."

    except Exception as e:
        print(f"[ERROR] Gagal menyimpan data absen: {e}")
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()