from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

from api import api_router

app = FastAPI(title='Mindsite Backend Developer Assignment')

# Include the API router
app.include_router(api_router)

# Redoc endpoint to serve the documentation
@app.get("/redoc", response_class=HTMLResponse)
async def redoc_html():
    openapi_schema = get_openapi(title="Mindsite", version="1.0.0", routes=app.routes)
    return get_redoc_html(openapi_schema)

# Serve OpenAPI JSON at /openapi.json
@app.get("/openapi.json")
async def get_openapi_endpoint():
    return JSONResponse(content=get_openapi(title="Mindsite", version="1.0.0", routes=app.routes))
