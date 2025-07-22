from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import uuid
import os
import base64
import cv2
import numpy as np
import webbrowser
import mediapipe as mp

from process import process_file, process_image

app = FastAPI()

# --- Setup ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Initialize MediaPipe Face Detection once to save resources
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

@app.on_event("startup")
def open_browser():
    """Opens the browser on startup."""
    webbrowser.open("http://127.0.0.1:8000")

# --- HTML Routes ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API Routes ---
@app.post("/upload/")
async def upload(
    file: UploadFile = File(...),
    blur_type: str = Form("blur")
):
    """
    Handles file uploads, processes them, and returns the result.
    This version includes robust error handling and cleanup.
    """
    temp_input_path = f"uploads/{uuid.uuid4().hex}_{file.filename}"
    
    try:
        # Save the uploaded file temporarily
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file and get the path to the output
        output_path = process_file(temp_input_path, blur_type)

        # Return the processed file as a response
        return FileResponse(
            path=output_path,
            filename=os.path.basename(output_path),
            media_type="application/octet-stream"
        )
    except Exception as e:
        # If any error occurs during processing, return a JSON error response
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process file: {str(e)}"}
        )
    finally:
        # IMPORTANT: Always clean up the temporary uploaded file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

@app.post("/process_frame/")
async def process_frame_endpoint(
    blur_type: str = Form("blur"),
    image_data: str = Form(...)
):
    """Handles processing a single base64 encoded image from the webcam."""
    try:
        # Decode the base64 image
        header, encoded = image_data.split(",", 1)
        binary = base64.b64decode(encoded)
        np_arr = np.frombuffer(binary, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Process the image data in memory
        processed_img = process_image(img, face_detection, blur_type)

        # Encode the processed image back to base64 to send to the frontend
        _, buffer = cv2.imencode('.png', processed_img)
        encoded_img = base64.b64encode(buffer).decode("utf-8")

        return JSONResponse(content={"image_data": f"data:image/png;base64,{encoded_img}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
