import pandas as pd
from pathlib import Path


def read_recipient_file(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)

    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path)

    raise ValueError("Unsupported file format. Use CSV or XLSX.")