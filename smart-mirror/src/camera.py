import cv2
import os


class Camera:
    def __init__(self, camera_index=0):
        self.capture = None
        self.camera_index = camera_index
        # self.start()  # Remove auto-start, let main.py control when to open the camera

    def start(self):
        print(f"[DEBUG] OpenCV version: {cv2.__version__}")
        print(f"[DEBUG] Trying camera index {self.camera_index} with default backend")
        cap = cv2.VideoCapture(self.camera_index)
        if cap.isOpened():
            self.capture = cap
            print(f"[DEBUG] Camera opened successfully at index {self.camera_index} with default backend")
            return
        print(f"[DEBUG] Failed to open camera at index {self.camera_index} with default backend")
        cap.release()
        raise Exception(f"Could not open video device at index {self.camera_index}. Check if the camera is in use or try reconnecting it.")

    def stop(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def capture_frame(self):
        if self.capture is None:
            raise Exception("Camera is not started")
        ret, frame = self.capture.read()
        if not ret:
            raise Exception("Could not read frame")
        return frame

    def take_photo(self, save_dir=".", analysis_results=None, faces=None):
        """
        Captures a frame, overlays the current date and time, and saves it as an image file.
        Also overlays analysis results if provided.
        Returns the path to the saved image.
        """
        from datetime import datetime
        if self.capture is None:
            self.start()
        ret, frame = self.capture.read()
        if not ret:
            raise Exception("Could not read frame")
        # Overlay analysis results if provided and not empty
        if analysis_results is not None and faces is not None and len(faces) > 0 and len(analysis_results) > 0:
            for ((x, y, w, h), analysis) in zip(faces, analysis_results):
                cv2.putText(frame, analysis, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        # Get current date and time
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        overlay_text = now.strftime("%Y-%m-%d %H:%M:%S")
        # Overlay date and time on the image
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (0, 255, 0)
        thickness = 2
        position = (10, frame.shape[0] - 20)
        cv2.putText(frame, overlay_text, position, font, font_scale, color, thickness, cv2.LINE_AA)
        # Save the image
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(save_dir, filename)
        cv2.imwrite(filepath, frame)
        return filepath

# No code at the bottom of this file. Camera is only opened by your main application (e.g., main.py)
# To open the camera, ensure your main.py contains:
# camera = Camera(camera_index=0)
# camera.start()