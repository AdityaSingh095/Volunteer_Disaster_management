import streamlit as st
import tempfile
import os
from modules.database import add_emergency, get_nearest_resources
from modules.geospatial import get_lat_lon, create_emergency_map, display_map
from modules.processing import (
    transcribe_audio,
    english_speech_to_text,
    process_image,
    process_text,
    extract_entities,
    generate_summary,
    get_first_aid_response
)

def user_workflow():
    """Main user workflow for emergency reporting and resource finding"""
    st.header("Disaster Management System")

    tab1, tab2 = st.tabs(["Report Emergency", "Find Resources"])

    with tab1:
        report_emergency()

    with tab2:
        find_resources()


def report_emergency():
    """Emergency reporting workflow with multiple input combinations"""
    st.subheader("Report Emergency")

    # Initialize emergency info
    emergency_info = {
        "location": "",
        "latitude": None,
        "longitude": None,
        "text": "",
        "emergency_type": ""
    }

    # Get location information
    location = st.text_input("Location (address, city, landmark)")
    if location:
        emergency_info["location"] = location
        lat, lon = get_lat_lon(location)
        if lat and lon:
            emergency_info["latitude"] = lat
            emergency_info["longitude"] = lon
            st.success(f"Location found: {lat:.6f}, {lon:.6f}")

            # Show location on map
            m = create_emergency_map(lat, lon)
            display_map(m)
        else:
            st.error("Location not found. Please try a different location.")

    # Input selection - allow multiple input types
    st.subheader("Report Input")
    st.write("Select the input methods you want to use (multiple allowed)")

    use_text = st.checkbox("Text Description")
    use_voice = st.checkbox("Voice Recording")
    use_image = st.checkbox("Image Upload")

    # Process text input if selected
    if use_text:
        st.subheader("Text Description")
        text_input = st.text_area("Describe the emergency situation", height=150)
        if text_input:
            emergency_info["text"] += f"\nText Description: {text_input}"

            # Process text to identify emergency type
            emergency_type, confidence = process_text(text_input)
            if not emergency_info["emergency_type"]:
                emergency_info["emergency_type"] = emergency_type

            # Extract entities
            entities = extract_entities(text_input)

            # Display extracted entities if any found
            if any(entities.values()):
                with st.expander("Extracted Information from Text"):
                    st.write(f"Detected emergency type: **{emergency_type}** (Confidence: {confidence:.2f})")
                    for entity_type, items in entities.items():
                        if items:
                            st.write(f"**{entity_type.replace('_', ' ').title()}**: {', '.join(items)}")

    # Process voice input if selected
    if use_voice:
        st.subheader("Voice Recording")
        uploaded_audio = st.audio_input("Upload audio file (mp3, wav)", key="audio_upload")

        if uploaded_audio is not None:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_audio.getvalue())
                audio_path = tmp_file.name

            st.audio(uploaded_audio)

            try:
                # Automatically process audio
                with st.spinner("Transcribing audio..."):
                    transcription = transcribe_audio(audio_path)
                    if not transcription:
                        transcription = english_speech_to_text(audio_path)

                if transcription:
                    st.success("Transcription successful")
                    st.write(transcription)
                    emergency_info["text"] += f"\nVoice Transcription: {transcription}"

                    # Process transcription to identify emergency type
                    emergency_type, confidence = process_text(transcription)
                    if not emergency_info["emergency_type"]:
                        emergency_info["emergency_type"] = emergency_type

                    # Extract entities
                    entities = extract_entities(transcription)

                    # Display extracted entities
                    if any(entities.values()):
                        with st.expander("Extracted Information from Voice"):
                            st.write(f"Detected emergency type: **{emergency_type}** (Confidence: {confidence:.2f})")
                            for entity_type, items in entities.items():
                                if items:
                                    st.write(f"**{entity_type.replace('_', ' ').title()}**: {', '.join(items)}")
                else:
                    st.error("Transcription failed. Please try again or use a different input method.")
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(audio_path)
                except:
                    pass

    # Process image input if selected
    if use_image:
        st.subheader("Image Upload")
        uploaded_image = st.file_uploader("Upload image file", type=["jpg", "jpeg", "png"], key="image_upload")

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_image.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_image.getvalue())
                image_path = tmp_file.name

            try:
                # Automatically process image
                with st.spinner("Processing image..."):
                    image_description = process_image(image_path)

                if image_description:
                    st.success("Image processed successfully")
                    st.write(image_description)
                    emergency_info["text"] += f"\nImage Description: {image_description}"

                    # Process description to identify emergency type
                    emergency_type, confidence = process_text(image_description)
                    if not emergency_info["emergency_type"]:
                        emergency_info["emergency_type"] = emergency_type

                    with st.expander("Extracted Information from Image"):
                        st.write(f"Detected emergency type: **{emergency_type}** (Confidence: {confidence:.2f})")
                else:
                    st.error("Image processing failed. Please try again or use a different input method.")
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(image_path)
                except:
                    pass

    # Submit report
    if st.button("Submit Emergency Report"):
        if emergency_info["location"] and emergency_info["text"] and emergency_info["latitude"] and emergency_info["longitude"]:
            add_emergency(
                emergency_info["location"],
                emergency_info["latitude"],
                emergency_info["longitude"],
                emergency_info["text"]
            )
            st.success("Emergency report submitted successfully!")

            # Show first aid information
            if emergency_info["emergency_type"]:
                st.subheader("First Aid Information")
                with st.spinner("Generating first aid response..."):
                    first_aid_info = get_first_aid_response(emergency_info["emergency_type"], emergency_info["text"])
                st.markdown(first_aid_info)

                # Notify about message being sent (simulation)
                st.success("First aid information sent to your contact number.")
        else:
            st.error("Please provide both location and at least one type of emergency information.")

def find_resources():
    """Resource finding workflow"""
    st.subheader("Find Nearby Resources")

    location = st.text_input("Your Location (address, city, landmark)", key="resource_location")

    if location:
        lat, lon = get_lat_lon(location)
        if lat and lon:
            st.success(f"Location found: {lat:.6f}, {lon:.6f}")

            # Get search radius
            radius = st.slider("Search Radius (km)", 1, 50, 10)

            # Get nearest resources
            resources = get_nearest_resources(lat, lon, max_km=radius)

            if resources:
                st.subheader(f"Found {len(resources)} resources within {radius} km")

                # Show resources on map
                m = create_emergency_map(lat, lon, resources=resources, center_label="Your Location")
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
            else:
                st.info("No resources found within the specified radius.")

                # Show empty map
                m = create_emergency_map(lat, lon, center_label="Your Location")
                display_map(m)
        else:
            st.error("Location not found. Please try a different location.")
