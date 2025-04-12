import streamlit as st
import pandas as pd
import plotly.express as px
from modules.database import execute_query
from modules.geospatial import create_emergency_map, display_map

def admin_dashboard():
    """Administrative dashboard for overview of the system"""
    st.header("System Dashboard")

    if 'admin_logged_in' not in st.session_state or not st.session_state.admin_logged_in:
        st.warning("Please log in as an administrator to view this dashboard.")

        # Simple admin login
        with st.form("admin_login"):
            username = st.text_input("Admin Username")
            password = st.text_input("Admin Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                # Simple hardcoded admin check - in a real app this would use proper authentication
                if username == "admin" and password == "admin123":
                    st.session_state.admin_logged_in = True
                    st.success("Admin login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
        return

    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Emergencies", "Resources", "Volunteers"])

    with tab1:
        system_overview()

    with tab2:
        emergency_analysis()

    with tab3:
        resource_analysis()

    with tab4:
        volunteer_analysis()

    # Logout button
    if st.sidebar.button("Admin Logout"):
        st.session_state.admin_logged_in = False
        st.sidebar.success("Logged out successfully!")
        st.experimental_rerun()

def system_overview():
    """System overview dashboard"""
    st.subheader("System Overview")

    # Get summary statistics
    emergencies = execute_query("SELECT COUNT(*) as count FROM emergency")[0]["count"]
    resources = execute_query("SELECT COUNT(*) as count FROM resource")[0]["count"]
    volunteers = execute_query("SELECT COUNT(*) as count FROM volunteer")[0]["count"]

    # Display KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Emergencies Reported", emergencies)

    with col2:
        st.metric("Resources Available", resources)

    with col3:
        st.metric("Volunteers Registered", volunteers)

    # Get time series data
    emergency_trend = execute_query('''
        SELECT date(timestamp) as date, COUNT(*) as count
        FROM emergency
        GROUP BY date(timestamp)
        ORDER BY date
    ''')

    if emergency_trend:
        # Convert to DataFrame
        df = pd.DataFrame(emergency_trend)

        # Plot trend
        fig = px.line(df, x="date", y="count", title="Emergency Reports Over Time")
        st.plotly_chart(fig)

    # Map of all emergencies and resources
    st.subheader("System Coverage Map")

    # Get all emergencies and resources
    all_emergencies = execute_query("SELECT * FROM emergency")
    all_resources = execute_query("SELECT * FROM resource")

    if all_emergencies or all_resources:
        # Get center coordinates (average of all points)
        all_lats = []
        all_lons = []

        for emergency in all_emergencies:
            all_lats.append(emergency["latitude"])
            all_lons.append(emergency["longitude"])

        for resource in all_resources:
            all_lats.append(resource["latitude"])
            all_lons.append(resource["longitude"])

        if all_lats and all_lons:
            center_lat = sum(all_lats) / len(all_lats)
            center_lon = sum(all_lons) / len(all_lons)

            # Create map
            m = create_emergency_map(
                center_lat,
                center_lon,
                resources=all_resources,
                emergencies=all_emergencies,
                center_label="System Center"
            )
            display_map(m)
        else:
            st.info("No location data available to display on map.")
    else:
        st.info("No emergencies or resources to display on map.")

def emergency_analysis():
    """Emergency data analysis dashboard"""
    st.subheader("Emergency Analysis")

    # Get all emergencies
    emergencies = execute_query("SELECT * FROM emergency ORDER BY timestamp DESC")

    if not emergencies:
        st.info("No emergency data available for analysis.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(emergencies)

    # Display interactive table
    st.dataframe(df)

    # Extract text features (would use NLP in a real implementation)
    # This is a placeholder - we'd use the NLP functions to extract these
    emergency_types = ["Earthquake", "Fire", "Flood", "Medical", "Other"]
    emergency_counts = [10, 15, 7, 12, 5]  # Example data

    # Plot emergency types
    fig = px.pie(names=emergency_types, values=emergency_counts, title="Emergency Types")
    st.plotly_chart(fig)

    # Heatmap of emergencies
    st.subheader("Emergency Location Heatmap")

    # Create map
    if emergencies:
        # Calculate center
        center_lat = sum(e["latitude"] for e in emergencies) / len(emergencies)
        center_lon = sum(e["longitude"] for e in emergencies) / len(emergencies)

        # Create map
        m = create_emergency_map(
            center_lat,
            center_lon,
            emergencies=emergencies,
            center_label="Center"
        )
        display_map(m)

def resource_analysis():
    """Resource data analysis dashboard"""
    st.subheader("Resource Analysis")

    # Get all resources
    resources = execute_query('''
        SELECT r.*, v.name as added_by
        FROM resource r
        LEFT JOIN volunteer v ON r.created_by = v.id
        ORDER BY r.timestamp DESC
    ''')

    if not resources:
        st.info("No resource data available for analysis.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(resources)

    # Display interactive table
    st.dataframe(df)

    # Group by amenity type
    amenity_counts = df["amenity"].value_counts().reset_index()
    amenity_counts.columns = ["amenity", "count"]

    # Plot amenity types
    fig = px.bar(amenity_counts, x="amenity", y="count", title="Resource Types")
    st.plotly_chart(fig)

    # Map of resources
    st.subheader("Resource Location Map")

    # Create map
    if resources:
        # Calculate center
        center_lat = sum(r["latitude"] for r in resources) / len(resources)
        center_lon = sum(r["longitude"] for r in resources) / len(resources)

        # Create map
        m = create_emergency_map(
            center_lat,
            center_lon,
            resources=resources,
            center_label="Center"
        )
        display_map(m)

def volunteer_analysis():
    """Volunteer data analysis dashboard"""
    st.subheader("Volunteer Analysis")

    # Get all volunteers (excluding password hash for security)
    volunteers = execute_query('''
        SELECT id, name, email, location, latitude, longitude, speciality, phone, timestamp
        FROM volunteer
        ORDER BY timestamp DESC
    ''')

    if not volunteers:
        st.info("No volunteer data available for analysis.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(volunteers)

    # Display interactive table
    st.dataframe(df)

    # Group by speciality
    speciality_counts = df["speciality"].value_counts().reset_index()
    speciality_counts.columns = ["speciality", "count"]

    # Plot speciality types
    fig = px.pie(speciality_counts, names="speciality", values="count", title="Volunteer Specialities")
    st.plotly_chart(fig)

    # Resources added by volunteers
    resources_by_volunteer = execute_query('''
        SELECT v.name, COUNT(r.resourceid) as resource_count
        FROM volunteer v
        LEFT JOIN resource r ON v.id = r.created_by
        GROUP BY v.id
        ORDER BY resource_count DESC
        LIMIT 10
    ''')

    if resources_by_volunteer:
        # Convert to DataFrame
        df_resources = pd.DataFrame(resources_by_volunteer)

        # Plot resources by volunteer
        fig = px.bar(df_resources, x="name", y="resource_count",
                    title="Top 10 Volunteers by Resources Added")
        st.plotly_chart(fig)

    # Map of volunteers
    st.subheader("Volunteer Location Map")

    # Convert volunteers to the format expected by create_emergency_map
    volunteer_locations = []
    for v in volunteers:
        volunteer_locations.append({
            "latitude": v["latitude"],
            "longitude": v["longitude"],
            "name": v["name"],
            "amenity": v["speciality"],
            "distance": 0  # Not relevant for this display
        })

    # Create map
    if volunteer_locations:
        # Calculate center
        center_lat = sum(v["latitude"] for v in volunteers) / len(volunteers)
        center_lon = sum(v["longitude"] for v in volunteers) / len(volunteers)

        # Create map
        m = create_emergency_map(
            center_lat,
            center_lon,
            resources=volunteer_locations,  # Use volunteers as "resources" for the map
            center_label="Center"
        )
        display_map(m)
