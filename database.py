"""
Scholar Track - Database Management Module
Handles SQLite connection, schema creation, seeding sample data,
and all parameterized CRUD queries with deadline and status calculations.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta

# Database file location in the same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'scholarships.db')

VALID_STATUSES = ['Pending', 'Applied', 'Approved', 'Rejected']


def get_db_connection():
    """Create and return a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency and foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Initialize SQLite database and scholarships table.
    Seed sample records if the table is newly created or empty.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_name TEXT NOT NULL,
            provider TEXT NOT NULL,
            description TEXT,
            eligibility TEXT,
            amount REAL NOT NULL DEFAULT 0.0,
            deadline TEXT NOT NULL,
            application_link TEXT,
            application_status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    # Check if table already contains data
    cursor.execute("SELECT COUNT(*) AS count FROM scholarships;")
    row = cursor.fetchone()
    count = row['count'] if row else 0

    if count == 0:
        seed_sample_data(cursor)
        conn.commit()

    conn.close()


def seed_sample_data(cursor):
    """
    Seeds initial realistic scholarship records for student testing.
    Deadlines are calculated relative to today so sample data is always dynamic and relevant.
    """
    today = date.today()

    sample_scholarships = [
        (
            "Google Generation Scholarship (APAC)",
            "Google Inc.",
            "Designed to help students pursuing computer science degrees excel in technology and become active leaders in the field.",
            "Undergraduate or graduate female students enrolled in Computer Science or related STEM degrees with high academic merit.",
            2500.00,
            (today + timedelta(days=3)).strftime("%Y-%m-%d"),  # Expiring soon
            "https://buildyourfuture.withgoogle.com/scholarships",
            "Applied"
        ),
        (
            "Microsoft Imagine Cup Technology Grant",
            "Microsoft Corporation",
            "Annual scholarship providing funding, mentoring, and Azure cloud credits to innovative student projects solving global issues.",
            "Enrolled university students worldwide (minimum 16 years old) with a verified software or hardware project prototype.",
            5000.00,
            (today + timedelta(days=14)).strftime("%Y-%m-%d"),  # Approaching
            "https://imaginecup.microsoft.com",
            "Pending"
        ),
        (
            "Reliance Foundation Undergraduate Scholarship",
            "Reliance Foundation",
            "Recognizes exceptional undergraduate students across diverse degree streams to support higher education tuition and living costs.",
            "Full-time undergraduate degree first-year students with minimum 60% in Grade 12 and family income below specified threshold.",
            2400.00,
            (today + timedelta(days=30)).strftime("%Y-%m-%d"),  # Active upcoming
            "https://www.scholarships.reliancefoundation.org",
            "Approved"
        ),
        (
            "Adobe Women-in-Technology Merit Award",
            "Adobe Systems",
            "Recognizes outstanding female undergraduate and masters students studying computer science and related technical programs.",
            "Identifies as female, enrolled full-time in CS, Engineering, or Data Science, with exceptional leadership and coding achievements.",
            10000.00,
            (today + timedelta(days=45)).strftime("%Y-%m-%d"),  # Active upcoming
            "https://www.adobe.com/careers/university/scholarships.html",
            "Pending"
        ),
        (
            "Tata Trust Higher Education Grant",
            "Sir Dorabji Tata Trust",
            "Needs-cum-merit financial assistance for students pursuing engineering, medicine, and research degrees in accredited colleges.",
            "Undergraduate and postgraduate students enrolled in recognized universities with demonstrated financial need.",
            1500.00,
            (today + timedelta(days=60)).strftime("%Y-%m-%d"),  # Active upcoming
            "https://www.tatatrusts.org",
            "Applied"
        ),
        (
            "Amazon Future Engineer Scholarship",
            "Amazon",
            "Supports high school seniors and college freshmen who plan to pursue a degree in computer science, software engineering, or related field.",
            "High school seniors or 1st-year college students from underrepresented communities studying CS with minimum 3.0 GPA.",
            4000.00,
            (today - timedelta(days=7)).strftime("%Y-%m-%d"),  # Recently expired
            "https://www.amazonfutureengineer.com",
            "Rejected"
        ),
        (
            "National STEM Research Fellowship",
            "Department of Science & Technology",
            "Fellowship grant to encourage undergraduate research scholars in basic sciences, mathematics, and biotechnology.",
            "Students in final year of B.Sc/B.Tech with an approved research proposal endorsed by their department head.",
            3200.00,
            (today - timedelta(days=25)).strftime("%Y-%m-%d"),  # Expired
            "https://dst.gov.in/fellowships",
            "Pending"
        ),
        (
            "AWS AI & Machine Learning Pioneer Award",
            "Amazon Web Services",
            "Equity-based scholarship offering financial support, Udacity Nanodegree mentorship, and hands-on deep learning workshops.",
            "College students aged 16+ globally with interest in Artificial Intelligence and basic Python programming proficiency.",
            3500.00,
            (today + timedelta(days=6)).strftime("%Y-%m-%d"),  # Expiring soon
            "https://aws.amazon.com/machine-learning/scholarship",
            "Applied"
        ),
    ]

    cursor.executemany("""
        INSERT INTO scholarships (
            scholarship_name, provider, description, eligibility,
            amount, deadline, application_link, application_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, sample_scholarships)


def enrich_scholarship(row):
    """
    Takes an sqlite3.Row or dict representing a scholarship and adds calculated fields:
    - days_remaining: integer difference from today
    - deadline_status: 'expired' | 'expiring_soon' | 'upcoming'
    - deadline_badge_class: Bootstrap CSS badge class
    - deadline_badge_text: Human readable text (e.g. '3 days left', 'Expired 5 days ago')
    - status_badge_class: Bootstrap CSS badge class for application status
    - formatted_deadline: e.g. 'Oct 25, 2026'
    - formatted_amount: e.g. '$2,500.00'
    """
    if row is None:
        return None

    data = dict(row)
    today = date.today()

    try:
        deadline_date = datetime.strptime(data['deadline'], "%Y-%m-%d").date()
        days_remaining = (deadline_date - today).days
        formatted_deadline = deadline_date.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        deadline_date = today
        days_remaining = 0
        formatted_deadline = data.get('deadline', 'N/A')

    data['days_remaining'] = days_remaining
    data['formatted_deadline'] = formatted_deadline

    # Deadline status & badges
    if days_remaining < 0:
        data['is_expired'] = True
        data['is_expiring_soon'] = False
        data['is_upcoming'] = False
        data['deadline_status'] = 'expired'
        data['deadline_badge_class'] = 'bg-danger text-white'
        past_days = abs(days_remaining)
        data['deadline_badge_text'] = f"Expired ({past_days}d ago)" if past_days > 1 else "Expired yesterday"
    elif days_remaining == 0:
        data['is_expired'] = False
        data['is_expiring_soon'] = True
        data['is_upcoming'] = False
        data['deadline_status'] = 'expiring_soon'
        data['deadline_badge_class'] = 'bg-danger text-white animate-pulse'
        data['deadline_badge_text'] = "Due Today!"
    elif 1 <= days_remaining <= 7:
        data['is_expired'] = False
        data['is_expiring_soon'] = True
        data['is_upcoming'] = False
        data['deadline_status'] = 'expiring_soon'
        data['deadline_badge_class'] = 'bg-warning text-dark font-weight-bold'
        data['deadline_badge_text'] = f"{days_remaining}d left (Urgent)"
    else:
        data['is_expired'] = False
        data['is_expiring_soon'] = False
        data['is_upcoming'] = True
        data['deadline_status'] = 'upcoming'
        data['deadline_badge_class'] = 'bg-success text-white'
        data['deadline_badge_text'] = f"{days_remaining} days left"

    # Application status badge class
    status = data.get('application_status', 'Pending')
    if status == 'Approved':
        data['status_badge_class'] = 'badge-status-approved'
        data['status_icon'] = 'bi-check-circle-fill'
    elif status == 'Applied':
        data['status_badge_class'] = 'badge-status-applied'
        data['status_icon'] = 'bi-send-check-fill'
    elif status == 'Rejected':
        data['status_badge_class'] = 'badge-status-rejected'
        data['status_icon'] = 'bi-x-circle-fill'
    else:  # Pending
        data['status_badge_class'] = 'badge-status-pending'
        data['status_icon'] = 'bi-hourglass-split'

    # Formatted amount
    try:
        amt = float(data.get('amount', 0))
        data['formatted_amount'] = f"${amt:,.2f}"
    except (ValueError, TypeError):
        data['formatted_amount'] = f"${data.get('amount', 0)}"

    return data


def get_all_scholarships(search_query=None, status_filter=None, deadline_filter=None, sort_by=None):
    """
    Retrieve all scholarships with optional search query, status filter,
    deadline status filter, and sorting.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM scholarships WHERE 1=1"
    params = []

    # Search filter (name or provider)
    if search_query and search_query.strip():
        query += " AND (scholarship_name LIKE ? OR provider LIKE ? OR description LIKE ?)"
        wildcard = f"%{search_query.strip()}%"
        params.extend([wildcard, wildcard, wildcard])

    # Status filter
    if status_filter and status_filter.strip() and status_filter != 'All':
        query += " AND application_status = ?"
        params.append(status_filter.strip())

    # Sorting
    if sort_by == 'deadline_asc':
        query += " ORDER BY deadline ASC"
    elif sort_by == 'deadline_desc':
        query += " ORDER BY deadline DESC"
    elif sort_by == 'amount_desc':
        query += " ORDER BY amount DESC"
    elif sort_by == 'amount_asc':
        query += " ORDER BY amount ASC"
    elif sort_by == 'name_asc':
        query += " ORDER BY scholarship_name ASC"
    else:
        # Default: newest created first
        query += " ORDER BY created_at DESC, id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Enrich rows with computed status and deadlines
    scholarships = [enrich_scholarship(row) for row in rows]

    # Deadline status filtering (done post-enrichment to respect dynamic current date)
    if deadline_filter and deadline_filter != 'all':
        if deadline_filter == 'upcoming':
            # Both active upcoming and expiring soon
            scholarships = [s for s in scholarships if not s['is_expired']]
        elif deadline_filter == 'expiring_soon':
            scholarships = [s for s in scholarships if s['is_expiring_soon']]
        elif deadline_filter == 'expired':
            scholarships = [s for s in scholarships if s['is_expired']]

    return scholarships


def get_scholarship_by_id(scholarship_id):
    """Fetch a single scholarship by its primary key ID, enriched."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scholarships WHERE id = ?;", (scholarship_id,))
    row = cursor.fetchone()
    conn.close()
    return enrich_scholarship(row) if row else None


def add_scholarship(name, provider, description, eligibility, amount, deadline, application_link, application_status='Pending'):
    """Insert a new scholarship record using parameterized SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scholarships (
            scholarship_name, provider, description, eligibility,
            amount, deadline, application_link, application_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        name.strip(),
        provider.strip(),
        description.strip() if description else '',
        eligibility.strip() if eligibility else '',
        float(amount) if amount else 0.0,
        deadline.strip(),
        application_link.strip() if application_link else '',
        application_status if application_status in VALID_STATUSES else 'Pending'
    ))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_scholarship(scholarship_id, name, provider, description, eligibility, amount, deadline, application_link, application_status):
    """Update an existing scholarship record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE scholarships
        SET scholarship_name = ?,
            provider = ?,
            description = ?,
            eligibility = ?,
            amount = ?,
            deadline = ?,
            application_link = ?,
            application_status = ?
        WHERE id = ?;
    """, (
        name.strip(),
        provider.strip(),
        description.strip() if description else '',
        eligibility.strip() if eligibility else '',
        float(amount) if amount else 0.0,
        deadline.strip(),
        application_link.strip() if application_link else '',
        application_status if application_status in VALID_STATUSES else 'Pending',
        scholarship_id
    ))

    updated_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return updated_rows > 0


def update_scholarship_status(scholarship_id, new_status):
    """Update only the application status of a scholarship."""
    if new_status not in VALID_STATUSES:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE scholarships
        SET application_status = ?
        WHERE id = ?;
    """, (new_status, scholarship_id))
    updated_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return updated_rows > 0


def delete_scholarship(scholarship_id):
    """Delete a scholarship record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scholarships WHERE id = ?;", (scholarship_id,))
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_rows > 0


def get_dashboard_statistics():
    """
    Compile comprehensive dashboard metrics:
    - Total scholarships
    - Upcoming/Active count
    - Expiring soon count (<= 7 days)
    - Expired count
    - Application status breakdowns (Pending, Applied, Approved, Rejected)
    - Total funding amount
    - Total approved funding amount
    - Recently added scholarships (5)
    - Approaching deadline scholarships (5)
    """
    all_scholarships = get_all_scholarships(sort_by='deadline_asc')

    total_scholarships = len(all_scholarships)
    upcoming_count = 0
    expiring_soon_count = 0
    expired_count = 0

    status_counts = {
        'Pending': 0,
        'Applied': 0,
        'Approved': 0,
        'Rejected': 0
    }

    total_amount = 0.0
    approved_amount = 0.0

    urgent_scholarships = []

    for s in all_scholarships:
        amt = float(s.get('amount') or 0.0)
        total_amount += amt

        status = s.get('application_status', 'Pending')
        if status in status_counts:
            status_counts[status] += 1

        if status == 'Approved':
            approved_amount += amt

        if s['is_expired']:
            expired_count += 1
        else:
            upcoming_count += 1
            if s['is_expiring_soon']:
                expiring_soon_count += 1
            # Keep active scholarships in urgent list
            if len(urgent_scholarships) < 5:
                urgent_scholarships.append(s)

    # Get 5 most recently created scholarships
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scholarships ORDER BY created_at DESC, id DESC LIMIT 5;")
    recent_rows = cursor.fetchall()
    conn.close()
    recent_scholarships = [enrich_scholarship(r) for r in recent_rows]

    return {
        'total_scholarships': total_scholarships,
        'upcoming_count': upcoming_count,
        'expiring_soon_count': expiring_soon_count,
        'expired_count': expired_count,
        'status_counts': status_counts,
        'total_amount': total_amount,
        'formatted_total_amount': f"${total_amount:,.2f}",
        'approved_amount': approved_amount,
        'formatted_approved_amount': f"${approved_amount:,.2f}",
        'urgent_scholarships': urgent_scholarships,
        'recent_scholarships': recent_scholarships,
    }
