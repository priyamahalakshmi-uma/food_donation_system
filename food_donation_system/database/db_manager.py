import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "food_donation.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create NGOs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ngos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        address TEXT NOT NULL,
        capacity_servings INTEGER NOT NULL,
        operating_hours TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )
    """)

    # Create Donations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_name TEXT NOT NULL,
        donor_contact TEXT NOT NULL,
        donor_lat REAL NOT NULL,
        donor_lon REAL NOT NULL,
        donor_address TEXT,
        food_type TEXT NOT NULL,
        confidence REAL,
        estimated_weight_kg REAL NOT NULL,
        estimated_servings INTEGER NOT NULL,
        safety_tag TEXT NOT NULL,
        safety_score REAL,
        prepared_time TEXT,
        storage_condition TEXT,
        matched_ngo_id INTEGER,
        matched_ngo_name TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(matched_ngo_id) REFERENCES ngos(id)
    )
    """)

    # Create Food Requests table (For NGO & Volunteer Need Requests)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requester_type TEXT NOT NULL, -- 'NGO' or 'Volunteer'
        requester_name TEXT NOT NULL,
        contact TEXT NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        address TEXT NOT NULL,
        food_type TEXT NOT NULL,
        servings_needed INTEGER NOT NULL,
        urgency TEXT DEFAULT 'Standard', -- 'Urgent', 'Standard'
        notes TEXT,
        matched_donation_id INTEGER,
        status TEXT DEFAULT 'Open', -- 'Open', 'Matched', 'Fulfilled'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    
    # Seed NGOs
    cursor.execute("DELETE FROM ngos")
    seed_ngos = [
        ("Hope Harbor Shelter & Orphanage", "+91 98422 10199", 11.0880, 77.3520, "Dharapuram Main Road, Kovilvazhi, Tiruppur, Tamil Nadu 641606", 250, "08:00 - 22:00"),
        ("Annapoorna Food Relief Trust", "+91 94433 02441", 11.1200, 77.3400, "Avinashi Main Road, Gandhi Nagar, Tiruppur, Tamil Nadu 641603", 200, "07:30 - 21:30"),
        ("Seva Rural Care Foundation", "+91 98941 04122", 11.0920, 77.3620, "Kangeyam Road, Nallur, Tiruppur, Tamil Nadu 641606", 300, "24 Hours"),
        ("Asha Children Welfare Home", "+91 97877 05673", 11.1085, 77.3411, "Old Bus Stand Road, City Center, Tiruppur, Tamil Nadu 641601", 180, "08:00 - 20:00"),
        ("City Harvest Relief Center", "+91 98430 55410", 11.0450, 77.3120, "Veerapandi, Palladam Main Road, Tiruppur, Tamil Nadu 641605", 150, "08:00 - 22:00")
    ]
    cursor.executemany("""
    INSERT INTO ngos (name, contact, lat, lon, address, capacity_servings, operating_hours)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, seed_ngos)
    conn.commit()

    # Seed Donations
    cursor.execute("DELETE FROM donations")
    cursor.execute("""
    INSERT INTO donations (
        donor_name, donor_contact, donor_lat, donor_lon, donor_address,
        food_type, confidence, estimated_weight_kg, estimated_servings,
        safety_tag, safety_score, prepared_time, storage_condition,
        matched_ngo_id, matched_ngo_name, status
    ) VALUES (
        'Sree Annapoorna Restaurant', '+91 98422 54321', 11.0850, 77.3300, 'Palladam Main Road, Tiruppur, Tamil Nadu 641604',
        'Cooked Rice & Grain Dishes', 0.96, 22.5, 65,
        'Fresh', 0.94, '2.0 hours ago', 'Covered & Room Temp (20-25°C)',
        1, 'Hope Harbor Shelter & Orphanage', 'Accepted'
    )
    """)
    conn.commit()

    # Seed Sample Food Need Requests (NGO & Volunteer)
    cursor.execute("DELETE FROM food_requests")
    seed_requests = [
        ("NGO", "Hope Harbor Shelter & Orphanage", "+91 98422 10199", 11.0880, 77.3520, "Kovilvazhi, Tiruppur", "Roti, Naan & Bread", 50, "Urgent", "Required for evening shelter dinner distribution."),
        ("Volunteer", "Kavitha (Youth Volunteer)", "+91 97890 12345", 11.1085, 77.3411, "Tiruppur Railway Station North Gate", "Assorted Mixed Meal / Buffet", 35, "Urgent", "Required for 35 homeless individuals near railway station."),
        ("Volunteer", "Ramesh (Community Care Volunteer)", "+91 98421 67890", 11.0920, 77.3620, "Nallur Government School Area", "Cooked Rice & Grain Dishes", 40, "Standard", "Lunch meals needed for construction migrant family camp.")
    ]
    cursor.executemany("""
    INSERT INTO food_requests (
        requester_type, requester_name, contact, lat, lon, address,
        food_type, servings_needed, urgency, notes, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
    """, seed_requests)
    conn.commit()

    conn.close()

def get_all_ngos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ngos WHERE active = 1")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_donation(donor_name, donor_contact, donor_lat, donor_lon, donor_address,
                 food_type, confidence, estimated_weight_kg, estimated_servings,
                 safety_tag, safety_score, prepared_time, storage_condition):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO donations (
        donor_name, donor_contact, donor_lat, donor_lon, donor_address,
        food_type, confidence, estimated_weight_kg, estimated_servings,
        safety_tag, safety_score, prepared_time, storage_condition, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
    """, (
        donor_name, donor_contact, donor_lat, donor_lon, donor_address,
        food_type, confidence, estimated_weight_kg, estimated_servings,
        safety_tag, safety_score, prepared_time, storage_condition
    ))
    donation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return donation_id

def assign_ngo_to_donation(donation_id, ngo_id, ngo_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE donations 
    SET matched_ngo_id = ?, matched_ngo_name = ?, status = 'Matched'
    WHERE id = ?
    """, (ngo_id, ngo_name, donation_id))
    conn.commit()
    conn.close()

def update_donation_status(donation_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE donations SET status = ? WHERE id = ?
    """, (status, donation_id))
    conn.commit()
    conn.close()

def get_all_donations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_donation_by_id(donation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations WHERE id = ?", (donation_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# FOOD REQUEST FUNCTIONS (NGO & VOLUNTEER)
def add_food_request(requester_type, requester_name, contact, lat, lon, address,
                     food_type, servings_needed, urgency, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO food_requests (
        requester_type, requester_name, contact, lat, lon, address,
        food_type, servings_needed, urgency, notes, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
    """, (
        requester_type, requester_name, contact, lat, lon, address,
        food_type, servings_needed, urgency, notes
    ))
    req_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return req_id

def get_all_food_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM food_requests ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_request_status(request_id, status, matched_donation_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE food_requests SET status = ?, matched_donation_id = ? WHERE id = ?
    """, (status, matched_donation_id, request_id))
    conn.commit()
    conn.close()
