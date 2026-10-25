"""Validate and transform HR data for identity provisioning."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any

_EMAIL_RE = re.compile(
    r"^[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?"
    r"(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+$",
    re.IGNORECASE,
)


def normalize_name(value: str) -> str:
    """Trim and collapse whitespace without changing capitalization."""
    if not isinstance(value, str):
        raise ValueError("name must be a string")

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError("name must not be empty")

    return normalized


def normalize_username(value: str) -> str:
    """Canonicalize and validate an email-style identity username."""
    if not isinstance(value, str):
        raise ValueError("username must be a string")

    normalized = value.strip().casefold()
    if not normalized or not _EMAIL_RE.fullmatch(normalized):
        raise ValueError("username must be a valid email address")

    return normalized


def parse_hr_date(value: str) -> date:
    """Parse the HR date format YYYY/MM/DD."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("hire_date must be a non-empty string")

    try:
        return datetime.strptime(value.strip(), "%Y/%m/%d").date()
    except ValueError as exc:
        raise ValueError("hire_date must use YYYY/MM/DD format") from exc


def normalize_identifier(value: str) -> str:
    """Generate a lowercase ASCII identifier without punctuation."""
    if not isinstance(value, str):
        raise ValueError("identifier source must be a string")

    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", ascii_value.casefold())


def transform_user_data(hr_data: dict[str, Any]) -> dict[str, Any]:
    """Transform and validate an HR record for an IdP."""
    if not isinstance(hr_data, dict):
        raise ValueError("HR record must be an object")

    required_fields = (
        "id",
        "legal_name",
        "department_code",
        "hire_date",
        "manager_email",
    )
    missing = [field for field in required_fields if field not in hr_data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    try:
        legal_name = normalize_name(hr_data["legal_name"])
    except ValueError as exc:
        raise ValueError(f"legal_name is invalid: {exc}") from exc

    name_parts = legal_name.split()
    if len(name_parts) < 2:
        raise ValueError("legal_name must contain a first name and surname")

    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:])
    username = normalize_identifier(first_name[0] + last_name)
    if not username:
        raise ValueError("Could not generate a valid username")

    department_code = hr_data["department_code"]
    if not isinstance(department_code, str):
        raise ValueError("department_code must be a string")

    department = re.sub(r"[^A-Za-z0-9 ]", " ", department_code)
    department = re.sub(r"\s+", " ", department).strip()
    if not department:
        raise ValueError("department_code must not be empty")

    start_date = parse_hr_date(hr_data["hire_date"]).isoformat()
    manager_email = normalize_username(hr_data["manager_email"])

    return {
        "external_id": hr_data["id"],
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "department": department,
        "start_date": start_date,
        "manager_email": manager_email,
    }


if __name__ == "__main__":
    hr_user_payload = {
        "id": "EMP-9042",
        "legal_name": "Maria de la Cruz",
        "department_code": "SEC-OPS & COMPLIANCE",
        "hire_date": "2026/03/15",
        "manager_email": " ALEX.RIVERIA@COMPANY.COM ",
    }

    print(transform_user_data(hr_user_payload))
