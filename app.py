"""The Streamlit web interface for the Job Application Tracker."""

import streamlit as st

from database import add_application, get_all_applications, initialize_database


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

st.subheader("Saved Applications")

applications = get_all_applications()

if applications:
    for saved_company, saved_position, saved_status in applications:
        st.write(f"**{saved_company}** — {saved_position} — {saved_status}")
else:
    st.info("There are no applications yet. Add your first application above!")
