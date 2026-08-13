"""SQLite setup for storing job applications."""

import sqlite3


DATABASE_NAME = "job_applications.db"
APPLICATION_STATUSES = ["Applied", "Interview", "Offer", "Rejected"]


def initialize_database(database_name=DATABASE_NAME):
    """Create the applications table and add any columns introduced later."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    # This basic table can be expanded as the tracker gains new features.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            date_applied TEXT,
            interview_date TEXT
        )
        """
    )

    # ALTER TABLE keeps rows from databases created by older versions of the app.
    cursor.execute("PRAGMA table_info(applications)")
    existing_columns = {column[1] for column in cursor.fetchall()}
    if "date_applied" not in existing_columns:
        cursor.execute("ALTER TABLE applications ADD COLUMN date_applied TEXT")
    if "interview_date" not in existing_columns:
        cursor.execute("ALTER TABLE applications ADD COLUMN interview_date TEXT")

    connection.commit()
    connection.close()


def add_application(
    company,
    position,
    status,
    database_name=DATABASE_NAME,
    date_applied=None,
    interview_date=None,
):
    """Add one job application to the applications table."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO applications
            (company, position, status, date_applied, interview_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (company, position, status, date_applied, interview_date),
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
        """
        SELECT id, company, position, status, date_applied, interview_date
        FROM applications ORDER BY id
        """
    )
    applications = cursor.fetchall()

    connection.close()
    return applications


def get_all_applications(database_name=DATABASE_NAME):
    """Return every saved application from the applications table."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT company, position, status, date_applied, interview_date
        FROM applications ORDER BY id
        """
    )
    applications = cursor.fetchall()

    connection.close()
    return applications


def get_total_application_count(database_name=DATABASE_NAME):
    """Return the total number of saved applications."""
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    connection.close()
    return total


def get_application_counts_by_status(database_name=DATABASE_NAME):
    """Return the number of applications saved under each dashboard status."""
    counts = {status: 0 for status in APPLICATION_STATUSES}
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT status, COUNT(*) FROM applications GROUP BY status"
    )
    for status, count in cursor.fetchall():
        if status in counts:
            counts[status] = count

    connection.close()
    return counts


def get_applications_by_status(status, database_name=DATABASE_NAME):
    """Return applications that match a status, or every application for All."""
    if status == "All":
        return get_all_applications(database_name)

    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT company, position, status, date_applied, interview_date
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
            SELECT company, position, status, date_applied, interview_date
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
            SELECT company, position, status, date_applied, interview_date
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
