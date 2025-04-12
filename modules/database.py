import sqlite3
import streamlit as st
from typing import List, Dict
from config import config
from modules.utils import haversine
'''
def get_db_path():
    # This will use the DB path from secrets but make it work in Streamlit Cloud's writeable directory
    db_name = os.path.basename(st.secrets["database"]["DB_PATH"])
    return db_name
'''
def init_db():
    """Initialize database with tables if they don't exist"""
    conn = None
    try:
        conn = sqlite3.connect(config["DB_PATH"])
        #conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        # Create emergency table
        cursor.execute('''CREATE TABLE IF NOT EXISTS emergency
                     (eid INTEGER PRIMARY KEY,
                      location TEXT,
                      latitude REAL,
                      longitude REAL,
                      text TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        # Create resource table
        cursor.execute('''CREATE TABLE IF NOT EXISTS resource
                     (resourceid INTEGER PRIMARY KEY,
                      amenity TEXT,
                      name TEXT,
                      latitude REAL,
                      longitude REAL,
                      created_by INTEGER,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        # Create volunteer table with password field
        cursor.execute('''CREATE TABLE IF NOT EXISTS volunteer
                     (id INTEGER PRIMARY KEY,
                      name TEXT,
                      email TEXT UNIQUE,
                      password_hash TEXT,
                      location TEXT,
                      latitude REAL,
                      longitude REAL,
                      speciality TEXT,
                      phone TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get database connection with proper configuration"""
    conn = sqlite3.connect(config["DB_PATH"], check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.create_function("HAVERSINE", 4, haversine)
    return conn

def execute_query(query: str, params: tuple = (), commit: bool = True) -> List[Dict]:
    """Execute a database query with proper connection handling"""
    conn = None
    results = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)

        if query.strip().upper().startswith("SELECT"):
            results = [dict(row) for row in cur.fetchall()]

        if commit:
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        if conn and commit:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return results

def add_emergency(location: str, lat: float, lon: float, text: str):
    """Add new emergency to database"""
    return execute_query(
        '''INSERT INTO emergency (location, latitude, longitude, text)
           VALUES (?, ?, ?, ?)''',
        (location, lat, lon, text)
    )

def get_nearest_emergencies(user_lat: float, user_lon: float, max_km=10, limit=10):
    """Get nearest emergencies to location"""
    return execute_query(
        f'''SELECT *, 
            HAVERSINE(?, ?, latitude, longitude) AS distance
            FROM emergency
            WHERE HAVERSINE(?, ?, latitude, longitude) <= ?
            ORDER BY distance
            LIMIT ?''',
        (user_lat, user_lon, user_lat, user_lon, max_km, limit)
    )

def add_resource(amenity: str, name: str, lat: float, lon: float, created_by: int):
    """Add new resource to database"""
    return execute_query(
        '''INSERT INTO resource (amenity, name, latitude, longitude, created_by)
           VALUES (?, ?, ?, ?, ?)''',
        (amenity, name, lat, lon, created_by)
    )

def get_nearest_resources(user_lat: float, user_lon: float, max_km=10, limit=10):
    """Get nearest resources to location"""
    return execute_query(
        f'''SELECT *, 
            HAVERSINE(?, ?, latitude, longitude) AS distance
            FROM resource
            WHERE HAVERSINE(?, ?, latitude, longitude) <= ?
            ORDER BY distance
            LIMIT ?''',
        (user_lat, user_lon, user_lat, user_lon, max_km, limit)
    )

def register_volunteer(name: str, email: str, password: str, location: str,
                       lat: float, lon: float, speciality: str, phone: str):
    """Register new volunteer"""
    from modules.utils import hash_password

    # Hash the password
    password_hash = hash_password(password)

    # Check if email already exists
    existing = execute_query(
        "SELECT * FROM volunteer WHERE email = ?",
        (email,)
    )
    if existing:
        return False, "Email already registered"

    # Insert new volunteer
    execute_query(
        '''INSERT INTO volunteer 
           (name, email, password_hash, location, latitude, longitude, speciality, phone)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (name, email, password_hash, location, lat, lon, speciality, phone)
    )

    # Get the new volunteer ID
    result = execute_query(
        "SELECT id FROM volunteer WHERE email = ?",
        (email,)
    )
    if result:
        return True, result[0]['id']
    return False, "Registration failed"

def volunteer_login(email: str, password: str):
    """Login volunteer by email and password"""
    from modules.utils import hash_password

    password_hash = hash_password(password)
    volunteers = execute_query(
        'SELECT * FROM volunteer WHERE email = ? AND password_hash = ?',
        (email, password_hash)
    )
    if not volunteers:
        return False, "Invalid email or password"
    return True, volunteers[0]

def get_volunteer_dashboard(volunteer_id: int):
    """Get dashboard data for volunteer"""
    # Get volunteer info
    volunteer = execute_query(
        'SELECT * FROM volunteer WHERE id = ?',
        (volunteer_id,)
    )[0]

    # Get nearby emergencies
    emergencies = get_nearest_emergencies(
        volunteer['latitude'],
        volunteer['longitude']
    )

    # Get nearby resources
    resources = get_nearest_resources(
        volunteer['latitude'],
        volunteer['longitude']
    )

    # Get resources created by this volunteer
    my_resources = execute_query(
        'SELECT * FROM resource WHERE created_by = ?',
        (volunteer_id,)
    )

    return volunteer, emergencies, resources, my_resources
