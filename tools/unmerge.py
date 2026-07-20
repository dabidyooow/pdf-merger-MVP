from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Depends, BackgroundTasks, Header
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
from typing import List
from pypdf import PdfReader, PdfWriter
import os
import uuid
import zipfile
import shutil

from tools.merger import verify_api_key

router = APIRouter()

templates = Jinja2Templates(directory="templates")

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def delete_files(path: str):
    if os.path.exists(path):
        os.remove(path)

@router.get("/split", response_class=HTMLResponse)
async def split_page(request: Request):
    return templates.TemplateResponse(
        "unmerge.html",
        {"request": request}
    )

def validate_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed."
        )
    
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the maximum limit of {MAX_FILE_SIZE / (1024 * 1024)} MB."
        )
    return file


@router.post("/pdf-info")
async def pdf_info(
        file: UploadFile = Depends(validate_pdf),
        _:str = Depends(verify_api_key)
):
    temp_name = f"{uuid.uuid4()}.pdf"
    temp_path = os.path.join(UPLOAD_DIR, temp_name)

    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        reader = PdfReader(temp_path)

        return {
            "filename": file.filename,
            "pages": len(reader.pages)
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/split")
async def split_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = Depends(validate_pdf),
    _: str = Depends(verify_api_key)
):
    temp_name = f"{uuid.uuid4()}.pdf"
    temp_path = os.path.join(UPLOAD_DIR, temp_name)

    output_folder = os.path.join(OUTPUT_DIR, str(uuid.uuid4()))
    os.makedirs(output_folder, exist_ok=True)

    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        reader = PdfReader(temp_path)

        for i, page in enumerate(reader.pages):

            writer = PdfWriter()
            writer.add_page(page)

            page_path = os.path.join(
                output_folder,
                f"page_{i+1}.pdf"
            )

            with open(page_path, "wb") as out:
                writer.write(out)

        zip_path = output_folder + ".zip"

        with zipfile.ZipFile(zip_path, "w") as zipf:

            for filename in os.listdir(output_folder):

                file_path = os.path.join(output_folder, filename)

                zipf.write(
                    file_path,
                    arcname=filename
                )

        background_tasks.add_task(shutil.rmtree, output_folder)
        background_tasks.add_task(delete_files, zip_path)

        return FileResponse(
            zip_path,
            filename="split_pages.zip",
            media_type="application/zip"
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
