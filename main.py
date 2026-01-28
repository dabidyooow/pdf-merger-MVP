from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Depends, BackgroundTasks, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from pypdf import PdfWriter
import uuid
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

API_KEY = "dangerous_api_key"  # Replace with your actual API key

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid API Key"
        )


@app.get("/", response_class = HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def validate_pdfs(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code = 400, detail = "At least two PDF files are required for merging.")
    for file in files:
        if not file.filename.lower().endswith("pdf"):
            raise HTTPException(status_code = 400, detail=f"File {file.filename} is not a PDF.")
        
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)

        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code= 413, detail=f"{file.filename} exceeds 5mb limit.")
        
    return files
    
def delete_file(path: str):
    if os.path.exists(path):
        os.remove(path)

    
@app.post("/merge")
async def merge_pdfs(background_tasks: BackgroundTasks,
                     files: List[UploadFile] = Depends(validate_pdfs),
                     _: str = Depends(verify_api_key)
                     ):
    writer = PdfWriter()
    saved_files = []

    for file in files:
        temp_name = f"{uuid.uuid4()}.pdf"
        temp_path = os.path.join(UPLOAD_DIR, temp_name)

        with open(temp_path, "wb") as f:
            f.write(await file.read())

        writer.append(temp_path)
        saved_files.append(temp_path)

    output_path = os.path.join(OUTPUT_DIR, f"merged_{uuid.uuid4()}.pdf")

    with open(output_path, "wb") as f:
        writer.write(f)

    for path in saved_files:
        os.remove(path)

    background_tasks.add_task(delete_file, output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="merged.pdf"
    )