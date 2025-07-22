# 📸 Face Anonymizer Web App (OpenCV + MediaPipe + FastAPI + Streamlit)

A full-stack face anonymization tool supporting image, video, and **real-time webcam** processing using:

- OpenCV
- MediaPipe
- FastAPI backend
- Streamlit frontend (or HTML+JS UI)
- Real-time keyboard toggle for anonymization types

---

## ✅ Features

| Feature         | Description                                                             |
|------------------|-------------------------------------------------------------------------|
| `Blur`           | Gaussian blur on detected faces                                         |
| `Pixelate`       | Mosaic-style pixelation on faces                                        |
| `Blackout`       | Black box over detected faces                                           |
| `Emoji`          | Custom emoji overlay (transparent PNG supported)                       |
| `Webcam`         | Live webcam feed with toggle features          |
| `Image/Video`    | Upload media files and process instantly                                |
| `Download`       | Save the anonymized result to local machine or server                  |

---

## ⚙️ Requirements

- Python 3.7 – 3.10  
- OpenCV  
- MediaPipe  
- NumPy  
- FastAPI  
- Jinja2 (for HTML frontend)  
- Uvicorn (ASGI server)  
- Streamlit (if using streamlit UI)

Install dependencies:

```bash
pip install -r requirements.txt
