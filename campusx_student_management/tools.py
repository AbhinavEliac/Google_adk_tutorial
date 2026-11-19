"""Tools for CampusX Student Management Agent."""

from typing import Any, Dict, Optional
from .database import (
    get_all_courses_db,
    get_course_by_id_db,
    get_student_by_email_db,
    get_student_enrollments_db,
    update_enrollment_refund_status_db,
)


def get_student_by_email(email: str) -> Dict[str, Any]:
    """Inquires about a student uniquely using their email address.

    Args:
        email: The student's registered email address (e.g., 'rahul.sharma@example.com').

    Returns:
        A dictionary containing student details (student_id, name, email, phone, registration_date),
        or an error message if the student is not found.
    """
    cleaned_email = email.strip()
    student = get_student_by_email_db(cleaned_email)
    if not student:
        return {
            "status": "not_found",
            "message": f"No student found with email: {cleaned_email}",
        }
    return {
        "status": "success",
        "student": student,
    }


def get_student_enrollments(email: str) -> Dict[str, Any]:
    """Retrieves all course enrollments for a student using their email address.

    Args:
        email: The student's registered email address.

    Returns:
        A dictionary containing student enrollments including course names, payment status,
        days since payment, course completion percentage, and refund status.
    """
    cleaned_email = email.strip()
    enrollments = get_student_enrollments_db(cleaned_email)
    if not enrollments:
        student = get_student_by_email_db(cleaned_email)
        if not student:
            return {
                "status": "not_found",
                "message": f"No student found with email: {cleaned_email}",
            }
        return {
            "status": "success",
            "message": f"Student {student['name']} is registered but not enrolled in any courses.",
            "enrollments": [],
        }

    return {
        "status": "success",
        "student_name": enrollments[0]["student_name"],
        "email": cleaned_email,
        "total_enrollments": len(enrollments),
        "enrollments": enrollments,
    }


def check_refund_eligibility(email: str, course_id: Optional[str] = None) -> Dict[str, Any]:
    """Evaluates refund eligibility for a student.

    Refund Rule:
    A student is eligible for a refund IF AND ONLY IF:
    1. The course enrollment has been paid (is_paid == True).
    2. Payment was made within the last 7 days (days_since_payment <= 7).
    3. The student has NOT completed more than 20% of the course (completion_percentage <= 20.0).
    4. A refund has not already been processed or approved.

    Otherwise, the refund request is rejected.

    Args:
        email: The student's email address.
        course_id: Optional course ID (e.g. 'CX-CRS-01'). If omitted, checks all enrolled courses.

    Returns:
        A dictionary detailing eligibility for the course(s), including pass/fail status
        for each criterion and a human-readable explanation.
    """
    cleaned_email = email.strip()
    enrollments = get_student_enrollments_db(cleaned_email)
    if not enrollments:
        return {
            "status": "error",
            "message": f"No enrollments found for student with email '{cleaned_email}'.",
        }

    results = []
    for enr in enrollments:
        cid = enr["course_id"]
        if course_id and cid.upper() != course_id.strip().upper():
            continue

        c_name = enr["course_name"]
        enr_id = enr["enrollment_id"]
        is_paid = bool(enr["is_paid"])
        days = enr["days_since_payment"] or 0
        completion = enr["completion_percentage"]
        refund_status = enr["refund_status"]

        # Criteria evaluations
        paid_ok = is_paid
        days_ok = days <= 7
        completion_ok = completion <= 20.0
        status_ok = refund_status not in ["Approved", "Already Refunded"]

        reasons = []
        if not paid_ok:
            reasons.append("Course has not been paid (unpaid or trial enrollment).")
        if not days_ok:
            reasons.append(f"Exceeded the 7-day refund window (payment made {days} days ago).")
        if not completion_ok:
            reasons.append(f"Course progress ({completion}%) exceeds the 20% maximum completion threshold.")
        if not status_ok:
            reasons.append(f"Refund is already in status: '{refund_status}'.")

        is_eligible = paid_ok and days_ok and completion_ok and status_ok

        decision_message = (
            f"ELIGIBLE for refund: Enrolled in '{c_name}', completed {completion}% (<= 20%), and paid {days} day(s) ago (<= 7 days)."
            if is_eligible
            else f"NOT ELIGIBLE for refund: {'; '.join(reasons)}"
        )

        results.append({
            "enrollment_id": enr_id,
            "course_id": cid,
            "course_name": c_name,
            "is_paid": is_paid,
            "days_since_payment": days,
            "completion_percentage": completion,
            "current_refund_status": refund_status,
            "is_eligible": is_eligible,
            "criteria_check": {
                "payment_verified": paid_ok,
                "within_7_days": days_ok,
                "completion_under_20_percent": completion_ok,
                "not_already_refunded": status_ok,
            },
            "decision": decision_message,
        })

    if not results:
        return {
            "status": "error",
            "message": f"Student is not enrolled in course '{course_id}'.",
        }

    return {
        "status": "success",
        "student_email": cleaned_email,
        "results": results,
    }


def process_refund(email: str, course_id: str, reason: str = "Student requested refund") -> Dict[str, Any]:
    """Processes a refund request for an eligible course enrollment.

    Args:
        email: The student's email address.
        course_id: The course ID (e.g., 'CX-CRS-01').
        reason: Optional reason for refund.

    Returns:
        A dictionary with the outcome of the refund processing.
    """
    eval_res = check_refund_eligibility(email=email, course_id=course_id)
    if eval_res.get("status") != "success":
        return eval_res

    course_result = eval_res["results"][0]
    if not course_result["is_eligible"]:
        return {
            "status": "rejected",
            "message": f"Refund cannot be processed. Reason: {course_result['decision']}",
            "details": course_result,
        }

    enr_id = course_result["enrollment_id"]
    course_name = course_result["course_name"]

    success = update_enrollment_refund_status_db(enr_id, "Approved")
    if success:
        return {
            "status": "approved",
            "message": f"Refund of course '{course_name}' ({course_id}) has been successfully approved for student {email}.",
            "enrollment_id": enr_id,
            "reason": reason,
        }
    else:
        return {
            "status": "error",
            "message": f"Failed to update database for enrollment ID {enr_id}.",
        }


def list_courses() -> Dict[str, Any]:
    """Returns a list of all courses offered by CampusX.

    Returns:
        A dictionary containing available courses with course_id, title, instructor, and price.
    """
    courses = get_all_courses_db()
    return {
        "status": "success",
        "total_courses": len(courses),
        "courses": courses,
    }
