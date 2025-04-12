import streamlit as st
import hashlib
import math

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'volunteer_id' not in st.session_state:
        st.session_state.volunteer_id = None

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth"""
    # Ensure inputs are floats
    lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    R = 6371  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def hash_password(password):
    """Create a secure password hash"""
    return hashlib.sha256(password.encode()).hexdigest()
