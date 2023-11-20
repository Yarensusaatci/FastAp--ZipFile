from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import shutil
import os
from starlette.responses import StreamingResponse
from tempfile import NamedTemporaryFile
import requests
from zipfile import ZipFile
import zipfile
from scraper import get_image_urls
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import models
import asyncio
import pytz

turkey_timezone = pytz.timezone('Europe/Istanbul')

current_utc_time = datetime.utcnow()

current_turkey_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(tz=turkey_timezone)

router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

download_tasks = {}

class DownloadRequest(BaseModel):
    url: str

class DownloadStatus(BaseModel):
    download_id: str
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    download_url: Optional[str]
    progress: Optional[float]

async def background_download_images(db: Session, download_id: str, url: str, background_tasks: BackgroundTasks):
    try:
        temp_dir = f"temp_images_{download_id}"
        os.makedirs(temp_dir, exist_ok=True)

        image_urls = await get_image_urls(url)
        
        total_images = min(len(image_urls), 50)
        images_downloaded = 0

        for index, image_url in enumerate(image_urls[:50]):
            response = requests.get(image_url)
            response.raise_for_status()

            image_path = os.path.join(temp_dir, f"image_{index}.jpg")
            with open(image_path, 'wb') as image_file:
                image_file.write(response.content)

           
            images_downloaded += 1
            progress = (images_downloaded / total_images) * 100

            # Update progress in the database
            download_db = db.query(Image).filter(Image.id == download_id).first()
            download_db.progress = progress
            db.commit()

        zip_path = f"downloaded_images_{download_id}.zip"
        with ZipFile(zip_path, 'w') as zip_file:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, temp_dir)
                    zip_file.write(file_path, arc_name)

        shutil.rmtree(temp_dir)

        download_db = db.query(Image).filter(Image.id == download_id).first()
        download_db.status = "FINISHED"
        download_db.finished_at = current_turkey_time
        download_db.file_path = zip_path  # Eklendi
        db.commit()
    except Exception as e:
        print(f"Hata oluştu: {e}")
        download_db = db.query(Image).filter(Image.id == download_id).first()
        download_db.status = "ERROR"
        download_db.finished_at = current_turkey_time
        db.commit()
        return
# I added progress in response. 100 means download finished.

#changes url to id
@router.post("/downloads", response_model=dict)
async def start_downloading_images(request: DownloadRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    url = request.url

    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    download_id = str(uuid.uuid4())

    # Save the download info in the database
    download_db = Image(
        id=download_id,
        started_at=current_turkey_time,
        status="IN_PROGRESS",
        progress=0,
        file_path=""  
    )
    db.add(download_db)
    db.commit()
    
    # asyncio.create_task 
    asyncio.create_task(background_download_images(db, download_id, url, background_tasks))

    return {"download_id": download_id}

# returns download status
@router.get('/downloads/{download_id}/status', response_model=DownloadStatus)
async def get_download_status(download_id: str, db: Session = Depends(get_db)):
    download_db = db.query(Image).filter(Image.id == download_id).first()

    if not download_db:
        raise HTTPException(status_code=404, detail="Download not found")

    if download_db.status == "IN_PROGRESS":
        finished_at = None
        download_url = None
    else:
        finished_at = download_db.finished_at
        download_url = f"http://localhost:8000/downloads/{download_id}"

    return {
        "download_id": download_id,
        "started_at": download_db.started_at,
        "finished_at": finished_at,
        "status": download_db.status,
        "download_url": download_url,
        "progress": download_db.progress,
    }

# if progress finished, you should click Download File button
@router.get("/downloads/{download_id}")
async def download_images(download_id: str, db: Session = Depends(get_db)):
    # Check if the download_id exists
    download_db = db.query(Image).filter(Image.id == download_id).first()

    if not download_db:
        raise HTTPException(status_code=404, detail="Download not found")

    temp_dir = f"temp_images_{download_id}"

    try:
        if download_db.status == "FINISHED":
            # Return the zip file as a streaming response
            zip_path = f"downloaded_images_{download_id}.zip"
            with open(zip_path, 'rb') as zip_file:
                return StreamingResponse(
                    iter([zip_file.read()]),
                    media_type="application/zip",
                    headers={"Content-Disposition": f"attachment; filename={download_id}.zip"}
                )
        elif download_db.status == "IN_PROGRESS":
            # Indicate that downloading is not finished yet
            return JSONResponse(content={"error": "Downloading is in progress. Please check later."}, status_code=423)
        else:
            # Indicate that an error occurred while downloading images
            return JSONResponse(content={"error": "An error occurred while downloading images."}, status_code=500)

    except FileNotFoundError:
        # Indicate that the downloaded zip file is not found
        return HTTPException(status_code=404, detail="Downloaded zip file not found")

    finally:
        # Clean up: Remove temporary directory and files
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(router, host='0.0.0.0', port=8000)
