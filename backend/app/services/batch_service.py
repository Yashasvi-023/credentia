import os
import re
import tempfile
from pathlib import Path

import pandas as pd

from app.services.certificate_service import replace_placeholders
from app.services.pdf_service import convert_pptx_to_pdf


def sanitize_filename(value: str) -> str:
    value = str(value).strip()

    value = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        value
    )

    value = re.sub(
        r"\s+",
        "_",
        value
    )

    return value


def generate_certificates(
    dataframe: pd.DataFrame,
    template_path: str,
    output_dir: str
) -> list[dict]:

    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    results = []

    for index, row in dataframe.iterrows():

        recipient = row.to_dict()

        name = sanitize_filename(
            recipient.get("Name", f"recipient_{index + 1}")
        )

        certificate_id = recipient.get(
            "Certificate_ID"
        )

        if pd.isna(certificate_id):
            certificate_id = f"{index + 1:04d}"

        certificate_id = sanitize_filename(
            certificate_id
        )

        base_name = f"{name}_{certificate_id}"

        pptx_path = output_path / f"{base_name}.pptx"

        try:
            replace_placeholders(
                template_path,
                str(pptx_path),
                recipient
            )

            pdf_path = convert_pptx_to_pdf(
                str(pptx_path),
                str(output_path)
            )

            results.append({
                "row": index + 2,
                "name": str(recipient.get("Name", "")),
                "email": str(recipient.get("Email", "")),
                "certificate": str(pdf_path),
                "status": "success"
            })

        except Exception as exc:

            results.append({
                "row": index + 2,
                "name": str(recipient.get("Name", "")),
                "email": str(recipient.get("Email", "")),
                "certificate": None,
                "status": "failed",
                "error": str(exc)
            })

            # Make sure a partially generated PPTX
            # doesn't remain after a failure.
            if pptx_path.exists():
                os.remove(pptx_path)

    # Remove intermediate PPTX files after
    # successful PDF generation.
    for file in output_path.glob("*.pptx"):
        file.unlink()

    return results