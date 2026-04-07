from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Depends, BackgroundTasks, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from pypdf import PdfWriter
import uuid
import os

from tools import merger

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------------------
# ROUTES
# ---------------------------------------

@app.get("/merger", response_class=HTMLResponse)
def merger_page(request: Request):
    return templates.TemplateResponse(
        "merger.html",
        {
            "request": request,
        }
    )

@app.get("/")
def home(request: Request):
    context = {
        "request": request,
        "title": "PDF Merger - Home"
    }
    return templates.TemplateResponse("index.html", context)

@app.get("/contact")
def contact(request: Request):
    context = {
        "request": request,
        "title": "PDF Merger - Contact Us"
    }
    return templates.TemplateResponse("contact.html", context)

app.include_router(merger.router)