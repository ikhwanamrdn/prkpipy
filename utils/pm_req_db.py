from binascii import Error
import mysql

def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Ganti dengan host MySQL Anda
        user="root",       # Ganti dengan user MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="kpix"    # Ganti dengan nama database Anda
    )
def create_pm_requests_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Periksa apakah tabel 'projects' sudah dibuat
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'projects'
        """)
        projects_exists = cursor.fetchone()[0]

        if not projects_exists:
            raise ValueError("Tabel 'projects' belum dibuat. Pastikan tabel 'projects' sudah ada.")

        # Periksa apakah tabel 'pm_requests' ada
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'pm_requests'
        """)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("Tabel 'pm_requests' sudah ada.")
        else:
            # Buat tabel 'pm_requests' jika belum ada
            cursor.execute("""
                CREATE TABLE pm_requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id VARCHAR(20) NOT NULL,
                    pm_name VARCHAR(255) NOT NULL,
                    pd_name VARCHAR(255) NOT NULL,
                    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
                    rejection_message TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            print("Tabel 'pm_requests' berhasil dibuat.")
    except Exception as e:
        print(f"Error creating 'pm_requests' table: {e}")
    finally:
        cursor.close()
        conn.close()


def submit_pm_request(project_id, pm_name, pd_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Simpan pengajuan PM ke tabel `pm_requests`
        query = """
        INSERT INTO pm_requests (project_id, pm_name, pd_name, status)
        VALUES (%s, %s, %s, 'Pending')
        """
        cursor.execute(query, (project_id, pm_name, pd_name))
        conn.commit()
        print(f"Pengajuan PM {pm_name} untuk proyek {project_id} berhasil disimpan.")
    except Exception as e:
        print(f"Error submitting PM request: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_pm_requests():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil semua pengajuan PM dari tabel `pm_requests`
        query = """
        SELECT id, project_id, pm_name, pd_name, status, created_at
        FROM pm_requests
        WHERE status = 'Pending'
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        requests = cursor.fetchall()
        return requests
    except Exception as e:
        print(f"Error fetching PM requests: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def approve_pm_request(request_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Ambil detail pengajuan dari tabel `pm_requests`
        cursor.execute("""
            SELECT project_id, pm_name FROM pm_requests WHERE id = %s
        """, (request_id,))
        request = cursor.fetchone()

        if not request:
            raise ValueError("Pengajuan tidak ditemukan.")

        project_id, pm_name = request

        # Cari ID PM berdasarkan nama
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'PM'", (pm_name,))
        pm_id = cursor.fetchone()

        if not pm_id:
            raise ValueError("PM tidak ditemukan.")

        # Update PM di tabel `projects`
        cursor.execute("""
            UPDATE projects
            SET pm_id = %s
            WHERE id = %s
        """, (pm_id[0], project_id))

        # Update status pengajuan di tabel `pm_requests`
        cursor.execute("""
            UPDATE pm_requests
            SET status = 'Approved'
            WHERE id = %s
        """, (request_id,))

        conn.commit()
        print(f"Pengajuan {request_id} disetujui, dan PM {pm_name} ditambahkan ke proyek {project_id}.")
    except Exception as e:
        print(f"Error approving PM request: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def reject_pm_request_with_message(request_id, message):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Update status pengajuan menjadi 'Rejected' dan simpan pesan penolakan
        query = """
        UPDATE pm_requests
        SET status = 'Rejected', rejection_message = %s
        WHERE id = %s
        """
        cursor.execute(query, (message, request_id))
        conn.commit()
        print(f"Permintaan {request_id} telah ditolak dengan pesan: {message}")
    except Exception as e:
        print(f"Error rejecting PM request with message: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_pm_requests_by_pd(pd_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT id, project_id, pm_name, status, rejection_message, created_at
        FROM pm_requests
        WHERE pd_name = %s
        ORDER BY created_at DESC
        """
        cursor.execute(query, (pd_name,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching PM requests for PD '{pd_name}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()