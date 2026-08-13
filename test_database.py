"""Tests for the Job Application Tracker database functions."""

import os
import tempfile
import unittest

from database import (
    add_application,
    delete_application,
    get_application_counts_by_status,
    get_applications_by_status,
    get_applications_with_ids,
    get_all_applications,
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
                ("Example Company", "Developer", "Applied"),
                ("Another Company", "Designer", "Interview"),
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
                ("Example Company", "Developer", "Applied"),
                ("Third Company", "Engineer", "Applied"),
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
            [("Example Company", "Developer", "Applied")],
        )

    def test_search_finds_position_case_insensitively(self):
        add_application("Example Company", "Software Developer", "Applied", self.database_name)
        add_application("Another Company", "Designer", "Interview", self.database_name)

        applications = search_applications("DEVELOPER", database_name=self.database_name)

        self.assertEqual(
            applications,
            [("Example Company", "Software Developer", "Applied")],
        )

    def test_search_works_with_status_filter(self):
        add_application("First Company", "Developer", "Applied", self.database_name)
        add_application("Second Company", "Developer", "Interview", self.database_name)

        applications = search_applications(
            "developer", "Interview", self.database_name
        )

        self.assertEqual(
            applications,
            [("Second Company", "Developer", "Interview")],
        )

    def test_empty_search_returns_applications_normally(self):
        add_application("First Company", "Developer", "Applied", self.database_name)
        add_application("Second Company", "Designer", "Interview", self.database_name)

        applications = search_applications("", "All", self.database_name)

        self.assertEqual(
            applications,
            [
                ("First Company", "Developer", "Applied"),
                ("Second Company", "Designer", "Interview"),
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
