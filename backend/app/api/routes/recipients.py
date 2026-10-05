from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os

from app.services.recipient_service import read_recipient_file
from app.services.validator import validate_recipients


router = APIRouter(prefix="/recipients", tags=["Recipients"])


@router.post("/upload")
async def upload_recipients(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1].lower()

    if suffix not in [".csv", ".xlsx"]:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported."
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        dataframe = read_recipient_file(temp_path)
        validation = validate_recipients(dataframe)

        return {
            "filename": file.filename,
            "rows": len(dataframe),
            "columns": list(dataframe.columns),
            "validation": validation
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not process file: {str(exc)}"
        )

    finally:
        os.remove(temp_path)