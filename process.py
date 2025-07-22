import os
import cv2
import mediapipe as mp
import numpy as np
import uuid

# Load the emoji image once
emoji_img = cv2.imread("data/emoji.png", cv2.IMREAD_UNCHANGED)

def _apply_anonymization(face_roi, anonymize_type):
    """Applies the selected anonymization effect to the face region of interest."""
    if anonymize_type == 'blur':
        return cv2.blur(face_roi, (25, 25))
    elif anonymize_type == 'pixelate':
        h, w, _ = face_roi.shape
        if h <= 0 or w <= 0: return face_roi
        pixel_size = max(1, w // 8)
        temp = cv2.resize(face_roi, (pixel_size, pixel_size), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
    elif anonymize_type == 'blackout':
        return np.zeros_like(face_roi)
    elif anonymize_type == 'emoji' and emoji_img is not None:
        h, w, _ = face_roi.shape
        if h <= 0 or w <= 0: return face_roi
        emoji_resized = cv2.resize(emoji_img, (w, h))
        
        if emoji_resized.shape[2] == 4:  # If emoji has alpha channel
            alpha = emoji_resized[:, :, 3] / 255.0
            alpha = alpha[..., np.newaxis]
            blended = (1 - alpha) * face_roi + alpha * emoji_resized[:, :, :3]
            return blended.astype(np.uint8)
        else:
            return emoji_resized[:, :, :3]
    return face_roi

def process_image(img, face_detection, anonymize_type='blur'):
    """Detects faces in a single image frame and applies anonymization."""
    H, W, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    out = face_detection.process(img_rgb)

    if out.detections:
        for detection in out.detections:
            loc_data = detection.location_data
            bbox = loc_data.relative_bounding_box
            
            x1, y1, w, h = int(bbox.xmin * W), int(bbox.ymin * H), int(bbox.width * W), int(bbox.height * H)
            
            # Ensure coordinates are within image bounds
            x2, y2 = x1 + w, y1 + h
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(W, x2), min(H, y2)

            if x1 < x2 and y1 < y2:
                face_roi = img[y1:y2, x1:x2]
                anonymized_face = _apply_anonymization(face_roi, anonymize_type)
                img[y1:y2, x1:x2] = anonymized_face
    return img

def process_file(input_path, blur_type='blur'):
    """
    Processes an image or video file, always saves the output, and returns the path.
    """
    filename = os.path.basename(input_path)
    output_filename = f"{uuid.uuid4().hex}_{filename}"
    output_path = os.path.join("output", output_filename)

    mp_face_detection = mp.solutions.face_detection
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        
        if input_path.lower().endswith((".jpg", ".jpeg", ".png")):
            img = cv2.imread(input_path)
            if img is None:
                raise ValueError(f"Could not read image from path: {input_path}")
            
            processed_img = process_image(img, face_detection, blur_type)
            cv2.imwrite(output_path, processed_img)
            return output_path

        elif input_path.lower().endswith((".mp4", ".avi", ".mov")):
            cap = cv2.VideoCapture(input_path)
            ret, frame = cap.read()
            if not ret:
                raise ValueError(f"Could not read video from path: {input_path}")

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_video = cv2.VideoWriter(output_path, fourcc, 25, (frame.shape[1], frame.shape[0]))

            while ret:
                processed_frame = process_image(frame, face_detection, blur_type)
                out_video.write(processed_frame)
                ret, frame = cap.read()

            cap.release()
            out_video.release()
            return output_path

        else:
            raise ValueError(f"Unsupported file type: {input_path}")
