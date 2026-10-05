from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.n8n_service import trigger_n8n

import os
import tempfile
import shutil
import uuid

from app.services.recipient_service import read_recipient_file
from app.services.validator import validate_recipients
from app.services.template_service import extract_placeholders
from app.services.mapping_service import map_template_fields
from app.services.batch_service import generate_certificates


router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"]
)


@router.post("/generate")
async def generate(
    recipients_file: UploadFile = File(...),
    template_file: UploadFile = File(...)
):

    recipient_suffix = os.path.splitext(
        recipients_file.filename
    )[1].lower()

    template_suffix = os.path.splitext(
        template_file.filename
    )[1].lower()

    if recipient_suffix not in [".csv", ".xlsx"]:
        raise HTTPException(
            status_code=400,
            detail="Recipients file must be CSV or XLSX."
        )

    if template_suffix != ".pptx":
        raise HTTPException(
            status_code=400,
            detail="Template must be a PPTX file."
        )

    temp_dir = tempfile.mkdtemp()
    batch_id = uuid.uuid4().hex

    output_dir = os.path.join(
        "output",
        batch_id
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    try:

        # -----------------------------
        # Save uploaded recipient file
        # -----------------------------

        recipient_path = os.path.join(
            temp_dir,
            f"recipients{recipient_suffix}"
        )

        with open(recipient_path, "wb") as file:
            shutil.copyfileobj(
                recipients_file.file,
                file
            )

        # -----------------------------
        # Save uploaded template
        # -----------------------------

        template_path = os.path.join(
            temp_dir,
            f"template{template_suffix}"
        )

        with open(template_path, "wb") as file:
            shutil.copyfileobj(
                template_file.file,
                file
            )

        # -----------------------------
        # Read recipients
        # -----------------------------

        dataframe = read_recipient_file(
            recipient_path
        )

        # -----------------------------
        # Validate recipients
        # -----------------------------

        validation = validate_recipients(
            dataframe
        )

        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "stage": "validation",
                    "validation": validation
                }
            )

        # -----------------------------
        # Detect placeholders
        # -----------------------------

        placeholders = extract_placeholders(
            template_path
        )

        # -----------------------------
        # Map fields
        # -----------------------------

        mapping = map_template_fields(
            placeholders,
            list(dataframe.columns)
        )

        if mapping["missing"]:

            raise HTTPException(
                status_code=400,
                detail={
                    "stage": "mapping",
                    "mapping": mapping
                }
            )

        # -----------------------------
        # Generate certificates
        # -----------------------------

        results = generate_certificates(
            dataframe,
            template_path,
            output_dir
        )

        for result in results:

            if result["status"] == "success":

                filename = os.path.basename(
                    result["certificate"]
                )

                result["certificate_url"] = (
                    f"/certificates/file/{batch_id}/{filename}"
                )

        successful_results = [
            result
            for result in results
            if result["status"] == "success"
        ]

        n8n_result = trigger_n8n(
            batch_id,
            successful_results
        )


        return {
            "message": "Certificate generation completed.",
            "batch_id": batch_id,
            "total_recipients": len(dataframe),
            "placeholders": placeholders,
            "mapping": mapping,
            "n8n": n8n_result,
            "results": results
        }
    
    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Certificate generation failed: {str(exc)}"
        )

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

@router.get("/file/{batch_id}/{filename}")
async def get_certificate(
    batch_id: str,
    filename: str
):

    file_path = os.path.join(
        "output",
        batch_id,
        filename
    )

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="Certificate not found."
        )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )