import cv2
from camera import Camera
from facial_tracking import FacialTracker
from datetime import datetime
import mediapipe as mp
import time
import site

# Commented out Raspberry Pi and OpenAI-specific imports for Windows compatibility
# from gpiozero import MotionSensor, Button
# from signal import pause
# import openai
# import numpy as np

# Check OpenCV and MediaPipe versions
print("OpenCV version:", cv2.__version__)
print("MediaPipe version:", mp.__version__)

def analyze_face(face_img):
    # Dummy analysis logic (replace with real ML or API call)
    # You could use OpenCV, a deep learning model, or an API here
    # For now, return a placeholder string
    return "Stress: Low | Acne: Mild | No major changes"

def main():
    # Initialize the camera (try different indices if needed)
    camera = Camera(camera_index=0)  # Try 0, 1, 2, ... if 0 does not work
    try:
        camera.start()
    except Exception as e:
        print(f"Camera failed to open: {e}")
        return

    # Initialize the facial tracker
    tracker = FacialTracker()

    try:
        print("[DEBUG] Starting hand detector...")
        hand_detector = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
        hand_present = False
        hand_start_time = None
        countdown = 5
        print("[INFO] Starting main loop. Press 'q' to quit.")
        while True:
            # Capture frame from the camera
            try:
                frame = camera.capture_frame()
                print("[DEBUG] Frame captured successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to capture frame: {e}")
                break

            # Perform facial tracking
            tracked_frame = tracker.track_faces(frame)

            # Detect faces for analysis
            faces = tracker.detect_faces(frame)
            analysis_results = []
            for (x, y, w, h) in faces:
                face_img = frame[y:y+h, x:x+w]
                analysis = analyze_face(face_img)
                analysis_results.append(analysis)
                cv2.putText(tracked_frame, analysis, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

            # Hand detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hand_detector.process(rgb_frame)
            hand_detected = results.multi_hand_landmarks is not None

            if hand_detected:
                if not hand_present:
                    hand_present = True
                    hand_start_time = time.time()
                elapsed = int(time.time() - hand_start_time)
                if elapsed < countdown:
                    # Show countdown on frame
                    cv2.putText(tracked_frame, f"Photo in {countdown - elapsed}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4, cv2.LINE_AA)
                else:
                    # Take photo with analysis overlays in saved photo
                    photo_path = camera.take_photo(analysis_results=analysis_results, faces=faces)
                    print(f"[INFO] Photo taken and saved to {photo_path}")
                    cv2.putText(tracked_frame, "Photo taken!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 4, cv2.LINE_AA)
                    hand_present = False
                    hand_start_time = None
            else:
                hand_present = False
                hand_start_time = None

            # Overlay date and time on the frame (clock)
            now = datetime.now()
            overlay_text = now.strftime("%Y-%m-%d %H:%M:%S")
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            color = (0, 255, 0)
            thickness = 2
            position = (10, frame.shape[0] - 20)
            cv2.putText(tracked_frame, overlay_text, position, font, font_scale, color, thickness, cv2.LINE_AA)

            # Display the resulting frame
            cv2.imshow('Smart Mirror', tracked_frame)
            key = cv2.waitKey(1)

            # Break the loop on 'q' key press
            if key & 0xFF == ord('q'):
                print("[INFO] Quitting main loop.")
                break
            # Exit camera on window close (Esc key)
            if cv2.getWindowProperty('Smart Mirror', cv2.WND_PROP_VISIBLE) < 1:
                print("[INFO] Window closed. Exiting.")
                break
    finally:
        # Release the camera and close windows
        print("[DEBUG] Stopping camera and closing windows.")
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()