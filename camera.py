# camera.py
import cv2
from PIL import Image
import customtkinter as ctk
from customtkinter import CTkImage
class Camera:
    def __init__(self, camera_index=0, resolution=(400, 400), fps=30):
        self.cap = None
        self.camera_index = camera_index
        self.resolution = resolution
        self.fps = fps
        self.is_opened = False

    def start(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.is_opened = self.cap.isOpened()
            return self.is_opened
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def get_frame(self):
        if self.is_opened and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, self.resolution)
                return frame
        return None

    def stop(self):
        self.is_opened = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def __del__(self):
        self.stop()