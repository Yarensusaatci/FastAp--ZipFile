# Yaren Su Saatçı

Expected REST API specification is in image_downloader.py :

### `POST - /downloads`

### `GET - /downloads/<download_id>/status`

### `GET - /downloads/<download_id>`

I used SQLite and objects stored there. I used Turkey timezone.

SQLALCHEMY_DATABASE_URL is in database.py 

In scraper.py, I used get_image_urls function.

Downloaded image number is limited to 50.

I used local file to store images and I store it in VSCode.

There is a file_path which is a downloaded file name in Vscode. Also, you can use "unzip {file_path}" comment for unzip file in VSCode terminal.

There is a test_main.py file for testing and I used pytest.

I used recdoc for documentation.

I added some new libraries to requirements.txt

Additionally, I used progress field for downloading images. 100 means download is finished. 
