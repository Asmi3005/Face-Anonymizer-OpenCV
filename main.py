import os
import argparse
import cv2
import mediapipe as mp
import numpy as np

# VALID_EXTS=(".jpg",".jpeg",".png",".bmp")

emoji_img=cv2.imread("data/emoji.png",cv2.IMREAD_UNCHANGED)
#  face blur logic 
def process_img(img,face_detection,anonymize_type='blur',emoji_path=None):
    H,W,_=img.shape
    img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    out=face_detection.process(img_rgb)
    
    if out.detections is not None:
        for detection in out.detections:
            loc_data=detection.location_data
            bbox=loc_data.relative_bounding_box
            x1,y1,w,h=bbox.xmin,bbox.ymin,bbox.width,bbox.height

            # converting relative coordinates to pixel coordinates
            x1=int(x1*W)
            y1=int(y1*H)
            w=int(w*W)
            h=int(h*H)

            pad_x = int(w * 0.1)
            pad_y = int(h * 0.1)
            x1 = max(0, x1 + pad_x)
            y1 = max(0, y1 + pad_y)
            x2 = min(W, x1 + w - 2 * pad_x)
            y2 = min(H, y1 + h - 2 * pad_y)

            face_roi=img[y1:y2,x1:x2]
            if anonymize_type=='blur':
                face_roi=cv2.blur(face_roi,(20,20))
            elif anonymize_type=='pixelate':
                pixel_size = max(5, min(20, face_roi.shape[1] // 10))
                temp = cv2.resize(face_roi, (pixel_size, pixel_size), interpolation=cv2.INTER_LINEAR)
                face_roi = cv2.resize(temp, (x2 - x1, y2 - y1), interpolation=cv2.INTER_NEAREST)
            elif anonymize_type=='blackout':
                face_roi=cv2.rectangle(face_roi,(0,0),(x2-x1,y2-y1),(0,0,0),-1)
            elif anonymize_type=='emoji' and emoji_path is not None:
                emoji=emoji_path
                emoji = cv2.resize(emoji, (x2 - x1, y2 - y1))
                if emoji.shape[2] == 4:  
                    alpha = emoji[:, :, 3] / 255.0
                    alpha = alpha[..., np.newaxis]             
                    face_roi = (1 - alpha) * face_roi + alpha * emoji[:, :, :3]
                    face_roi = face_roi.astype(np.uint8)   
                else:
                    face_roi = emoji[:, :, :3]
            img[y1:y2,x1:x2]=face_roi
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            conf=detection.score[0]
            label=f"Face: {int(conf*100)}%"
            cv2.putText(img,label,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)
        return img

            

# argument parsing
args=argparse.ArgumentParser()
# args.add_argument("--mode",default='image')
# args.add_argument("--filePath",default="../pics_cv/standing.jpg")
# args.add_argument("--mode",default='video')
# args.add_argument("--filePath",default="../pics_cv/talking.mp4")
args.add_argument("--mode",default='webcam',choices=['image','video','webcam'])
args.add_argument("--filePath",default=None)
args.add_argument("--blurType",default='blur',choices=['blur','pixelate','emoji','blackout'])
args=args.parse_args()

# create output directory
output_dir='./output'
os.makedirs(output_dir,exist_ok=True)

# load face detection model
mp_face_detection=mp.solutions.face_detection
with mp_face_detection.FaceDetection(model_selection=1,min_detection_confidence=0.5) as face_detection:
    # image mode
    if args.mode in ["image"]:
        if args.filePath is None:
            print("Please provide --filePath for image mode.")
        else:
            img=cv2.imread(args.filePath)
            img=process_img(img,face_detection)
            cv2.imwrite(os.path.join(output_dir,'output.jpg'),img)
    
    # video mode
    elif args.mode in ['video']:
        if args.filePath is None:
            print("Please provide --filePath for video mode.")
        else:
            cap=cv2.VideoCapture(args.filePath)
            ret,frame=cap.read()
            output_video=cv2.VideoWriter(os.path.join(output_dir,'output.mp4'),
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    25,
                                    (frame.shape[1],frame.shape[0]))
            while ret:
                frame=process_img(frame,face_detection)
                output_video.write(frame)
                ret,frame=cap.read()
            

            cap.release()
            output_video.release()
    
    
    # webcam mode

    elif args.mode in['webcam']:
        cap=cv2.VideoCapture(0)
        ret,frame=cap.read()
        output_video=cv2.VideoWriter(os.path.join(output_dir,'webcam_output.mp4'),
                                     cv2.VideoWriter_fourcc(*'mp4v'),
                                     25,
                                     (frame.shape[1],frame.shape[0]))
        curr_blur_type=args.blurType
        print("Press 'b' for blur,'p' for pixelate,'k' for blackout,'e' for emoji,'q' to quit.")

        while ret:
            frame=process_img(frame,face_detection,curr_blur_type,emoji_img)
            cv2.imshow('Face obscuration (webcam)',frame)
            output_video.write(frame)
            
            key=cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key==ord('b'):
                curr_blur_type='blur'
                print("switched to BLUE mode")
            elif key==ord('p'):
                curr_blur_type='pixelate'
                print("switched to PIXELATE mode")
            elif key==ord('k'):
                curr_blur_type='blackout'
                print("switched to BLACKOUT mode")
            elif key==ord('e'):
                curr_blur_type='emoji'
                print("switched to EMOJI mode")

            ret,frame=cap.read()
        cap.release()
        output_video.release()
        cv2.destroyAllWindows()

