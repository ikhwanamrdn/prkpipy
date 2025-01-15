from binascii import Error
import mysql
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host="localhost",  # Ganti dengan host MySQL Anda
        user="root",       # Ganti dengan user MySQL Anda
        password="",       # Ganti dengan password MySQL Anda
        database="kpix"    # Ganti dengan nama database Anda
    )

# Function to assign ME to a project
def assign_me_to_project(project_id, me_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'ME'", (me_name,))
        me_id = cursor.fetchone()

        if me_id is None:
            raise ValueError(f"Manager Engineer '{me_name}' not found or user is not a Manager Engineer")

        # Check if ME is already assigned to the project
        cursor.execute("""
            SELECT 1 FROM project_me WHERE project_id = %s AND me_id = %s
        """, (project_id, me_id[0]))
        if cursor.fetchone():
            raise ValueError(f"ME {me_name} is already assigned to this project.")

        # Insert into the project_me table to assign the ME to the project
        cursor.execute("""
            INSERT INTO project_me (project_id, me_id)
            VALUES (%s, %s)
        """, (project_id, me_id[0]))
        conn.commit()

        print(f"ME {me_name} has been assigned to project ID {project_id}")
    except Error as e:
        print(f"Error assigning ME to project: {e}")
    except ValueError as ve:
        print(ve)
    finally:
        cursor.close()
        conn.close()

# Function to get the list of MEs assigned to a project
def get_assigned_mes(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.name FROM users u
            JOIN project_me pm ON u.id = pm.me_id
            WHERE pm.project_id = %s
        """, (project_id,))
        assigned_mes = [me[0] for me in cursor.fetchall()]
        return assigned_mes
    except mysql.connector.Error as e:
        st.error(f"Error fetching assigned MEs: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Function to remove ME from project
def remove_me_from_project(project_id, me_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE name = %s AND role = 'ME'", (me_name,))
        me_id = cursor.fetchone()

        if me_id is None:
            raise ValueError(f"Manager Engineer '{me_name}' not found or user is not a Manager Engineer")

        # Remove ME from the project
        cursor.execute("""
            DELETE FROM project_me WHERE project_id = %s AND me_id = %s
        """, (project_id, me_id[0]))
        conn.commit()

        print(f"ME {me_name} has been removed from project ID {project_id}")
    except Error as e:
        print(f"Error removing ME from project: {e}")
    except ValueError as ve:
        print(ve)
    finally:
        cursor.close()
        conn.close()