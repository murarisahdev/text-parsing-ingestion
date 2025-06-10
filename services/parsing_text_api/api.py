# services/parsing_text_api/api.py
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from utils import publish_ingestion_event, save_file_to_gcs

router = APIRouter()


@router.post("/upload")
async def upload_file(tenant_id: str = Form(...), file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        gcs_path = await save_file_to_gcs(file, tenant_id, file_id)

        await publish_ingestion_event(
            {
                "type": "file",
                "tenant_id": tenant_id,
                "file_id": file_id,
                "filename": file.filename,
                "gcs_path": gcs_path,
            }
        )

        return JSONResponse({"status": "success", "file_id": file_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/url")
async def submit_url(tenant_id: str = Form(...), url: str = Form(...)):
    try:
        url_id = str(uuid.uuid4())
        await publish_ingestion_event(
            {"type": "url", "tenant_id": tenant_id, "url_id": url_id, "url": url}
        )

        return JSONResponse({"status": "success", "url_id": url_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
