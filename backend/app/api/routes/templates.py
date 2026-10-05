from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os

from app.services.template_service import extract_placeholders
from app.services.mapping_service import map_template_fields
from app.services.certificate_service import replace_placeholders


router = APIRouter(
    prefix="/templates",
    tags=["Templates"]
)


@router.post("/upload")
async def upload_template(file: UploadFile = File(...)):

    suffix = os.path.splitext(file.filename)[1].lower()

    if suffix != ".pptx":
        raise HTTPException(
            status_code=400,
            detail="Only PPTX templates are supported for now."
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        placeholders = extract_placeholders(temp_path)

        return {
            "filename": file.filename,
            "placeholders": placeholders
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not process template: {str(exc)}"
        )

    finally:
        os.remove(temp_path)

@router.post("/map")
async def map_template(
    placeholders: list[str],
    columns: list[str]
):
    mapping = map_template_fields(
        placeholders,
        columns
    )

    return mapping

@router.post("/test-generate")
async def test_generate():

    template_path = "test_template.pptx"
    output_path = "test_output.pptx"

    recipient_data = {
        "Name": "Rahul Sharma",
        "Course": "AI Workshop",
        "Date": "03/10/2026",
        "Certificate_ID": "CERT-001"
    }

    try:
        replace_placeholders(
            template_path,
            output_path,
            recipient_data
        )

        return {
            "message": "Certificate generated successfully.",
            "output": output_path
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not generate certificate: {str(exc)}"
        )