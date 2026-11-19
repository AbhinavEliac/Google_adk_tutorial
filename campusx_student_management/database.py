"""Database management and dummy dataset initialization for CampusX Student Management."""

import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campusx_students.db")


def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: str = DB_FILE, force: bool = False) -> None:
    """Initializes tables and seeds dummy datasets for students, courses, and enrollments."""
    if os.path.exists(db_path) and not force:
        return

    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. Create Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            registration_date TEXT NOT NULL
        )
    """)

    # 2. Create Courses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            instructor TEXT NOT NULL,
            price_inr REAL NOT NULL,
            duration_weeks INTEGER NOT NULL
        )
    """)

    # 3. Create Enrollments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            is_paid INTEGER NOT NULL,
            payment_date TEXT,
            days_since_payment INTEGER,
            completion_percentage REAL NOT NULL,
            refund_status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)

    # Clear existing data if forced re-init
    cursor.execute("DELETE FROM enrollments")
    cursor.execute("DELETE FROM courses")
    cursor.execute("DELETE FROM students")

    # 4. Seed Courses Dataset
    courses_data = [
        ("CX-CRS-01", "Complete Data Science Bootcamp", "Nitish Singh", 5999.0, 24),
        ("CX-CRS-02", "Deep Learning & Neural Networks Masterclass", "Nitish Singh", 6999.0, 16),
        ("CX-CRS-03", "Mastering LangChain & Agentic AI Systems", "Nitish Singh", 7999.0, 12),
        ("CX-CRS-04", "Machine Learning with Python & Scikit-Learn", "Ankit Sachan", 4999.0, 14),
        ("CX-CRS-05", "Generative AI Engineering: LLMs to Agents", "Nitish Singh", 8999.0, 10),
    ]
    cursor.executemany("""
        INSERT INTO courses (course_id, course_name, instructor, price_inr, duration_weeks)
        VALUES (?, ?, ?, ?, ?)
    """, courses_data)

    # 5. Seed Students Dataset
    students_data = [
        ("CX-STU-101", "Rahul Sharma", "rahul.sharma@example.com", "+91-9876543210", "2026-11-15"),
        ("CX-STU-102", "Priya Verma", "priya.verma@example.com", "+91-9876543211", "2026-11-01"),
        ("CX-STU-103", "Amit Patel", "amit.patel@example.com", "+91-9876543212", "2026-11-10"),
        ("CX-STU-104", "Sneha Reddy", "sneha.reddy@example.com", "+91-9876543213", "2026-11-18"),
        ("CX-STU-105", "Vikram Singh", "vikram.singh@example.com", "+91-9876543214", "2026-10-25"),
        ("CX-STU-106", "Ananya Iyer", "ananya.iyer@example.com", "+91-9876543215", "2026-11-17"),
    ]
    cursor.executemany("""
        INSERT INTO students (student_id, name, email, phone, registration_date)
        VALUES (?, ?, ?, ?, ?)
    """, students_data)

    # 6. Seed Enrollments Dataset
    # Cases to test:
    # - ENR-101 (Rahul): Paid, 3 days ago, 12% completed -> ELIGIBLE
    # - ENR-102 (Priya): Paid, 15 days ago, 18% completed -> INELIGIBLE (days > 7)
    # - ENR-103 (Amit): Paid, 4 days ago, 45% completed -> INELIGIBLE (completion > 20%)
    # - ENR-104 (Sneha): Unpaid, 0 days, 5% completed -> INELIGIBLE (not paid)
    # - ENR-105 (Vikram - Course 1): Paid, 5 days ago, 10% completed -> ELIGIBLE
    # - ENR-106 (Vikram - Course 2): Paid, 22 days ago, 85% completed -> INELIGIBLE (days > 7, completion > 20%)
    # - ENR-107 (Ananya): Paid, 2 days ago, 5% completed, refund_status='Already Refunded' -> ALREADY REFUNDED
    enrollments_data = [
        ("ENR-101", "CX-STU-101", "CX-CRS-01", 1, "2026-11-17", 3, 12.0, "Not Requested"),
        ("ENR-102", "CX-STU-102", "CX-CRS-02", 1, "2026-11-05", 15, 18.0, "Not Requested"),
        ("ENR-103", "CX-STU-103", "CX-CRS-03", 1, "2026-11-16", 4, 45.0, "Not Requested"),
        ("ENR-104", "CX-STU-104", "CX-CRS-04", 0, None, 0, 5.0, "Not Requested"),
        ("ENR-105", "CX-STU-105", "CX-CRS-01", 1, "2026-11-15", 5, 10.0, "Not Requested"),
        ("ENR-106", "CX-STU-105", "CX-CRS-03", 1, "2026-10-29", 22, 85.0, "Not Requested"),
        ("ENR-107", "CX-STU-106", "CX-CRS-05", 1, "2026-11-18", 2, 5.0, "Already Refunded"),
    ]
    cursor.executemany("""
        INSERT INTO enrollments (
            enrollment_id, student_id, course_id, is_paid,
            payment_date, days_since_payment, completion_percentage, refund_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, enrollments_data)

    conn.commit()
    conn.close()


# Ensure DB exists on import
init_database()


def get_student_by_email_db(email: str) -> Optional[Dict[str, Any]]:
    """Query student record by unique email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name, email, phone, registration_date
        FROM students
        WHERE LOWER(email) = LOWER(?)
    """, (email.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_enrollments_db(email: str) -> List[Dict[str, Any]]:
    """Query all enrollments with course details for a student email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.student_id,
            s.name AS student_name,
            s.email,
            e.enrollment_id,
            e.course_id,
            c.course_name,
            c.instructor,
            c.price_inr,
            e.is_paid,
            e.payment_date,
            e.days_since_payment,
            e.completion_percentage,
            e.refund_status
        FROM students s
        JOIN enrollments e ON s.student_id = e.student_id
        JOIN courses c ON e.course_id = c.course_id
        WHERE LOWER(s.email) = LOWER(?)
    """, (email.strip(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_courses_db() -> List[Dict[str, Any]]:
    """Query all available courses."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT course_id, course_name, instructor, price_inr, duration_weeks
        FROM courses
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_course_by_id_db(course_id: str) -> Optional[Dict[str, Any]]:
    """Query course details by course_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT course_id, course_name, instructor, price_inr, duration_weeks
        FROM courses
        WHERE UPPER(course_id) = UPPER(?)
    """, (course_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_enrollment_refund_status_db(enrollment_id: str, new_status: str) -> bool:
    """Update refund status for an enrollment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE enrollments
        SET refund_status = ?
        WHERE enrollment_id = ?
    """, (new_status, enrollment_id.strip()))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
