from db import get_connection
from datetime import datetime

def create_customer_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phoneNumber VARCHAR(10),
            email VARCHAR(100),
            linkedId INT,
            linkPrecedence ENUM('primary','secondary'),
            createdAt DATETIME NOT NULL,
            updatedAt DATETIME NOT NULL,
            deletedAt DATETIME
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def query_records(email=None, phone=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM customer WHERE 1=1"
    params = []
    if email:
        query += " AND email = %s"
        params.append(email)
    if phone:
        query += " AND phoneNumber = %s"
        params.append(phone)
    cursor.execute(query, params)
    results = cursor.fetchall()

    return results

def _find_existing_contacts(cursor, email, phone):
    """Find all existing contacts matching email or phone"""
    cursor.execute(
        "SELECT * FROM customer WHERE (email = %s OR phoneNumber = %s) AND deletedAt IS NULL ORDER BY createdAt",
        (email, phone)
    )
    return cursor.fetchall()

def _handle_new_contact(cursor, email, phone, now):
    """Create new primary contact"""
    cursor.execute(
        "INSERT INTO customer (email, phoneNumber, linkPrecedence, createdAt, updatedAt) VALUES (%s, %s, 'primary', %s, %s)",
        (email, phone, now, now)
    )
    return cursor.lastrowid

def _handle_existing_contacts(cursor, existing, email, phone, now):
    """Handle existing contacts - return primary_id"""
    exact_match = any(c['email'] == email and c['phoneNumber'] == phone for c in existing)
    primaries = [c for c in existing if c['linkPrecedence'] == 'primary']

    if exact_match:
        return primaries[0]['id'] if primaries else existing[0]['id']

    if len(primaries) <= 1:
        # Add secondary to existing primary
        primary_id = primaries[0]['id'] if primaries else existing[0]['id']
        cursor.execute(
            "INSERT INTO customer (email, phoneNumber, linkPrecedence, linkedId, createdAt, updatedAt) VALUES (%s, %s, 'secondary', %s, %s, %s)",
            (email, phone, primary_id, now, now)
        )
        return primary_id

    # Merge multiple primaries no new record is added,existing accounts are linked
    primary_id = min(primaries, key=lambda x: x['createdAt'])['id']
    for p in primaries:
        if p['id'] != primary_id:
            cursor.execute(
                "UPDATE customer SET linkPrecedence = 'secondary', linkedId = %s, updatedAt = %s WHERE id = %s",
                (primary_id, now, p['id'])
            )
    return primary_id

def _build_response(cursor, primary_id):
    """Build consolidated contact response"""
    cursor.execute(
        "SELECT id, email, phoneNumber FROM customer WHERE (id = %s OR linkedId = %s) AND deletedAt IS NULL ORDER BY CASE WHEN id = %s THEN 0 ELSE 1 END, createdAt",
        (primary_id, primary_id, primary_id)
    )
    contacts = cursor.fetchall()

    emails = list(dict.fromkeys([c['email'] for c in contacts if c['email']]))
    phones = list(dict.fromkeys([c['phoneNumber'] for c in contacts if c['phoneNumber']]))

    return {
        "contact": {
            "primaryContatctId": primary_id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": [c['id'] for c in contacts[1:]]
        }
    }

def add_or_update_contact(email=None, phone=None):
    """Main function - orchestrates the contact management flow"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    now = datetime.now()

    existing = _find_existing_contacts(cursor, email, phone)

    if not existing:
        primary_id = _handle_new_contact(cursor, email, phone, now)
    else:
        primary_id = _handle_existing_contacts(cursor, existing, email, phone, now)

    response = _build_response(cursor, primary_id)

    conn.commit()
    cursor.close()
    conn.close()

    return response
