from db.connection import get_connection

def save_project(name):
    """
    Menyimpan nama proyek ke tabel lokasi_project di MySQL.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if not name.strip():  # Validasi input kosong
            raise ValueError("Nama proyek tidak boleh kosong.")
        
        # Eksekusi query INSERT
        query = "INSERT INTO lokasi_project (name) VALUES (%s)"
        cursor.execute(query, (name,))
        conn.commit()  # Commit transaksi
        return True
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan proyek: {e}")  # Log error
        conn.rollback()  # Rollback jika ada kesalahan
        return False
    finally:
        cursor.close()
        conn.close()

def save_kelola_project(
    project_id, pd_id, pm_id, anggaran_mandays, start_date,
    end_date, project_type, nilai_kontrak, roi_percent, roi_idr, lokasi_id
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO kelola_project (
            id, pd, pm, anggaran_mandays, start_date, end_date,
            project_type, nilai_kontrak, roi_percent, roi_idr, lokasi_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            project_id, pd_id, pm_id, anggaran_mandays, start_date,
            end_date, project_type, nilai_kontrak, roi_percent, roi_idr, lokasi_id
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan proyek: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_projects():
    """
    Mengambil semua data dari tabel lokasi_project di MySQL.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM lokasi_project ORDER BY id ASC"
        cursor.execute(query)
        projects = cursor.fetchall()  # Ambil semua data hasil query
        return projects
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data proyek: {e}")
        return []  # Jika error, kembalikan daftar kosong
    finally:
        cursor.close()
        conn.close()

def get_projects_by_role(role_id):
    """
    Mengambil data proyek berdasarkan role ID.

    Parameters:
    - role_id (int): ID role untuk menyaring data.

    Returns:
    - list: Daftar proyek dari tabel lokasi_project sesuai dengan role ID.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if role_id == 14:  # Role 14 untuk DIR OPERASIONAL
            query = "SELECT * FROM lokasi_project ORDER BY id ASC"
            cursor.execute(query)
        else:
            # Role lain tidak memiliki akses ke proyek
            raise ValueError(f"Role '{role_id}' tidak memiliki akses ke data proyek.")

        projects = cursor.fetchall()  # Ambil semua data hasil query
        return projects
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data proyek untuk role '{role_id}': {e}")
        return []  # Kembalikan daftar kosong jika terjadi error
    finally:
        cursor.close()
        conn.close()

def get_all_locations():
    """
    Mengambil semua lokasi training dari tabel lokasi_project
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, name FROM lokasi_project ORDER BY name ASC"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data lokasi: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_project_types_by_location(location_id):
    """
    Mengambil project type dan ID dari tabel kelola_project berdasarkan pd (lokasi_id).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT id, project_type 
        FROM kelola_project 
        WHERE pd = %s AND project_type IS NOT NULL
        """
        cursor.execute(query, (location_id,))
        results = cursor.fetchall()
        
        # Format: [(id, "project_type ID"), ...]
        return [(row['id'], f"{row['project_type']} {row['id']}") for row in results] if results else []
    except Exception as e:
        print(f"[ERROR] Gagal mengambil project type: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_last_project_id(project_type_code):
    """
    Mengambil ID terakhir berdasarkan tipe proyek dan menghasilkan ID baru.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Query untuk mengambil ID terakhir berdasarkan tipe proyek
        query = f"SELECT id FROM kelola_project WHERE id LIKE '{project_type_code}%' ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        last_id = cursor.fetchone()

        # Jika ada hasil, ambil angka setelah prefix (contoh: 'PE01' -> 1)
        if last_id:
            return int(last_id[0][2:]) + 1
        else:
            return 1  # Jika belum ada, mulai dari 1
    except Exception as e:
        print(f"[ERROR] Gagal mengambil ID terakhir: {e}")
        return 1
    finally:
        cursor.close()
        conn.close()

def generate_project_id(project_type):
    """
    Menghasilkan ID proyek berdasarkan tipe proyek.
    """
    # Tentukan prefix ID berdasarkan tipe proyek
    if project_type == "Pendampingan":
        project_type_code = "PE"
    elif project_type == "Semi-Pendampingan":
        project_type_code = "SM"
    elif project_type == "Mentoring":
        project_type_code = "MT"
    elif project_type == "Prepetuation":
        project_type_code = "PP"
    else:
        raise ValueError("Tipe proyek tidak valid.")

    # Ambil ID terakhir untuk tipe proyek tertentu
    last_id = get_last_project_id(project_type_code)

    # Format ID baru (contoh: PE01, SM02, MT03, PP04)
    return f"{project_type_code}{last_id:02d}"

def get_all_roles(role_id):
    """
    Mengambil daftar pengguna berdasarkan role ID dari tabel employees.

    Parameters:
    - role_id (int): ID role untuk menyaring pengguna.

    Returns:
    - list: Daftar pengguna dengan role tertentu.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Gunakan dictionary=True untuk mengembalikan data sebagai dict
    try:
        query = """
        SELECT id, employees_name AS name
        FROM employees
        WHERE position_id = %s
        ORDER BY employees_name ASC
        """
        cursor.execute(query, (role_id,))
        roles = cursor.fetchall()
        return roles
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data roles: {e}")
        return []  # Kembalikan daftar kosong jika terjadi error
    finally:
        cursor.close()
        conn.close()

def get_project_managers():
    """
    Mengambil daftar karyawan dengan posisi PROJECT MANAGER dari tabel employees.
    
    Returns:
    - list: Daftar project manager dengan informasi id dan nama
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, name FROM employees WHERE position = 'PROJECT MANAGER' ORDER BY name ASC"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data project manager: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_projects_by_location(location_id):
    """
    Mengambil proyek berdasarkan lokasi (lokasi_id).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT id
        FROM kelola_project
        WHERE lokasi_id = %s
        """
        cursor.execute(query, (location_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] Gagal mengambil proyek untuk lokasi {location_id}: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_kelola_project():
    """
    Mengambil semua data training dari lokasi_project dan project_type dari kelola_project
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT 
            lp.id as project_id,
            lp.name as project_name,
            kp.project_type,
            kp.pd,
            kp.pm,
            kp.anggaran_mandays,
            kp.start_date,
            kp.end_date,
            kp.nilai_kontrak,
            kp.roi_percent,
            kp.roi_idr
        FROM lokasi_project lp
        LEFT JOIN kelola_project kp ON lp.id = kp.id
        ORDER BY lp.name ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data kelola project: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_training_with_project_types():
    """
    Mengambil daftar training beserta project type dari tabel kelola_project dan lokasi_project.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT DISTINCT lp.id, lp.name, kp.project_type 
        FROM lokasi_project lp
        LEFT JOIN kelola_project kp ON lp.id = kp.pd
        WHERE kp.project_type IS NOT NULL
        ORDER BY lp.name ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data training dengan project type: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def is_project_name_exists(project_name):
    """
    Memeriksa apakah nama proyek sudah ada di tabel lokasi_project.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT COUNT(*) AS count FROM lokasi_project WHERE name = %s"
        cursor.execute(query, (project_name,))
        result = cursor.fetchone()
        return result['count'] > 0  # True jika proyek sudah ada
    except Exception as e:
        print(f"[ERROR] Gagal memeriksa nama proyek: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_locations():
    """
    Mengambil semua data dari tabel lokasi_project.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, name FROM lokasi_project ORDER BY id ASC"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] Gagal mengambil data lokasi_project: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_projects_by_pd(pd_id):
    """
    Mengambil proyek berdasarkan Project Director ID (pd_id).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT * FROM kelola_project WHERE pd = %s
        """
        cursor.execute(query, (pd_id,))
        projects = cursor.fetchall()
        print("Projects found:", projects)  # Debug log
        return projects
    except Exception as e:
        print(f"[ERROR] Gagal mengambil proyek untuk PD: {e}")
        return []
    finally:
        cursor.close()
        conn.close()