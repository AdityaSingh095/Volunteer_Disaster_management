import streamlit as st
import tempfile
import os
from modules.database import (
    volunteer_login,
    register_volunteer,
    get_volunteer_dashboard,
    add_resource
)
from modules.geospatial import get_lat_lon, create_emergency_map, display_map
from modules.processing import (
    generate_summary,
    get_first_aid_response,
    process_text,
    extract_entities
)

def volunteer_login_workflow():
    """Volunteer login workflow"""
    st.header("Volunteer Login")

    # Check if already logged in
    if st.session_state.logged_in:
        volunteer_dashboard()
        return

    # Login form
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if email and password:
                success, result = volunteer_login(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.volunteer_id = result["id"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.error("Please enter both email and password.")

    # Link to registration
    st.write("New volunteer? [Register here](#volunteer-registration)")

def volunteer_registration_workflow():
    """Volunteer registration workflow"""
    st.header("Volunteer Registration")

    # Check if already logged in
    if st.session_state.logged_in:
        st.warning("You are already logged in. Please log out to register a new account.")
        return

    # Registration form
    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        location = st.text_input("Location")
        speciality = st.selectbox(
            "Speciality",
            ["First Aid", "Medical", "Rescue", "Firefighting", "Transportation", "Communication", "Other"]
        )

        if speciality == "Other":
            speciality = st.text_input("Specify speciality")

        phone = st.text_input("Phone Number")

        submitted = st.form_submit_button("Register")

        if submitted:
            # Validate inputs
            if not (name and email and password and confirm_password and location and speciality and phone):
                st.error("Please fill all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Get coordinates from location
                lat, lon = get_lat_lon(location)
                if not (lat and lon):
                    st.error("Could not get coordinates for the provided location. Please be more specific.")
                else:
                    # Register volunteer
                    success, result = register_volunteer(name, email, password, location, lat, lon, speciality, phone)
                    if success:
                        st.success("Registration successful! You can now log in.")
                        st.session_state.logged_in = True
                        st.session_state.volunteer_id = result
                        st.rerun()
                    else:
                        st.error(result)

def volunteer_dashboard():
    """Volunteer dashboard after login"""
    if not st.session_state.logged_in:
        st.warning("Please log in to access the dashboard.")
        return

    st.header("Volunteer Dashboard")

    # Get dashboard data
    volunteer, emergencies, resources, my_resources = get_volunteer_dashboard(st.session_state.volunteer_id)

    # Volunteer info
    st.subheader("Your Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {volunteer['name']}")
        st.write(f"**Email:** {volunteer['email']}")
        st.write(f"**Phone:** {volunteer['phone']}")
    with col2:
        st.write(f"**Location:** {volunteer['location']}")
        st.write(f"**Speciality:** {volunteer['speciality']}")

    # Tabs for different dashboard sections
    tab1, tab2, tab3, tab4 = st.tabs(["Nearby Emergencies", "Resource Management", "Add Resource", "Situation Analysis"])

    with tab1:
        st.subheader("Nearby Emergencies")
        if emergencies:
            # Show emergencies on map
            m = create_emergency_map(
                volunteer['latitude'],
                volunteer['longitude'],
                emergencies=emergencies,
                center_label="Your Location"
            )
            display_map(m)

            # Show emergency details
            for i, emergency in enumerate(emergencies):
                with st.expander(f"Emergency at {emergency['location']} ({emergency['distance']:.2f} km)"):
                    st.write(f"**Report:** {emergency['text']}")
                    st.write(f"**Reported on:** {emergency['timestamp']}")
        else:
            st.info("No emergencies reported nearby.")

    with tab2:
        st.subheader("Nearby Resources")
        if resources:
            # Show resources on map
            m = create_emergency_map(
                volunteer['latitude'],
                volunteer['longitude'],
                resources=resources,
                center_label="Your Location"
            )
            display_map(m)

            # Show resources in table
            resources_data = []
            for r in resources:
                resources_data.append({
                    "Name": r["name"],
                    "Type": r["amenity"],
                    "Distance (km)": f"{r['distance']:.2f}"
                })

            st.table(resources_data)

            st.subheader("Resources Added by You")
            if my_resources:
                my_resources_data = []
                for r in my_resources:
                    my_resources_data.append({
                        "Name": r["name"],
                        "Type": r["amenity"],
                        "Added on": r["timestamp"]
                    })

                st.table(my_resources_data)
            else:
                st.info("You haven't added any resources yet.")
        else:
            st.info("No resources found nearby.")

    with tab3:
        st.subheader("Add New Resource")

        amenity_type = st.selectbox(
            "Resource Type",
            ["Hospital", "Medical Center", "Police Station", "Fire Station",
             "Shelter", "Food Bank", "Water Supply", "Fuel Station", "Other"]
        )

        if amenity_type == "Other":
            amenity_type = st.text_input("Specify resource type")

        name = st.text_input("Resource Name")

        # Location can be different from volunteer's location
        use_current_location = st.checkbox("Use my current location")

        if use_current_location:
            location_lat = volunteer['latitude']
            location_lon = volunteer['longitude']
            location_name = volunteer['location']

            st.success(f"Using your location: {location_name} ({location_lat:.6f}, {location_lon:.6f})")

            # Show location on map
            m = create_emergency_map(location_lat, location_lon, center_label="Resource Location")
            display_map(m)
        else:
            location_name = st.text_input("Resource Location")

            if location_name:
                location_lat, location_lon = get_lat_lon(location_name)
                if location_lat and location_lon:
                    st.success(f"Location found: {location_lat:.6f}, {location_lon:.6f}")

                    # Show location on map
                    m = create_emergency_map(location_lat, location_lon, center_label="Resource Location")
                    display_map(m)
                else:
                    st.error("Location not found. Please try a different location.")
                    location_lat = None
                    location_lon = None
            else:
                location_lat = None
                location_lon = None

        if st.button("Add Resource"):
            if amenity_type and name and location_lat and location_lon:
                add_resource(
                    amenity_type,
                    name,
                    location_lat,
                    location_lon,
                    st.session_state.volunteer_id
                )
                st.success("Resource added successfully!")
                st.rerun()
            else:
                st.error("Please fill all required fields.")

    with tab4:
        st.subheader("Situation Analysis")
        st.write("Upload documents or provide information to get situation analysis and first aid guidance")

        # Document upload for volunteers
        uploaded_document = st.file_uploader("Upload document (PDF)", type=["pdf"])

        situation_text = st.text_area("Describe the situation", height=150)

        if uploaded_document is not None:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_document.getvalue())
                pdf_path = tmp_file.name

            try:
                if st.button("Analyze Document"):
                    with st.spinner("Processing document..."):
                        summary = generate_summary(pdf_path)

                    if summary:
                        st.success("Document processed successfully")

                        # Display summary
                        with st.expander("Document Summary"):
                            st.write(summary)

                        # Process summary to identify emergency type
                        emergency_type, confidence = process_text(summary)

                        # Extract entities
                        entities = extract_entities(summary)

                        # Display extracted information
                        with st.expander("Extracted Information"):
                            st.write(f"Detected emergency type: **{emergency_type}** (Confidence: {confidence:.2f})")
                            for entity_type, items in entities.items():
                                if items:
                                    st.write(f"**{entity_type.replace('_', ' ').title()}**: {', '.join(items)}")

                        # Generate first aid response
                        st.subheader("First Aid Information")
                        with st.spinner("Generating first aid response..."):
                            first_aid_info = get_first_aid_response(emergency_type, summary)
                        st.markdown(first_aid_info)
                    else:
                        st.error("Document processing failed. Please try again.")
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(pdf_path)
                except:
                    pass

        elif situation_text:
            if st.button("Analyze Text"):
                # Process text to identify emergency type
                emergency_type, confidence = process_text(situation_text)

                # Extract entities
                entities = extract_entities(situation_text)

                # Display extracted information
                with st.expander("Extracted Information"):
                    st.write(f"Detected emergency type: **{emergency_type}** (Confidence: {confidence:.2f})")
                    for entity_type, items in entities.items():
                        if items:
                            st.write(f"**{entity_type.replace('_', ' ').title()}**: {', '.join(items)}")

                # Generate first aid response
                st.subheader("First Aid Information")
                with st.spinner("Generating first aid response..."):
                    first_aid_info = get_first_aid_response(emergency_type, situation_text)
                st.markdown(first_aid_info)

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.volunteer_id = None
        st.sidebar.success("Logged out successfully!")
        st.rerun()
