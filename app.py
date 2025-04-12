import streamlit as st
from modules.utils import init_session_state
from modules.database import init_db
from views.user import user_workflow
from views.volunteer import volunteer_login_workflow, volunteer_registration_workflow

def main():
    """Main Streamlit application"""
    # Initialize database
    init_db()

    st.title("Disaster Management Application")

    # Sidebar navigation
    workflow = st.sidebar.radio(
        "Select Workflow",
        ("User", "Volunteer Login", "Volunteer Registration")
    )

    if workflow == "User":
        user_workflow()
    elif workflow == "Volunteer Login":
        volunteer_login_workflow()
    elif workflow == "Volunteer Registration":
        volunteer_registration_workflow()

if __name__ == '__main__':
    init_session_state()
    main()
