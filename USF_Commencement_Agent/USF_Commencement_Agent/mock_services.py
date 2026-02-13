"""
Mock services for Shibboleth SSO, Ellucian Banner, and the application database.
Replace these with real integrations when connecting to USF infrastructure.
"""

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────
# Mock Shibboleth SSO
# ─────────────────────────────────────────────────────────────────────

# In production, this value comes from the Shibboleth SP session attributes
# (e.g., the REMOTE_USER header or eduPersonPrincipalName attribute).

SHIBBOLETH_SESSION = {
    "username": "sjbosso",
    "auth_time": datetime.now(timezone.utc).isoformat(),
    "idp": "https://idp.usfca.edu/shibboleth",
}


def get_sso_username() -> str:
    """Simulate extracting the authenticated username from Shibboleth."""
    return SHIBBOLETH_SESSION["username"]


# ─────────────────────────────────────────────────────────────────────
# Mock Ellucian Banner Student Information System
# ─────────────────────────────────────────────────────────────────────

# In production, these would be REST calls to the Ethos/BIA API or
# SQL queries against Banner reporting views.

BANNER_RECORDS = {
    "sjbosso": {
        "student_name": "Steven Bosso",
        "usf_email": "sjbosso@usfca.edu",
        "student_id": "12345678",
        "school_college": "CAS",
        "program": "Computer Science",
    },
    # Add more mock students here for testing
    "jdoe": {
        "student_name": "Jane Doe",
        "usf_email": "jdoe@usfca.edu",
        "student_id": "87654321",
        "school_college": "SOM",
        "program": "Business Administration",
    },
}


def lookup_banner_record(username: str) -> Optional[dict]:
    """
    Simulate a Banner API call to retrieve student information.

    In production, this calls:
      GET /api/persons?filter=credentials.value=={username}
      GET /api/student-academic-programs?student.id=={person_id}
    via the Ethos Integration API or Banner Integration API.
    """
    return BANNER_RECORDS.get(username)


# ─────────────────────────────────────────────────────────────────────
# In-Memory Application Database
# ─────────────────────────────────────────────────────────────────────

@dataclass
class ExceptionRequest:
    """Represents a commencement exception request."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Pre-filled from SSO + Banner
    usf_username: str = ""
    student_name: str = ""
    usf_email: str = ""
    student_id: str = ""
    school_college: str = ""
    program: str = ""

    # Collected from student
    phone_number: str = ""
    original_ceremony_semester: str = ""
    requested_ceremony_semester: str = ""
    extenuating_circumstances: str = ""

    # Workflow
    status: str = "DRAFT"  # DRAFT -> SUBMITTED -> UNDER_REVIEW -> APPROVED/DENIED
    submitted_at: Optional[str] = None
    decided_at: Optional[str] = None

    # Registrar decision
    reviewer_name: Optional[str] = None
    decision_rationale: Optional[str] = None

    # Fulfillment (post-approval)
    gown_size: Optional[str] = None
    cap_size: Optional[str] = None
    mailing_street: Optional[str] = None
    mailing_city: Optional[str] = None
    mailing_state: Optional[str] = None
    mailing_zip: Optional[str] = None
    fulfillment_status: Optional[str] = None  # PENDING / PROCESSING / SHIPPED

    # Conversation log
    conversation_history: list = field(default_factory=list)

    # Audit trail
    audit_log: list = field(default_factory=list)

    # PDF path once generated
    pdf_path: Optional[str] = None


class ApplicationDatabase:
    """
    In-memory database for exception requests.
    In production, replace with PostgreSQL via SQLAlchemy or similar ORM.
    """

    def __init__(self):
        self._requests: dict[str, ExceptionRequest] = {}

    def save_request(self, request: ExceptionRequest) -> str:
        self._requests[request.id] = request
        return request.id

    def get_request(self, request_id: str) -> Optional[ExceptionRequest]:
        return self._requests.get(request_id)

    def get_request_by_username(self, username: str) -> Optional[ExceptionRequest]:
        for req in self._requests.values():
            if req.usf_username == username:
                return req
        return None

    def get_all_requests(self, status: Optional[str] = None) -> list[ExceptionRequest]:
        if status:
            return [r for r in self._requests.values() if r.status == status]
        return list(self._requests.values())

    def update_status(self, request_id: str, new_status: str,
                      reviewer_name: str = None, rationale: str = None):
        req = self._requests.get(request_id)
        if req:
            old_status = req.status
            req.status = new_status
            if new_status in ("APPROVED", "DENIED"):
                req.decided_at = datetime.now(timezone.utc).isoformat()
                req.reviewer_name = reviewer_name
                req.decision_rationale = rationale
            req.audit_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": f"Status changed: {old_status} -> {new_status}",
                "actor": reviewer_name or "system",
            })

    def update_fulfillment(self, request_id: str, gown_size: str, cap_size: str,
                           street: str, city: str, state: str, zip_code: str):
        req = self._requests.get(request_id)
        if req:
            req.gown_size = gown_size
            req.cap_size = cap_size
            req.mailing_street = street
            req.mailing_city = city
            req.mailing_state = state
            req.mailing_zip = zip_code
            req.fulfillment_status = "PENDING"
            req.audit_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "Fulfillment information submitted",
                "actor": req.usf_username,
            })


# Shared singleton database instance
db = ApplicationDatabase()
