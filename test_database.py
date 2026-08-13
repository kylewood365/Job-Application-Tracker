"""Tests for the Job Application Tracker database functions."""

import os
import tempfile
import unittest

from database import (
    add_application,
    delete_application,
    get_applications_with_ids,
    get_all_applications,
    initialize_database,
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

    def test_get_all_applications_returns_an_empty_list_at_first(self):
        self.assertEqual(get_all_applications(self.database_name), [])

    def test_get_all_applications_returns_saved_applications(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)

        applications = get_all_applications(self.database_name)

        self.assertEqual(
            applications,
            [
                ("Example Company", "Developer", "Applied"),
                ("Another Company", "Designer", "Interview"),
            ],
        )

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
                ("Example Company", "Developer", "Interview"),
                ("Another Company", "Designer", "Applied"),
            ],
        )

    def test_delete_application_deletes_only_the_selected_application(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)
        first_application_id = get_applications_with_ids(self.database_name)[0][0]

        delete_application(first_application_id, self.database_name)

        self.assertEqual(
            get_all_applications(self.database_name),
            [("Another Company", "Designer", "Interview")],
        )

    def test_delete_application_ignores_an_unknown_id(self):
        add_application("Example Company", "Developer", "Applied", self.database_name)

        delete_application(999, self.database_name)

        self.assertEqual(
            get_all_applications(self.database_name),
            [("Example Company", "Developer", "Applied")],
        )


if __name__ == "__main__":
    unittest.main()
