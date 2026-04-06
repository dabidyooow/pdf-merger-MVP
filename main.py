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

@app.get("/merger", response_class = HTMLResponse)
def merger_page(request: Request):
    return templates.TemplateResponse("merger.html", {"request": request, "menu": [{"name": "Merger"}]})


@app.get("/")
def home(request: Request):
    context = {
        "request": request,
        "menu": [{"name": "Home", "url": "/"}, {"name": "Merger", "url": "/merger"}, {"name": "Contact", "url": "/contact"}, {"name": "Privacy Policy", "url": "/privacy"}, {"name": "Terms of Service", "url": "/terms"}, {"name": "About", "url": "/about"}
        ],
        "title": "PDF Merger - Home"
    }
    return templates.TemplateResponse("index.html", context)

app.include_router(merger.router)

