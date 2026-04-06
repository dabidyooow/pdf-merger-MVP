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


@app.get("/", response_class = HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "menu": [{"name": "Home"}]})

@app.get("/contact", response_class = HTMLResponse)
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request, "menu": [{"name": "Contact"}]})
@app.get("/privacy", response_class = HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request, "menu": [{"name": "Privacy Policy"}]})

@app.get("/terms", response_class = HTMLResponse)
def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request, "menu": [{"name": "Terms of Service"}]})
@app.get("/about", response_class = HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "menu": [{"name": "About"}]})
app.include_router(merger.router)

