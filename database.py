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
