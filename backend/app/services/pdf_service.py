import subprocess
from pathlib import Path


LIBREOFFICE_PATH = (
    r"C:\Program Files\LibreOffice\program\soffice.exe"
)


def convert_pptx_to_pdf(
    pptx_path: str,
    output_dir: str
) -> str:

    pptx_path = Path(pptx_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        LIBREOFFICE_PATH,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(pptx_path)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed: {result.stderr}"
        )

    pdf_path = output_dir / f"{pptx_path.stem}.pdf"

    if not pdf_path.exists():
        raise RuntimeError(
            "LibreOffice completed, but the PDF was not created."
        )

    return str(pdf_path)