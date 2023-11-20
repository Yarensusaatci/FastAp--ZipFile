# I used pytest
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_download_task():
    # Test the /downloads endpoint

    # Make a request to create a download task
    response = client.post("/downloads", json={"url": "http://example.com/image.jpg"})

    # Check that the response is successful (HTTP 200 OK)
    assert response.status_code == 200

    # Check that the response contains the download_id
    assert "download_id" in response.json()

@pytest.mark.asyncio
async def test_get_download_status():
    # Test the /downloads/{download_id}/status endpoint

    # Create a download task for testing
    response_create = client.post("/downloads", json={"url": "http://example.com/image.jpg"})
    download_id = response_create.json()["download_id"]

    # Make a request to get the download status
    response = client.get(f"/downloads/{download_id}/status")

    # Check that the response is successful (HTTP 200 OK)
    assert response.status_code == 200

    # Check that the response contains the expected fields
    assert "download_id" in response.json()
    assert "started_at" in response.json()
    assert "status" in response.json()
    assert "progress" in response.json()

@pytest.mark.asyncio
async def test_download_images():
    # Test the /downloads/{download_id} endpoint

    # Create a download task for testing
    response_create = client.post("/downloads", json={"url": "http://example.com/image.jpg"})
    download_id = response_create.json()["download_id"]

    # Make a request to download the images
    response = client.get(f"/downloads/{download_id}")

    # Check that the response is either 200 (finished) or 423 (in progress)
    assert response.status_code in [200, 423]

    # If the response is 200, check that it contains the zip file
    if response.status_code == 200:
        assert response.headers["content-type"] == "application/zip"
        assert response.headers["content-disposition"].startswith(f"attachment; filename={download_id}.zip")
