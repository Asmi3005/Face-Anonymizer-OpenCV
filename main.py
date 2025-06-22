import os
import argparse
import cv2
import mediapipe as mp


#  face blur logic 
def process_img(img,face_detection):
    H,W,_=img.shape
    img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    out=face_detection.process(img_rgb)
    
    if out.detections is not None:
        for detection in out.detections:
            loc_data=detection.location_data
            bbox=loc_data.relative_bounding_box
            x1,y1,w,h=bbox.xmin,bbox.ymin,bbox.width,bbox.height

            # converting to pixel coordinates
            x1=int(x1*W)
            y1=int(y1*H)
            w=int(w*W)
            h=int(h*H)

            # applying blur to only face region
            img[y1:y1+h,x1:x1+w,:]=cv2.blur(img[y1:y1+h,x1:x1+w,:],(20,20))
    return img

# argument parsing
args=argparse.ArgumentParser()
# args.add_argument("--mode",default='image')
# args.add_argument("--filePath",default="../pics_cv/standing.jpg")
# args.add_argument("--mode",default='video')
# args.add_argument("--filePath",default="../pics_cv/talking.mp4")
args.add_argument("--mode",default='webcam',choices=['image','video','webcam'])
args.add_argument("--filePath",default=None)
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
        while ret:
            frame=process_img(frame,face_detection)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            ret,frame=cap.read()
        cap.release()
        cv2.destroyAllWindows()

