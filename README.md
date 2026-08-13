# Job Application Tracker

A lightweight web application for organizing a job search in one place. The
tracker lets you record opportunities, follow each application through the
hiring process, and quickly find the information you need. Data is stored in a
local SQLite database during development, or a hosted Neon PostgreSQL database
in production, and presented through a Streamlit interface.

## Live Demo

Try the [live Job Application Tracker](https://job-application-tracker-ehfmedyijdzmb3kznb9arp.streamlit.app)
to explore the application in your browser.

## Features

- Add applications with a company, position, status, application date,
  optional interview date, salary, and notes.
- View dashboard totals for all applications and for each supported status:
  Applied, Interview, Offer, and Rejected.
- Search applications by company, position, or notes.
- Filter saved applications by status.
- Update an application's status.
- Delete applications after confirming the action.
- Store application data in SQLite locally or Neon PostgreSQL in production.

## Technologies Used

- **Python** provides the application and database logic.
- **Streamlit** supplies the interactive web interface and runs the app without
  a separate frontend framework.
- **SQLite** stores application records in a local `job_applications.db` file.
  SQLite is built into Python, so no separate database server is required.
- **Neon PostgreSQL** provides persistent production storage when a
  `DATABASE_URL` environment variable is configured. Psycopg connects the app
  to PostgreSQL.
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

## Use Neon in Production

The database backend is selected automatically:

- When `DATABASE_URL` is set, the app connects to Neon PostgreSQL with Psycopg.
- When `DATABASE_URL` is not set, the app continues to use
  `job_applications.db` with SQLite. This is also how the automated tests run
  without external credentials.

Create a Neon project, copy its PostgreSQL connection string, and configure it
as the `DATABASE_URL` secret in your hosting provider. For example, in a shell
you can set it before starting Streamlit:

```bash
export DATABASE_URL="your-Neon-connection-string"
streamlit run app.py
```

Never commit the real value. `.env` files are ignored by Git because they can
contain secrets. The app creates the `applications` table in Neon automatically
on startup if it does not already exist.

## CRUD Operations

CRUD describes the four basic operations used to manage stored data:

- **Create:** the add-application form inserts a new application into the
  selected database.
- **Read:** the dashboard, saved-application list, search, and status filter
  retrieve application records.
- **Update:** the status control changes the selected application's progress.
- **Delete:** the delete control permanently removes a confirmed application.

Together, these operations cover the complete lifecycle of an application
record without requiring users to work with the database directly.

## Deployment Notes

The app is deployed on Streamlit Community Cloud with `app.py` as the entry
point. `requirements.txt` supplies the required Streamlit package. The deployed
app uses Neon PostgreSQL for persistent cloud storage through its configured
`DATABASE_URL` secret.

SQLite is well suited to local development and automated tests. Local SQLite
storage on Streamlit Community Cloud is **not guaranteed to persist**. For other
deployments, set the hosted app's `DATABASE_URL` secret to a Neon connection
string for durable production data. If the secret is absent, the SQLite
fallback remains active.

## Future Improvements

Potential follow-up work includes:

- Add authentication so each user has a private set of applications.
- Add more reporting and visualizations for job-search trends.
- Export and import application data in common formats such as CSV.
- Add reminders for interviews and follow-up dates.
- Expand automated coverage to include Streamlit interface behavior.

These are ideas for future development and are not part of the current app.
