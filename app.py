"""The Streamlit web interface for the Job Application Tracker."""

import streamlit as st

from database import (
    add_application,
    delete_application,
    get_application_counts_by_status,
    get_applications_with_ids,
    get_total_application_count,
    initialize_database,
    search_applications,
    update_application_status,
)


STATUSES = ["Applied", "Interview", "Offer", "Rejected"]

# Create the database table before showing the page.
initialize_database()

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide",
)

# A small amount of styling keeps the app polished without hiding Streamlit's
# familiar, beginner-friendly controls.
st.markdown(
    """
    <style>
        .block-container {max-width: 1180px; padding-top: 2.5rem; padding-bottom: 4rem;}
        h1, h2, h3 {letter-spacing: -0.02em;}
        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 0.75rem;
            padding: 1rem 1.1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        div[data-testid="stMetricLabel"] {color: #64748b;}
        div[data-testid="stMetricValue"] {color: #0f172a;}
        div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #e2e8f0;
            border-radius: 0.85rem;
        }
        .section-intro {color: #64748b; margin-top: -0.65rem; margin-bottom: 1.25rem;}
        .application-status {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            font-size: 0.78rem;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💼 Job Application Tracker")
st.markdown(
    '<p class="section-intro">Keep every opportunity organized, from application to offer.</p>',
    unsafe_allow_html=True,
)

st.subheader("Overview")
total_count = get_total_application_count()
status_counts = get_application_counts_by_status()

metric_labels = ["Total", *STATUSES]
metric_values = [total_count, *(status_counts[status] for status in STATUSES)]
for metric_column, label, value in zip(st.columns(5), metric_labels, metric_values):
    metric_column.metric(label, value)

st.divider()

form_column, controls_column = st.columns([1.25, 1], gap="large")

with form_column:
    st.subheader("Add an application")
    st.markdown(
        '<p class="section-intro">Save the role details now. Optional details can be added when useful.</p>',
        unsafe_allow_html=True,
    )

    with st.form("add_application_form", border=True):
        company = st.text_input("Company", placeholder="Company name")
        position = st.text_input("Position / Job title", placeholder="Role title")

        status_column, applied_date_column = st.columns(2)
        status = status_column.selectbox("Status", STATUSES)
        date_applied = applied_date_column.date_input("Date applied")

        interview_column, salary_column = st.columns(2)
        interview_date = interview_column.date_input(
            "Interview date (optional)",
            value=None,
        )
        salary = salary_column.text_input(
            "Salary (optional)",
            placeholder="For example: $75,000",
        )
        notes = st.text_area(
            "Notes (optional)",
            placeholder="Add useful details about the role or application",
        )

        save_application = st.form_submit_button(
            "Save application",
            type="primary",
            use_container_width=True,
        )

    if save_application:
        if not company.strip() or not position.strip():
            st.error("Please enter both a company and a position.")
        else:
            add_application(
                company.strip(),
                position.strip(),
                status,
                date_applied=date_applied.isoformat(),
                interview_date=(
                    interview_date.isoformat() if interview_date is not None else None
                ),
                salary=salary.strip() or None,
                notes=notes.strip() or None,
            )
            st.success("Application saved successfully!")

with controls_column:
    st.subheader("Manage applications")
    st.markdown(
        '<p class="section-intro">Update progress or remove an application in one place.</p>',
        unsafe_allow_html=True,
    )

    applications_with_ids = get_applications_with_ids()
    update_tab, delete_tab = st.tabs(["Update status", "Delete"])

    with update_tab:
        if applications_with_ids:
            selected_application = st.selectbox(
                "Application",
                applications_with_ids,
                format_func=lambda application: (
                    f"{application[1]} — {application[2]} ({application[3]})"
                ),
            )
            new_status = st.selectbox("New status", STATUSES)

            if st.button("Update status", type="primary", use_container_width=True):
                update_application_status(selected_application[0], new_status)
                st.success("Application status updated successfully!")
        else:
            st.info("Save an application before updating its status.")

    with delete_tab:
        if applications_with_ids:
            application_to_delete = st.selectbox(
                "Application to delete",
                applications_with_ids,
                format_func=lambda application: (
                    f"{application[1]} — {application[2]} ({application[3]})"
                ),
            )
            st.warning("Deleting an application cannot be undone.")
            confirm_delete = st.checkbox("I understand and want to delete it")

            if st.button("Delete application", use_container_width=True):
                if confirm_delete:
                    delete_application(application_to_delete[0])
                    st.success("Application deleted successfully!")
                else:
                    st.error("Please confirm that you want to delete this application.")
        else:
            st.info("There are no applications to delete.")

st.divider()
st.subheader("Saved Applications")
st.markdown(
    '<p class="section-intro">Search your saved roles and quickly review the important details.</p>',
    unsafe_allow_html=True,
)

search_column, filter_column = st.columns([2, 1])
search_text = search_column.text_input(
    "Search",
    placeholder="Search by company, position, or notes",
)
status_filter = filter_column.selectbox(
    "Filter by status",
    ["All", *STATUSES],
)

# Read the applications after updates or deletions so changes appear immediately.
applications = search_applications(search_text, status_filter)

if applications:
    application_word = "application" if len(applications) == 1 else "applications"
    st.caption(f"Showing {len(applications)} {application_word}")
    for (
        saved_company,
        saved_position,
        saved_status,
        saved_date_applied,
        saved_interview_date,
        saved_salary,
        saved_notes,
    ) in applications:
        with st.container(border=True):
            title_column, status_column = st.columns([4, 1])
            title_column.markdown(f"#### {saved_company}")
            title_column.caption(saved_position)
            status_column.markdown(
                f'<span class="application-status">{saved_status}</span>',
                unsafe_allow_html=True,
            )

            details = []
            if saved_date_applied:
                details.append(f"Applied: {saved_date_applied}")
            if saved_interview_date:
                details.append(f"Interview: {saved_interview_date}")
            if saved_salary:
                details.append(f"Salary: {saved_salary}")
            if details:
                st.caption(" • ".join(details))
            if saved_notes:
                st.markdown("**Notes**")
                st.write(saved_notes)
else:
    if search_text.strip():
        st.info("No applications match your search. Try a different search term.")
    elif status_filter == "All":
        st.info("There are no applications yet. Add your first application above!")
    else:
        st.info(f"There are no applications with the status {status_filter}.")
