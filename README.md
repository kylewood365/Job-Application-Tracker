# Job Application Tracker

A lightweight web application for organizing a job search in one place. The
tracker lets you record opportunities, follow each application through the
hiring process, and quickly find the information you need. Data is stored in a
local SQLite database and presented through a Streamlit interface.

## Features

- Add applications with a company, position, status, application date,
  optional interview date, salary, and notes.
- View dashboard totals for all applications and for each supported status:
  Applied, Interview, Offer, and Rejected.
- Search applications by company, position, or notes.
- Filter saved applications by status.
- Update an application's status.
- Delete applications after confirming the action.
- Keep application data locally in a small SQLite database.

## Technologies Used

- **Python** provides the application and database logic.
- **Streamlit** supplies the interactive web interface and runs the app without
  a separate frontend framework.
- **SQLite** stores application records in a local `job_applications.db` file.
  SQLite is built into Python, so no separate database server is required.
- **Git and GitHub** provide version control, change history, and a place to
  host and collaborate on the source code.

## Run Locally

### Prerequisites

- Python 3.9 or newer
- Git

### Setup

1. Clone the repository and enter its directory:

   ```bash
   git clone <your-repository-url>
   cd Job-Application-Tracker
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell, activate it with:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install the dependency:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown by Streamlit (normally
   `http://localhost:8501`). The database is created automatically on first
   launch.

To run the existing automated tests:

```bash
python -m unittest
```

## Project Structure

```text
Job-Application-Tracker/
├── app.py              # Streamlit page, forms, dashboard, and controls
├── database.py         # SQLite schema and data-access functions
├── test_database.py    # Unit tests for the database operations
├── requirements.txt    # Runtime Python dependency
├── .gitignore          # Files intentionally excluded from Git
└── README.md            # Project documentation
```

The app creates `job_applications.db` at runtime. It is local data, so it is
ignored by Git and does not appear in the project tree above.

## CRUD Operations

CRUD describes the four basic operations used to manage stored data:

- **Create:** the add-application form inserts a new application into SQLite.
- **Read:** the dashboard, saved-application list, search, and status filter
  retrieve application records.
- **Update:** the status control changes the selected application's progress.
- **Delete:** the delete control permanently removes a confirmed application.

Together, these operations cover the complete lifecycle of an application
record without requiring users to work with the database directly.

## Deployment Notes

The repository can be connected to Streamlit Community Cloud with `app.py` as
the entry point. `requirements.txt` supplies the required Streamlit package.

SQLite is well suited to local development and small, single-user projects.
However, local SQLite storage on Streamlit Community Cloud is **not guaranteed
to persist**: app restarts, redeployments, or infrastructure changes can remove
the locally created database. Use an external persistent database or storage
service before relying on the hosted app for durable data.

## Future Improvements

Potential follow-up work includes:

- Use a hosted database for reliable multi-session deployment storage.
- Add authentication so each user has a private set of applications.
- Add more reporting and visualizations for job-search trends.
- Export and import application data in common formats such as CSV.
- Add reminders for interviews and follow-up dates.
- Expand automated coverage to include Streamlit interface behavior.

These are ideas for future development and are not part of the current app.
