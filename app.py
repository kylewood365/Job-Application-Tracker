"""The Streamlit web interface for the Job Application Tracker."""

import streamlit as st

from database import (
    add_application,
    delete_application,
    get_applications_with_ids,
    initialize_database,
    search_applications,
    update_application_status,
)


# Create the database table before showing the page.
initialize_database()

st.set_page_config(page_title="Job Application Tracker", page_icon="💼")

st.title("💼 Job Application Tracker")
st.write("Welcome! This app will help you keep track of your job applications.")

company = st.text_input("Company")
position = st.text_input("Position / Job title")
status = st.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected"])

if st.button("Save application"):
    if not company.strip() or not position.strip():
        st.error("Please enter both a company and a position.")
    else:
        add_application(company.strip(), position.strip(), status)
        st.success("Application saved successfully!")

st.subheader("Update Application Status")

applications_with_ids = get_applications_with_ids()

if applications_with_ids:
    selected_application = st.selectbox(
        "Choose an application",
        applications_with_ids,
        format_func=lambda application: (
            f"{application[1]} — {application[2]} ({application[3]})"
        ),
    )
    new_status = st.selectbox(
        "New status",
        ["Applied", "Interview", "Offer", "Rejected"],
    )

    if st.button("Update status"):
        update_application_status(selected_application[0], new_status)
        st.success("Application status updated successfully!")
else:
    st.info("Save an application before updating its status.")

st.subheader("Delete Application")

if applications_with_ids:
    application_to_delete = st.selectbox(
        "Choose an application to delete",
        applications_with_ids,
        format_func=lambda application: (
            f"{application[1]} — {application[2]} ({application[3]})"
        ),
    )
    st.warning("Deleting an application cannot be undone.")
    confirm_delete = st.checkbox("Yes, I want to delete this application")

    if st.button("Delete application"):
        if confirm_delete:
            delete_application(application_to_delete[0])
            st.success("Application deleted successfully!")
        else:
            st.error("Please confirm that you want to delete this application.")
else:
    st.info("There are no applications to delete.")

st.subheader("Saved Applications")

search_text = st.text_input(
    "Search saved applications",
    placeholder="Search by company or position",
)

status_filter = st.selectbox(
    "Filter saved applications by status",
    ["All", "Applied", "Interview", "Offer", "Rejected"],
)

# Read the applications after updates or deletions so changes appear immediately.
applications = search_applications(search_text, status_filter)

if applications:
    for saved_company, saved_position, saved_status in applications:
        st.write(f"**{saved_company}** — {saved_position} — {saved_status}")
else:
    if search_text.strip():
        st.info("No applications match your search. Try a different search term.")
    elif status_filter == "All":
        st.info("There are no applications yet. Add your first application above!")
    else:
        st.info(f"There are no applications with the status {status_filter}.")
