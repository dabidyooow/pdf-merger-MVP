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
templates.env.cache = {} # Disable Jinja2 caching for development
templates.env.auto_reload = True

app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------------------
# ROUTES
# ---------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/merger", response_class=HTMLResponse)
def merger_page(request: Request):
    return templates.TemplateResponse(
        "merger.html",
        {"request": request}
    )

app.include_router(merger.router)