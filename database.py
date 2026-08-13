"""SQLite setup for storing job applications."""

import sqlite3


DATABASE_NAME = "job_applications.db"


def initialize_database(database_name=DATABASE_NAME):
    """Create the applications table if it does not already exist."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    # This basic table can be expanded as the tracker gains new features.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied'
        )
        """
    )

    connection.commit()
    connection.close()


def add_application(company, position, status, database_name=DATABASE_NAME):
    """Add one job application to the applications table."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO applications (company, position, status) VALUES (?, ?, ?)",
        (company, position, status),
    )

    connection.commit()
    connection.close()


def update_application_status(application_id, new_status, database_name=DATABASE_NAME):
    """Update the status of one saved application."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE applications SET status = ? WHERE id = ?",
        (new_status, application_id),
    )

    connection.commit()
    connection.close()


def delete_application(application_id, database_name=DATABASE_NAME):
    """Delete one saved application using its database ID."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM applications WHERE id = ?", (application_id,))

    connection.commit()
    connection.close()


def get_applications_with_ids(database_name=DATABASE_NAME):
    """Return every saved application, including its database ID."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, company, position, status FROM applications ORDER BY id"
    )
    applications = cursor.fetchall()

    connection.close()
    return applications


def get_all_applications(database_name=DATABASE_NAME):
    """Return every saved application from the applications table."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT company, position, status FROM applications ORDER BY id"
    )
    applications = cursor.fetchall()

    connection.close()
    return applications


def get_applications_by_status(status, database_name=DATABASE_NAME):
    """Return applications that match a status, or every application for All."""
    if status == "All":
        return get_all_applications(database_name)

    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT company, position, status
        FROM applications
        WHERE status = ?
        ORDER BY id
        """,
        (status,),
    )
    applications = cursor.fetchall()

    connection.close()
    return applications


def search_applications(search_text, status="All", database_name=DATABASE_NAME):
    """Search company and position names, optionally filtering by status."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    # The percent signs allow the search text to appear anywhere in either name.
    search_pattern = f"%{search_text.strip()}%"

    if status == "All":
        cursor.execute(
            """
            SELECT company, position, status
            FROM applications
            WHERE company LIKE ? COLLATE NOCASE
               OR position LIKE ? COLLATE NOCASE
            ORDER BY id
            """,
            (search_pattern, search_pattern),
        )
    else:
        cursor.execute(
            """
            SELECT company, position, status
            FROM applications
            WHERE status = ?
              AND (company LIKE ? COLLATE NOCASE
                   OR position LIKE ? COLLATE NOCASE)
            ORDER BY id
            """,
            (status, search_pattern, search_pattern),
        )

    applications = cursor.fetchall()
    connection.close()
    return applications
