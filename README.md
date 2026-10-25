# HR Identity Data Transformation

A focused Python project that validates and transforms an HR record into an Identity Provider (IdP) payload. All implementation code and the runnable sample are in the single module `src/identity_data_quality_demo/hr_transform.py`.

The transformation preserves the employee ID and full surname, derives a lowercase ASCII username from the first initial and surname, cleans the department, converts `YYYY/MM/DD` hire dates to ISO format, and trims and validates the manager email. Invalid or missing required values raise `ValueError`.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

## Run

```bash
uv sync --dev
uv run python -m identity_data_quality_demo.hr_transform
```

The sample record produces:

```text
{'external_id': 'EMP-9042', 'first_name': 'Maria', 'last_name': 'de la Cruz', 'username': 'mdelacruz', 'department': 'SEC OPS COMPLIANCE', 'start_date': '2026-03-15', 'manager_email': 'alex.riveria@company.com'}
```

## Tests

```bash
uv run pytest -v
```

Tests for the transformation are in `tests/test_hr_transform.py`.
