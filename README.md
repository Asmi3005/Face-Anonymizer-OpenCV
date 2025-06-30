# 📸 Face Anonymizer with OpenCV and MediaPipe

This project provides a real-time face anonymization tool using OpenCV and MediaPipe, with support for:

- Blur  
- Pixelate  
- Blackout  
- Emoji overlay  
- Webcam, image, and video
- Real-time keyboard toggles for anonymization type  

---

##  Features

| Feature      | Description                                       |
|--------------|---------------------------------------------------|
| `Blur`       | Smooth face area using Gaussian-style box blur    |
| `Pixelate`   | Obscure face using mosaic block effect            |
| `Blackout`   | Fully black out the detected face                 |
| `Emoji`      | Overlay custom emoji PNG with transparency        |
| `Live Toggle`| Switch modes in real-time with keys: `b`, `p`, `k`, `e`, `q` |
| `Modes`      | Process webcam, image file, video file            |

---

## 🛠️ Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy

Install dependencies:

```bash
pip install opencv-python mediapipe numpy


## Usage

```bash
# For image input
python main.py --mode image --filePath pics_cv/standing.jpg

# For video input
python main.py --mode video --filePath pics_cv/talking.mp4

# For webcam input
python main.py --mode webcam
