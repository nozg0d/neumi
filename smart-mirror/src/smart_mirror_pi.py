import cv2
import time
import datetime
from camera import Camera
from facial_tracking import FacialTracker
from utils import resize_image, draw_rectangle
# from gpiozero import MotionSensor, Button
# from signal import pause
# import openai
import numpy as np
# Google Cloud Vision API integration
from google.cloud import vision
import io
import os

# Set your OpenAI API key here
# openai.api_key = 'YOUR_OPENAI_API_KEY'

# GPIO pin numbers (adjust as needed)
# MOTION_SENSOR_PIN = 4  # Example GPIO pin for PIR motion sensor
# BUTTON_PIN = 17        # Example GPIO pin for hand sign/photo button

# Initialize hardware
# pir = MotionSensor(MOTION_SENSOR_PIN)
# photo_button = Button(BUTTON_PIN)

# Initialize camera and facial tracker
camera = Camera(camera_index=0)
tracker = FacialTracker()

# Set the path to your downloaded JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "d:/neumi/smart-mirror/src/neumi-462912-63a98f319d46.json"

# Initialize Vision API client
vision_client = vision.ImageAnnotatorClient()

# Helper: Draw date, time, and clock on frame
def draw_datetime(frame):
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')
    cv2.putText(frame, date_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.putText(frame, time_str, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    return frame

# Helper: Analyze face with OpenAI (dummy for now)
def analyze_face_with_openai(face_img):
    # Return dummy result for now
    return "Analysis: Stress level low, mild acne detected."

# Helper: Analyze face with Vision API
def analyze_face_with_vision_api(face_img):
    # Save face image temporarily
    temp_filename = "temp_face.jpg"
    cv2.imwrite(temp_filename, face_img)
    with io.open(temp_filename, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations
    if labels:
        return ", ".join([label.description for label in labels])
    return "No labels detected."

# Photo capture callback
captured_photos = []
def take_photo(frame):
    filename = f"photo_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Photo saved: {filename}")
    captured_photos.append(filename)

# Main loop
try:
    camera.start()
    print("Smart Mirror started. Press 'p' to take photo, 'q' to quit.")
    while True:
        frame = camera.capture_frame()
        frame = draw_datetime(frame)
        tracked_frame = tracker.track_faces(frame)
        cv2.imshow('Smart Mirror', tracked_frame)
        # Facial analysis (for each detected face)
        faces = tracker.detect_faces(frame)
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            # Use Google Vision API for analysis
            analysis = analyze_face_with_vision_api(face_img)
            cv2.putText(tracked_frame, analysis, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('p'):
            take_photo(frame)
        if cv2.getWindowProperty('Smart Mirror', cv2.WND_PROP_VISIBLE) < 1:
            break
finally:
    camera.stop()
    cv2.destroyAllWindows()
    print("Smart Mirror stopped.")
