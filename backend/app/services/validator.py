import re
import pandas as pd


REQUIRED_COLUMNS = {"Name", "Email"}


def validate_email(email: str) -> bool:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


def validate_recipients(dataframe: pd.DataFrame) -> dict:
    errors = []

    # 1. Required columns
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        errors.append({
            "type": "missing_columns",
            "columns": list(missing_columns)
        })

        return {
            "valid": False,
            "errors": errors
        }

    # 2. Empty names
    for index, row in dataframe.iterrows():
        name = row["Name"]

        if pd.isna(name) or str(name).strip() == "":
            errors.append({
                "row": index + 2,
                "field": "Name",
                "message": "Name is empty."
            })

    # 3. Invalid emails
    for index, row in dataframe.iterrows():
        email = row["Email"]

        if pd.isna(email) or not validate_email(str(email).strip()):
            errors.append({
                "row": index + 2,
                "field": "Email",
                "message": "Invalid email address."
            })

    # 4. Duplicate emails
    email_series = (
        dataframe["Email"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
    )

    duplicates = email_series[email_series.duplicated(keep=False)]

    for email in duplicates.unique():
        rows = [
            index + 2
            for index, value in email_series.items()
            if value == email
        ]

        errors.append({
            "field": "Email",
            "value": email,
            "rows": rows,
            "message": "Duplicate email address."
        })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "total_rows": len(dataframe)
    }