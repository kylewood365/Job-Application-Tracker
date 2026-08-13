"""Tests for the Job Application Tracker database functions."""

import os
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from unittest.mock import patch

import database
from database import (
    add_application,
    delete_application,
    get_application_counts_by_status,
    get_applications_by_status,
    get_applications_with_ids,
    get_all_applications,
    get_database_backend,
    get_total_application_count,
    initialize_database,
    search_applications,
    update_application_status,
)


class DatabaseTests(unittest.TestCase):
    """Check that applications can be saved and retrieved."""

    def setUp(self):
        temporary_database = tempfile.NamedTemporaryFile(delete=False)
        self.database_name = temporary_database.name
        temporary_database.close()
        initialize_database(self.database_name)

    def tearDown(self):
        os.remove(self.database_name)

    def test_default_database_uses_sqlite_without_database_url(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_database_backend(), "sqlite")

    def test_default_database_uses_postgresql_with_database_url(self):
        # Selection can be tested with a fake URL; no external connection is made.
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://example.invalid/test"},
            clear=True,
        ):
            self.assertEqual(get_database_backend(), "postgresql")

    def test_explicit_test_database_stays_on_sqlite_with_database_url(self):
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://example.invalid/test"},
            clear=True,
        ):
            self.assertEqual(get_database_backend(self.database_name), "sqlite")
            self.assertEqual(get_all_applications(self.database_name), [])

    def test_postgresql_initialization_locks_schema_changes_in_one_transaction(self):
        executed_statements = []

        class RecordingCursor:
            def execute(self, statement, parameters=None):
                executed_statements.append((" ".join(statement.split()), parameters))

            def fetchall(self):
                return []

        class RecordingConnection:
            def cursor(self):
                return RecordingCursor()

        @contextmanager
        def recording_connection(_database_name):
            yield RecordingConnection()

        with patch.object(database, "get_database_backend", return_value="postgresql"), patch.object(
            database, "_connect", recording_connection
        ):
            initialize_database()

        self.assertEqual(
            executed_statements[0],
            (
                "SELECT pg_advisory_xact_lock(%s)",
                (database.POSTGRESQL_SCHEMA_LOCK_KEY,),
            ),
        )
        self.assertTrue(executed_statements[1][0].startswith("CREATE TABLE IF NOT EXISTS"))
        self.assertEqual(len(executed_statements), 6)

        executed_statements.clear()
        with patch.object(database, "get_database_backend", return_value="sqlite"), patch.object(
            database, "_connect", recording_connection
        ):
            initialize_database(self.database_name)

        self.assertFalse(
            any("pg_advisory_xact_lock" in statement for statement, _ in executed_statements)
        )

    def test_get_all_applications_returns_an_empty_list_at_first(self):
        self.assertEqual(get_all_applications(self.database_name), [])

    def test_get_all_applications_returns_saved_applications(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)

        applications = get_all_applications(self.database_name)

        self.assertEqual(
            applications,
            [
                (
                    "Example Company", "Developer", "Applied", None, None, None, None
                ),
                (
                    "Another Company", "Designer", "Interview", None, None, None, None
                ),
            ],
        )

    def test_dashboard_counts_are_zero_when_there_are_no_applications(self):
        self.assertEqual(get_total_application_count(self.database_name), 0)
        self.assertEqual(
            get_application_counts_by_status(self.database_name),
            {"Applied": 0, "Interview": 0, "Offer": 0, "Rejected": 0},
        )

    def test_dashboard_counts_saved_applications_by_status(self):
        add_application("First Company", "Developer", "Applied", self.database_name)
        add_application("Second Company", "Designer", "Applied", self.database_name)
        add_application("Third Company", "Engineer", "Interview", self.database_name)
        add_application("Fourth Company", "Manager", "Offer", self.database_name)
        add_application("Fifth Company", "Writer", "Rejected", self.database_name)

        self.assertEqual(get_total_application_count(self.database_name), 5)
        self.assertEqual(
            get_application_counts_by_status(self.database_name),
            {"Applied": 2, "Interview": 1, "Offer": 1, "Rejected": 1},
        )

    def test_filter_all_returns_every_application(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)

        applications = get_applications_by_status("All", self.database_name)

        self.assertEqual(
            applications,
            [
                ("Example Company", "Developer", "Applied", None, None, None, None),
                ("Another Company", "Designer", "Interview", None, None, None, None),
            ],
        )

    def test_filter_status_returns_only_matching_applications(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)
        add_application("Third Company", "Engineer", "Applied", self.database_name)

        applications = get_applications_by_status("Applied", self.database_name)

        self.assertEqual(
            applications,
            [
                ("Example Company", "Developer", "Applied", None, None, None, None),
                ("Third Company", "Engineer", "Applied", None, None, None, None),
            ],
        )

    def test_filter_status_returns_an_empty_list_when_nothing_matches(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)

        applications = get_applications_by_status("Offer", self.database_name)

        self.assertEqual(applications, [])

    def test_search_finds_company_name_case_insensitively(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)

        applications = search_applications("eXaMpLe", database_name=self.database_name)

        self.assertEqual(
            applications,
            [("Example Company", "Developer", "Applied", None, None, None, None)],
        )

    def test_search_finds_position_case_insensitively(self):
        add_application("Example Company", "Software Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)

        applications = search_applications("DEVELOPER", database_name=self.database_name)

        self.assertEqual(
            applications,
            [
                (
                    "Example Company",
                    "Software Developer",
                    "Applied",
                    None,
                    None,
                    None,
                    None,
                )
            ],
        )

    def test_search_works_with_status_filter(self):
        add_application("First Company", "Developer", "Applied", self.database_name)
        add_application("Second Company", "Developer", "Interview", self.database_name)

        applications = search_applications(
            "developer", "Interview", self.database_name
        )

        self.assertEqual(
            applications,
            [("Second Company", "Developer", "Interview", None, None, None, None)],
        )

    def test_empty_search_returns_applications_normally(self):
        add_application("First Company", "Developer", "Applied", self.database_name)
        add_application("Second Company", "Designer", "Interview", self.database_name)

        applications = search_applications("", "All", self.database_name)

        self.assertEqual(
            applications,
            [
                ("First Company", "Developer", "Applied", None, None, None, None),
                ("Second Company", "Designer", "Interview", None, None, None, None),
            ],
        )

    def test_search_returns_an_empty_list_when_nothing_matches(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)

        applications = search_applications("accountant", database_name=self.database_name)

        self.assertEqual(applications, [])

    def test_update_application_status_updates_the_selected_application(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Applied", self.database_name)
        first_application_id = get_applications_with_ids(self.database_name)[0][0]

        update_application_status(
            first_application_id, "Interview", self.database_name
        )

        self.assertEqual(
            get_all_applications(self.database_name),
            [
                ("Example Company", "Developer", "Interview", None, None, None, None),
                ("Another Company", "Designer", "Applied", None, None, None, None),
            ],
        )

    def test_delete_application_deletes_only_the_selected_application(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)
        first_application_id = get_applications_with_ids(self.database_name)[0][0]

        delete_application(first_application_id, self.database_name)

        self.assertEqual(
            get_all_applications(self.database_name),
            [("Another Company", "Designer", "Interview", None, None, None, None)],
        )

    def test_delete_application_ignores_an_unknown_id(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)

        delete_application(999, self.database_name)

        self.assertEqual(
            get_all_applications(self.database_name),
            [("Example Company", "Developer", "Applied", None, None, None, None)],
        )

    def test_date_applied_and_interview_date_are_saved(self):
        add_application(
            "Example Company",
            "Developer",
            "Interview",
            self.database_name,
            date_applied="2026-08-01",
            interview_date="2026-08-15",
        )

        self.assertEqual(
            get_all_applications(self.database_name),
            [
                (
                    "Example Company",
                    "Developer",
                    "Interview",
                    "2026-08-01",
                    "2026-08-15",
                    None,
                    None,
                )
            ],
        )

    def test_interview_date_can_be_empty(self):
        add_application(
            "Example Company",
            "Developer",
            "Applied",
            self.database_name,
            date_applied="2026-08-01",
        )

        self.assertEqual(
            get_all_applications(self.database_name),
            [
                (
                    "Example Company",
                    "Developer",
                    "Applied",
                    "2026-08-01",
                    None,
                    None,
                    None,
                )
            ],
        )

    def test_salary_and_notes_are_saved(self):
        add_application(
            "Example Company",
            "Developer",
            "Applied",
            self.database_name,
            salary="$80,000",
            notes="Ask about remote work.",
        )

        self.assertEqual(
            get_all_applications(self.database_name),
            [
                (
                    "Example Company",
                    "Developer",
                    "Applied",
                    None,
                    None,
                    "$80,000",
                    "Ask about remote work.",
                )
            ],
        )

    def test_salary_and_notes_can_be_empty(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)

        self.assertEqual(
            get_all_applications(self.database_name),
            [("Example Company", "Developer", "Applied", None, None, None, None)],
        )

    def test_search_finds_text_in_notes_and_respects_status_filter(self):
        add_application(
            "First Company",
            "Developer",
            "Applied",
            self.database_name,
            notes="Referral from Taylor",
        )
        add_application(
            "Second Company",
            "Designer",
            "Interview",
            self.database_name,
            notes="TAYLOR will join the interview",
        )

        applications = search_applications(
            "taylor", "Interview", self.database_name
        )

        self.assertEqual(
            applications,
            [
                (
                    "Second Company",
                    "Designer",
                    "Interview",
                    None,
                    None,
                    None,
                    "TAYLOR will join the interview",
                )
            ],
        )

    def test_initialize_database_migrates_an_existing_database_safely(self):
        os.remove(self.database_name)
        connection = sqlite3.connect(self.database_name)
        connection.execute(
            """
            CREATE TABLE applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied'
            )
            """
        )
        connection.execute(
            "INSERT INTO applications (company, position, status) VALUES (?, ?, ?)",
            ("Saved Company", "Engineer", "Applied"),
        )
        connection.commit()
        connection.close()

        initialize_database(self.database_name)

        self.assertEqual(
            get_all_applications(self.database_name),
            [("Saved Company", "Engineer", "Applied", None, None, None, None)],
        )
        connection = sqlite3.connect(self.database_name)
        table_information = connection.execute("PRAGMA table_info(applications)")
        columns = {column[1] for column in table_information}
        connection.close()
        self.assertIn("salary", columns)
        self.assertIn("notes", columns)


if __name__ == "__main__":
    unittest.main()
