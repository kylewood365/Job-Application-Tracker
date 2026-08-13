"""The Streamlit web interface for the Job Application Tracker."""

import streamlit as st

from database import initialize_database


# Create the database table before showing the page.
initialize_database()

st.set_page_config(page_title="Job Application Tracker", page_icon="💼")

st.title("💼 Job Application Tracker")
st.write("Welcome! This app will help you keep track of your job applications.")
st.info("The project setup is ready. Application features will be added next.")
