import requests
import folium
import streamlit as st
from streamlit_folium import folium_static
from config import config

def get_lat_lon(location_name):
    """Get latitude and longitude from location name using OpenCage Geocoder"""
    url = f'https://api.opencagedata.com/geocode/v1/json?q={location_name}&key={config["OPENCAGE_API_KEY"]}'
    try:
        response = requests.get(url)
        data = response.json()
        if data['status']['code'] == 200 and data['results']:
            lat = data['results'][0]['geometry']['lat']
            lon = data['results'][0]['geometry']['lng']
            return lat, lon
        else:
            return None, None
    except Exception as e:
        st.error(f"Geocoding error: {e}")
        return None, None

def create_emergency_map(lat, lon, resources=None, emergencies=None, center_label="Your Location"):
    """Create a Folium map with emergency information and resources"""
    # Create map centered at the given coordinates
    m = folium.Map(location=[lat, lon], zoom_start=13)

    # Add marker for the center location
    folium.Marker(
        [lat, lon],
        popup=center_label,
        tooltip=center_label,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    # Add resource markers if provided
    if resources:
        for res in resources:
            folium.Marker(
                [res["latitude"], res["longitude"]],
                popup=f"<b>{res['name']}</b><br>Type: {res['amenity']}<br>Distance: {res['distance']:.2f} km",
                tooltip=f"{res['name']} ({res['amenity']})",
                icon=folium.Icon(color="green", icon="plus")
            ).add_to(m)

            # Add a line connecting center to resource
            folium.PolyLine(
                locations=[[lat, lon], [res["latitude"], res["longitude"]]],
                weight=2,
                color="green",
                opacity=0.7,
                dash_array="5"
            ).add_to(m)

    # Add emergency markers if provided
    if emergencies:
        for emerg in emergencies:
            folium.Marker(
                [emerg["latitude"], emerg["longitude"]],
                popup=f"<b>Emergency at {emerg['location']}</b><br>Distance: {emerg['distance']:.2f} km<br>Report: {emerg['text'][:100]}...",
                tooltip=f"Emergency: {emerg['location']}",
                icon=folium.Icon(color="red", icon="exclamation-sign")
            ).add_to(m)

            # Add a line connecting center to emergency
            folium.PolyLine(
                locations=[[lat, lon], [emerg["latitude"], emerg["longitude"]]],
                weight=2,
                color="red",
                opacity=0.7
            ).add_to(m)

    # Add circle showing rough coverage area (10km)
    folium.Circle(
        radius=10000,  # 10km in meters
        location=[lat, lon],
        color="blue",
        fill=True,
        fill_opacity=0.1
    ).add_to(m)

    # Add distance scale
    folium.plugins.MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)

    return m

def display_map(m):
    """Display the Folium map in Streamlit"""
    folium_static(m)
