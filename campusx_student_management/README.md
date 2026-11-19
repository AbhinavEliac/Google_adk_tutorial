# CampusX Student Management & Refund Eligibility Agent

An agentic system built with the **Google Agent Development Kit (ADK)** and **Gemini API** for managing students, courses, enrollments, and automating course refund eligibility evaluations.

---

## 📋 Business Logic & Refund Policy

A student is **ELIGIBLE** for a full refund if and only if:
1. **Payment Verified:** The enrollment must be paid (`is_paid == True`).
2. **Payment Window:** The refund is requested **within 7 days** of payment (`days_since_payment <= 7`).
3. **Course Progress Limit:** The student has finished **no more than 20%** of the course (`completion_percentage <= 20.0%`).
4. **Not Already Refunded:** The current status is not already `Approved` or `Already Refunded`.

If **any** condition fails, the request is rejected with a clear explanation of which policy rule was violated.

---

## 🗄️ Datasets & Database Schema

The system uses an embedded SQLite database (`campusx_students.db`) pre-seeded with 3 interconnected datasets:

### 1. `students` Table
| Column | Type | Description |
|---|---|---|
| `student_id` | TEXT PK | Unique student identifier (e.g. `CX-STU-101`) |
| `name` | TEXT | Full name |
| `email` | TEXT UNIQUE | Unique email address for lookups |
| `phone` | TEXT | Contact number |
| `registration_date` | TEXT | Registration timestamp |

### 2. `courses` Table
| Column | Type | Description |
|---|---|---|
| `course_id` | TEXT PK | Unique course identifier (e.g. `CX-CRS-01`) |
| `course_name` | TEXT | Name of the course |
| `instructor` | TEXT | Course instructor |
| `price_inr` | REAL | Price in INR |
| `duration_weeks` | INTEGER | Course duration |

### 3. `enrollments` Table
| Column | Type | Description |
|---|---|---|
| `enrollment_id` | TEXT PK | Unique enrollment record ID |
| `student_id` | TEXT FK | References `students(student_id)` |
| `course_id` | TEXT FK | References `courses(course_id)` |
| `is_paid` | INTEGER | `1` if paid, `0` if unpaid / trial |
| `payment_date` | TEXT | Date when payment was completed |
| `days_since_payment` | INTEGER | Elapsed days since payment |
| `completion_percentage` | REAL | Current course progress percentage |
| `refund_status` | TEXT | `Not Requested`, `Pending`, `Approved`, `Already Refunded` |

---

## 🧪 Pre-Seeded Test Scenarios

The dummy dataset includes pre-configured records designed to test every edge case:

| Student Email | Name | Course | Paid? | Days Ago | Progress | Expected Outcome | Reason |
|---|---|---|---|---|---|---|---|
| `rahul.sharma@example.com` | Rahul Sharma | Data Science Bootcamp | ✅ Yes | 3 days | 12.0% | **ELIGIBLE** | Within 7 days & <= 20% progress |
| `priya.verma@example.com` | Priya Verma | Deep Learning Masterclass | ✅ Yes | 15 days | 18.0% | **NOT ELIGIBLE** | Exceeded 7 days (paid 15 days ago) |
| `amit.patel@example.com` | Amit Patel | Agentic AI Systems | ✅ Yes | 4 days | 45.0% | **NOT ELIGIBLE** | Completed 45% (> 20% limit) |
| `sneha.reddy@example.com` | Sneha Reddy | Machine Learning | ❌ No | 0 days | 5.0% | **NOT ELIGIBLE** | Course is unpaid |
| `vikram.singh@example.com` | Vikram Singh | Enrolled in 2 courses | ✅ Yes | 5d & 22d | 10% & 85% | **Mixed** | Course 1 eligible, Course 2 ineligible |
| `ananya.iyer@example.com` | Ananya Iyer | Generative AI Engineering | ✅ Yes | 2 days | 5.0% | **ALREADY REFUNDED** | Status is `Already Refunded` |

---

## 🛠️ Tools Developed

1. **`get_student_by_email(email: str)`**
   * Looks up a student uniquely by their email address.
2. **`get_student_enrollments(email: str)`**
   * Retrieves all courses enrolled by the student along with payment, progress, and refund status.
3. **`check_refund_eligibility(email: str, course_id: Optional[str])`**
   * Evaluates the 4-part refund policy and returns a structured decision and breakdown.
4. **`process_refund(email: str, course_id: str, reason: str)`**
   * Updates database enrollment status to `Approved` if eligible.
5. **`list_courses()`**
   * Returns all available CampusX courses with IDs, titles, and instructors.

---

## 🚀 How to Run

### Interactive CLI:
```bash
adk run campusx_student_management
```

### Web UI:
```bash
adk web
```
Then visit `http://127.0.0.1:8000` and select **campusx_student_management**.

---

## 💬 Sample Prompts to Try

* *"Look up student rahul.sharma@example.com and tell me what courses they are taking."*
* *"Is rahul.sharma@example.com eligible for a refund on their Data Science course?"*
* *"Check refund eligibility for priya.verma@example.com."* (Checks 15-day limit)
* *"Can amit.patel@example.com get a refund?"* (Checks 20% progress limit)
* *"Show me all courses offered by CampusX."*
* *"Process refund for rahul.sharma@example.com for course CX-CRS-01."*
