import yt_dlp
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel
import os
import urllib.parse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} deleted.")
    else:
        print(f"File {file_path} not found for deletion.")

# Hook function to get file name
def hook(d):
    if d['status'] == 'finished':
        global downloaded_file_name
        downloaded_file_name = d['filename']
        print(f"Downloaded file: {d['filename']}")

class DownloadRequest(BaseModel):
    youtube_url: str

@app.post("/download-mp3")
async def download_mp3(request: DownloadRequest):
    youtube_url = request.youtube_url
    global downloaded_file_name
    downloaded_file_name = "unknown.mp3"  # Default file name

    # Ensure the static directory exists

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'%(title)s.%(ext)s',  # Save directly to static folder
        'noplaylist': True,
        'progress_hooks': [hook],
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    # Encode file name for URL
    encoded_file_name = urllib.parse.quote(downloaded_file_name)

    # Return the file path for download
    file_path = downloaded_file_name[:-4] + "mp3"
    print(file_path)
    if file_path and os.path.exists(file_path):
        return {"file_name": file_path}
    else:
        return {"error": "Failed to download file"}


@app.post("/get-mp3")
async def get_mp3(request: DownloadRequest, background_tasks: BackgroundTasks):
    # Decode the file name
    file_name = urllib.parse.unquote(request.youtube_url)
    print(file_name)
    # file_path = os.path.join("static", file_name)
    file_path = file_name
    if os.path.exists(file_path):
        background_tasks.add_task(delete_file, file_path)
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")