"""The Streamlit web interface for the Job Application Tracker."""

import streamlit as st

from database import add_application, initialize_database


# Create the database table before showing the page.
initialize_database()

st.set_page_config(page_title="Job Application Tracker", page_icon="💼")

st.title("💼 Job Application Tracker")
st.write("Welcome! This app will help you keep track of your job applications.")

st.subheader("Add a job application")

# These widgets collect the details for one application.
company = st.text_input("Company")
position = st.text_input("Position / Job title")
status = st.selectbox(
    "Status",
    ["Applied", "Interview", "Offer", "Rejected"],
)

if st.button("Save application"):
    if company and position:
        add_application(company, position, status)
        st.success("Application saved successfully!")
    else:
        st.warning("Please enter both a company and a position.")
