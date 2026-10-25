import pytest

from identity_data_quality_demo.hr_transform import (
    normalize_identifier,
    transform_user_data,
)


@pytest.fixture
def sample_hr_record() -> dict[str, str]:
    return {
        "id": "EMP-9042",
        "legal_name": "Maria de la Cruz",
        "department_code": "SEC-OPS & COMPLIANCE",
        "hire_date": "2026/03/15",
        "manager_email": " ALEX.RIVERIA@COMPANY.COM ",
    }


def test_direct_answer_transforms_sample_hr_record(sample_hr_record: dict[str, str]) -> None:
    assert transform_user_data(sample_hr_record) == {
        "external_id": "EMP-9042",
        "first_name": "Maria",
        "last_name": "de la Cruz",
        "username": "mdelacruz",
        "department": "SEC OPS COMPLIANCE",
        "start_date": "2026-03-15",
        "manager_email": "alex.riveria@company.com",
    }


def test_transform_preserves_multiword_surname(sample_hr_record: dict[str, str]) -> None:
    assert transform_user_data(sample_hr_record)["last_name"] == "de la Cruz"


def test_normalize_identifier_transliterates_accents_and_removes_punctuation() -> None:
    assert normalize_identifier("Élodie O'Neil-Smith") == "elodieoneilsmith"


def test_transform_rejects_missing_required_fields() -> None:
    with pytest.raises(ValueError, match="Missing required fields: legal_name"):
        transform_user_data(
            {
                "id": "EMP-1",
                "department_code": "IT",
                "hire_date": "2026/01/01",
                "manager_email": "lead@example.com",
            }
        )


@pytest.mark.parametrize("legal_name", ["Madonna", "  ", "  Prince  ", None])
def test_transform_rejects_names_without_given_and_family_parts(
    sample_hr_record: dict[str, str], legal_name: object
) -> None:
    sample_hr_record["legal_name"] = legal_name  # type: ignore[assignment]
    with pytest.raises(ValueError, match="legal_name"):
        transform_user_data(sample_hr_record)


@pytest.mark.parametrize("hire_date", ["15/03/2026", "2026-03-15", "2026/02/30", ""])
def test_transform_rejects_invalid_hire_date(
    sample_hr_record: dict[str, str], hire_date: str
) -> None:
    sample_hr_record["hire_date"] = hire_date
    with pytest.raises(ValueError, match="hire_date"):
        transform_user_data(sample_hr_record)


def test_transform_rejects_malformed_manager_email(sample_hr_record: dict[str, str]) -> None:
    sample_hr_record["manager_email"] = "not-an-email"
    with pytest.raises(ValueError, match="valid email"):
        transform_user_data(sample_hr_record)


def test_transform_rejects_empty_department(sample_hr_record: dict[str, str]) -> None:
    sample_hr_record["department_code"] = " -- & !! "
    with pytest.raises(ValueError, match="department_code"):
        transform_user_data(sample_hr_record)
