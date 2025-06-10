import cv2

def resize_image(image, width, height):
    return cv2.resize(image, (width, height))

def draw_rectangle(image, coordinates, color=(255, 0, 0), thickness=2):
    x, y, w, h = coordinates
    return cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)