import mysql.connector
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3308,
        user="root",
        password="",
        database="kpix"
    )

def create_projects_table():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                pd INT,
                anggaran_mandays INT NOT NULL,
                start_month INT,
                pm_id INT,
                FOREIGN KEY (pd) REFERENCES users(id),
                FOREIGN KEY (pm_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        print("Table 'projects' has been created (if it did not exist).")
    except Error as e:
        print(f"Error creating table 'projects': {e}")
    finally:
        cursor.close()
        conn.close()

def save_project(project_name, pd_name, anggaran_mandays, start_month):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s", (pd_name,))
        pd_id = cursor.fetchone()

        if pd_id is None:
            raise ValueError("Project Director not found")

        query = """
        INSERT INTO projects (name, pd, anggaran_mandays, start_month)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (project_name, pd_id[0], anggaran_mandays, start_month))
        conn.commit()
        print(f"Project '{project_name}' has been saved.")
    except mysql.connector.Error as err:
        print(f"Error saving project: {err}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def get_pd_users():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM users WHERE role = 'PD'")
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching PD users: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_projects_by_dirops():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.id, p.name, u.name AS pd_name, p.start_month, pm.name AS pm_name
            FROM projects p
            JOIN users u ON p.pd = u.id
            LEFT JOIN users pm ON p.pm_id = pm.id
            WHERE u.role = 'DirOps'
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching projects: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_projects_by_pd(pd_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.id, p.name, u.name AS pd_name, p.start_month, pm.name AS pm_name
            FROM projects p
            JOIN users u ON p.pd = u.id
            LEFT JOIN users pm ON p.pm_id = pm.id
            WHERE u.role = 'PD' AND u.name = %s
        """, (pd_name,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching projects for PD '{pd_name}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_users_by_role(role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM users WHERE role = %s", (role,))
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching users by role '{role}': {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def assign_pm_to_project(project_id, pm_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'PM'", (pm_name,))
        pm_id = cursor.fetchone()

        if pm_id is None:
            raise ValueError("PM not found or user is not a PM")

        cursor.execute("SELECT pm_id FROM projects WHERE id = %s", (project_id,))
        existing_pm = cursor.fetchone()
        if existing_pm and existing_pm[0] is not None:
            raise ValueError("This project already has a PM assigned")

        query = """
        UPDATE projects
        SET pm_id = %s
        WHERE id = %s
        """
        cursor.execute(query, (pm_id[0], project_id))
        conn.commit()
        print(f"PM {pm_name} has been assigned to project ID {project_id}")
    except Error as e:
        print(f"Error assigning PM to project: {e}")
    except ValueError as ve:
        print(ve)
    finally:
        cursor.close()
        conn.close()

def get_project_reimbursement_total(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT SUM(reimbursement_amount) AS total
            FROM budgets
            WHERE project_id = %s
        """, (project_id,))
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Error as e:
        print(f"Error fetching project reimbursement total: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_all_project_reimbursements():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.name, SUM(b.reimbursement_amount) AS total_reimbursement
            FROM projects p
            LEFT JOIN budgets b ON p.id = b.project_id
            GROUP BY p.id
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching all project reimbursements: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
