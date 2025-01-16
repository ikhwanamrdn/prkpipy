import mysql.connector
from datetime import datetime
import json

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3308,
        user="root",
        password="",
        database="kpix"
    )

def create_reimbust_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS reimbust (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                reimbursement_amount DECIMAL(15,2) NOT NULL,
                date_created DATE NOT NULL,
                jenis_reimbust VARCHAR(255),
                rincian_kegiatan TEXT,
                nama_penjual VARCHAR(255),
                keterangan_penjual TEXT,
                file_path TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)
        conn.commit()
        print("Table 'reimbust' created successfully (if not already present).")
    except mysql.connector.Error as err:
        print(f"Error creating reimbust table: {err}")
    finally:
        cursor.close()
        conn.close()

def save_reimbursement(project_id, amount, jenis_reimbust, rincian_kegiatan, nama_penjual, keterangan_penjual, saved_files):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO reimbust (project_id, reimbursement_amount, date_created, jenis_reimbust, rincian_kegiatan, nama_penjual, keterangan_penjual, file_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Store file paths as a JSON array directly
        file_paths = json.dumps(saved_files) if saved_files else json.dumps([])
        cursor.execute(query, (project_id, amount, datetime.now().date(), jenis_reimbust, rincian_kegiatan, nama_penjual, keterangan_penjual, file_paths))
        conn.commit()
        print(f"Reimbursement of {amount} saved for project {project_id} with details: {jenis_reimbust}, {rincian_kegiatan}, {nama_penjual}, {keterangan_penjual}")
    except mysql.connector.Error as err:
        print(f"Error saving reimbursement: {err}")
    finally:
        cursor.close()
        conn.close()

def get_total_reimbust():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(""" 
            SELECT SUM(reimbursement_amount) AS total_reimbust
            FROM reimbust
        """)
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except mysql.connector.Error as err:
        print(f"Error calculating total reimbust: {err}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_project_reimbursements(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(""" 
            SELECT reimbursement_amount, date_created, jenis_reimbust, rincian_kegiatan, nama_penjual, keterangan_penjual, file_path
            FROM reimbust
            WHERE project_id = %s
            ORDER BY date_created DESC
        """, (project_id,))
        results = cursor.fetchall()

        # Create a new list to hold modified results
        modified_results = []
        for result in results:
            file_paths = json.loads(result[6]) if result[6] and result[6] != 'null' else []  # Parse JSON file paths
            modified_results.append(list(result[:6]) + [file_paths])  # Convert tuple to list and add file_paths

        return modified_results
    except mysql.connector.Error as err:
        print(f"Error fetching reimbursements: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_all_project_reimbursements():
    conn = get_connection()
    cursor = conn.cursor()
    all_reimbursements = []

    try:
        projects = get_project_details()

        for project in projects:
            project_id = project[0]
            project_name = project[1]
            reimbursements = get_project_reimbursements(project_id)
            all_reimbursements.append((project_id, project_name, reimbursements))

        print("All Project Reimbursements Retrieved:", all_reimbursements)
        return all_reimbursements
    except mysql.connector.Error as err:
        print(f"Error fetching all project reimbursements: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_project_details():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(""" 
            SELECT p.id, p.name, p.pm_id, 
                   COALESCE(SUM(r.reimbursement_amount), 0) AS total_funds
            FROM projects p
            LEFT JOIN reimbust r ON p.id = r.project_id
            GROUP BY p.id, p.name, p.pm_id
            ORDER BY p.name
        """)
        projects = cursor.fetchall()
        print("Projects:", projects)
        return projects
    except mysql.connector.Error as err:
        print(f"Error fetching project details: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_reimbust_data():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(""" 
            SELECT r.id, p.name AS project_name, r.reimbursement_amount, r.date_created, r.jenis_reimbust,
                   r.rincian_kegiatan, r.nama_penjual, r.keterangan_penjual, r.file_path
            FROM reimbust r
            JOIN projects p ON r.project_id = p.id
            ORDER BY r.date_created DESC
        """)
        reimbusts = cursor.fetchall()

        reimbust_data = []
        for reimbust in reimbusts:
            project_name = reimbust[1]
            reimbursement_amount = f"Rp {reimbust[2]:,.2f}"
            date_created = reimbust[3]
            jenis_reimbust = reimbust[4] if reimbust[4] else "Tidak ada jenis"
            rincian_kegiatan = reimbust[5] if reimbust[5] else "Tidak ada rincian"
            nama_penjual = reimbust[6] if reimbust[6] else "Tidak ada penjual"
            keterangan_penjual = reimbust[7] if reimbust[7] else "Tidak ada keterangan"
            file_paths = json.loads(reimbust[8]) if reimbust[8] else []  # Parse JSON file paths
            reimbust_data.append([project_name, reimbursement_amount, date_created, jenis_reimbust, rincian_kegiatan, nama_penjual, keterangan_penjual, file_paths])

        return reimbust_data
    except mysql.connector.Error as err:
        print(f"Error fetching reimbust data: {err}")
        return []
    finally:
        cursor.close()
        conn.close()
