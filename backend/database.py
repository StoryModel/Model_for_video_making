import sqlite3
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_title TEXT,
        style_reference_path TEXT,
        main_character_name TEXT,
        character_description TEXT,
        character_image_path TEXT,
        story_file_path TEXT,
        style_prompt TEXT,
        last_scene_number INTEGER DEFAULT 0,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        project_status TEXT DEFAULT 'active'
    );
    """)

    conn.commit()
    conn.close()


def create_project(
    story_title,
    main_character_name=None,
    character_image_path=None,
    story_file_path=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO projects (
        story_title,
        main_character_name,
        character_image_path,
        story_file_path
    )
    VALUES (?, ?, ?, ?)
    """, (
        story_title,
        main_character_name,
        character_image_path,
        story_file_path
    ))

    conn.commit()

    project_id = cursor.lastrowid

    conn.close()

    return project_id


def get_all_projects():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM projects
    WHERE project_status != 'deleted'
    ORDER BY created_date DESC
    """)

    projects = cursor.fetchall()

    conn.close()

    return [dict(project) for project in projects]


def get_project(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM projects
    WHERE project_id = ?
    """, (project_id,))

    project = cursor.fetchone()

    conn.close()

    if project:
        return dict(project)

    return None


def update_project_scene(project_id, last_scene_number):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE projects
    SET last_scene_number = ?,
        updated_date = CURRENT_TIMESTAMP
    WHERE project_id = ?
    """, (
        last_scene_number,
        project_id
    ))

    conn.commit()
    conn.close()


def update_character_description(project_id, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE projects
    SET character_description = ?,
        updated_date = CURRENT_TIMESTAMP
    WHERE project_id = ?
    """, (
        description,
        project_id
    ))

    conn.commit()
    conn.close()


def delete_project(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE projects
    SET project_status = 'deleted',
        updated_date = CURRENT_TIMESTAMP
    WHERE project_id = ?
    """, (project_id,))

    conn.commit()
    conn.close()