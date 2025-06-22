# Real-Time Face Blur with OpenCV and MediaPipe

A Python application to detect and blur human faces in images, videos, or live webcam streams.

## Features
- Face detection using MediaPipe
- Face blurring using OpenCV
- Supports:
  - Static images
  - Pre-recorded videos
  - Live webcam feed

## Usage

```bash
# For image input
python main.py --mode image --filePath pics_cv/standing.jpg

# For video input
python main.py --mode video --filePath pics_cv/talking.mp4

# For webcam input
python main.py --mode webcam
