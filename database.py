"""Database helpers for SQLite locally and Neon PostgreSQL in production."""

import os
import sqlite3
from contextlib import contextmanager


DATABASE_NAME = "job_applications.db"
APPLICATION_STATUSES = ["Applied", "Interview", "Offer", "Rejected"]


def get_database_backend(database_name=DATABASE_NAME):
    """Return the backend selected for this database operation.

    Passing a different database filename is how the automated tests use their
    own temporary SQLite database. Normal application calls use PostgreSQL when
    DATABASE_URL is configured and otherwise keep using the local SQLite file.
    """
    if database_name == DATABASE_NAME and os.environ.get("DATABASE_URL"):
        return "postgresql"
    return "sqlite"


@contextmanager
def _connect(database_name=DATABASE_NAME):
    """Open and reliably close a connection to the selected database."""
    if get_database_backend(database_name) == "postgresql":
        # Imported only when PostgreSQL is selected, so local SQLite-only tools
        # and tests do not need database credentials or a running server.
        import psycopg

        connection = psycopg.connect(os.environ["DATABASE_URL"])
    else:
        connection = sqlite3.connect(database_name)

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _placeholder(database_name):
    """Return the parameter marker expected by the selected database driver."""
    return "%s" if get_database_backend(database_name) == "postgresql" else "?"


def initialize_database(database_name=DATABASE_NAME):
    """Create the applications table and safely add fields from newer versions."""
    postgresql = get_database_backend(database_name) == "postgresql"
    id_definition = "BIGSERIAL PRIMARY KEY" if postgresql else "INTEGER PRIMARY KEY AUTOINCREMENT"

    with _connect(database_name) as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS applications (
                id {id_definition},
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied',
                date_applied TEXT,
                interview_date TEXT,
                salary TEXT,
                notes TEXT
            )
            """
        )

        if postgresql:
            # These statements also upgrade a Neon table made by an older app.
            for column_name in ("date_applied", "interview_date", "salary", "notes"):
                cursor.execute(
                    f"ALTER TABLE applications ADD COLUMN IF NOT EXISTS {column_name} TEXT"
                )
        else:
            # SQLite does not support ADD COLUMN IF NOT EXISTS on older versions.
            cursor.execute("PRAGMA table_info(applications)")
            existing_columns = {column[1] for column in cursor.fetchall()}
            for column_name in ("date_applied", "interview_date", "salary", "notes"):
                if column_name not in existing_columns:
                    cursor.execute(
                        f"ALTER TABLE applications ADD COLUMN {column_name} TEXT"
                    )


def add_application(company, position, status, database_name=DATABASE_NAME,
                    date_applied=None, interview_date=None, salary=None, notes=None):
    """Add one job application to the applications table."""
    marker = _placeholder(database_name)
    markers = ", ".join([marker] * 7)
    with _connect(database_name) as connection:
        connection.execute(
            f"""INSERT INTO applications
                (company, position, status, date_applied, interview_date, salary, notes)
                VALUES ({markers})""",
            (company, position, status, date_applied, interview_date, salary, notes),
        )


def update_application_status(application_id, new_status, database_name=DATABASE_NAME):
    """Update the status of one saved application."""
    marker = _placeholder(database_name)
    with _connect(database_name) as connection:
        connection.execute(
            f"UPDATE applications SET status = {marker} WHERE id = {marker}",
            (new_status, application_id),
        )


def delete_application(application_id, database_name=DATABASE_NAME):
    """Delete one saved application using its database ID."""
    marker = _placeholder(database_name)
    with _connect(database_name) as connection:
        connection.execute(f"DELETE FROM applications WHERE id = {marker}", (application_id,))


def _fetch_all(query, parameters=(), database_name=DATABASE_NAME):
    """Run a read query and return all rows as tuples."""
    with _connect(database_name) as connection:
        cursor = connection.execute(query, parameters)
        return cursor.fetchall()


def get_applications_with_ids(database_name=DATABASE_NAME):
    """Return every saved application, including its database ID."""
    return _fetch_all(
        """SELECT id, company, position, status, date_applied, interview_date,
                  salary, notes FROM applications ORDER BY id""",
        database_name=database_name,
    )


def get_all_applications(database_name=DATABASE_NAME):
    """Return every saved application from the applications table."""
    return _fetch_all(
        """SELECT company, position, status, date_applied, interview_date, salary, notes
           FROM applications ORDER BY id""",
        database_name=database_name,
    )


def get_total_application_count(database_name=DATABASE_NAME):
    """Return the total number of saved applications."""
    return _fetch_all("SELECT COUNT(*) FROM applications", database_name=database_name)[0][0]


def get_application_counts_by_status(database_name=DATABASE_NAME):
    """Return the number of applications saved under each dashboard status."""
    counts = {status: 0 for status in APPLICATION_STATUSES}
    rows = _fetch_all(
        "SELECT status, COUNT(*) FROM applications GROUP BY status",
        database_name=database_name,
    )
    for status, count in rows:
        if status in counts:
            counts[status] = count
    return counts


def get_applications_by_status(status, database_name=DATABASE_NAME):
    """Return applications that match a status, or every application for All."""
    if status == "All":
        return get_all_applications(database_name)
    marker = _placeholder(database_name)
    return _fetch_all(
        f"""SELECT company, position, status, date_applied, interview_date, salary, notes
            FROM applications WHERE status = {marker} ORDER BY id""",
        (status,), database_name,
    )


def search_applications(search_text, status="All", database_name=DATABASE_NAME):
    """Search company, position, and notes case-insensitively, optionally by status."""
    marker = _placeholder(database_name)
    # PostgreSQL's ILIKE and SQLite's NOCASE preserve the same search behavior.
    if get_database_backend(database_name) == "postgresql":
        comparisons = f"company ILIKE {marker} OR position ILIKE {marker} OR notes ILIKE {marker}"
    else:
        comparisons = (
            f"company LIKE {marker} COLLATE NOCASE OR position LIKE {marker} COLLATE NOCASE "
            f"OR notes LIKE {marker} COLLATE NOCASE"
        )

    search_pattern = f"%{search_text.strip()}%"
    parameters = [search_pattern] * 3
    status_clause = ""
    if status != "All":
        status_clause = f"status = {marker} AND "
        parameters.insert(0, status)

    return _fetch_all(
        f"""SELECT company, position, status, date_applied, interview_date, salary, notes
            FROM applications WHERE {status_clause}({comparisons}) ORDER BY id""",
        tuple(parameters), database_name,
    )
