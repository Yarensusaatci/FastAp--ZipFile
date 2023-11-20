from collections import _OrderedDictItemsView
from turtle import color, left
from api import api_router
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from api.image_downloader import get_db
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.models import OpenAPI
from fastapi.openapi.utils import get_openapi
import tkinter as TK

app = FastAPI(title='Mindsite Backend Developer Assignment')

#__init__.py then image_downloader.py
app.include_router(api_router)

# In bonus, I added redoc
# Redoc endpoint to serve the documentation
@app.get("/redoc", response_class=HTMLResponse)
async def redoc_html():
    openapi_schema = get_openapi(title="Mindsite", version="1.0.0", routes=app.routes)
    return get_redoc_html(openapi_schema)

def get_redoc_html(openapi_schema: dict) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>Redoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/redoc@next/dist/redoc.min.css" rel="stylesheet">
        <style>
          :root {
            --color: #3498db; 
          }
          .redoc-wrap {
            _OrderedDictItemsView-left: 5px solid var(--colors-primary); 
          }
        </style>
      </head>
      <body>
        <div id="redoc-container"></div>
        <script src="https://cdn.jsdelivr.net/npm/redoc@next/dist/redoc.min.js"> </script>
        <script>
          Redoc.init('http://localhost:8000/openapi.json')
        </script>
      </body>
    </html>
    """

# Serve OpenAPI JSON at /openapi.json
@app.get("/openapi.json")
async def get_openapi_endpoint():
    return JSONResponse(content=get_openapi(title="Mindsite", version="1.0.0", routes=app.routes))
