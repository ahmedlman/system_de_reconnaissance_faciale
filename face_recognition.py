import os
import cv2
import numpy as np
import tensorflow as tf
import mysql.connector
from mysql.connector import Error
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
from datetime import datetime, timedelta
from time import time
from config import *


class FaceRecognition:
    def __init__(self, root):
        self.root = root
        self.cap = None
        self.model = None
        self.label_map = {}
        self.reverse_label_map = {}
        self.is_running = False
        self.current_image = None
        self.recognition_start_time = None
        self.last_recognitions = {}   # Track last recognition time for each student
        self.recognition_durations = {}  # Track total duration for each student

        # Initialize UI
        self.setup_ui()

        # Initialize database connection
        self.db_connection = self.init_db_connection()

        # Load face detection model
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Load recognition model
        self.load_model()

    def init_db_connection(self):
        """Initialize database connection with error handling"""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"Database connection failed: {e}")
            return None

    def setup_ui(self):
        """Setup the user interface with enhanced design"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title frame
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=(10, 20), fill="x")

        # Title label
        title_label = ctk.CTkLabel(
            title_frame,
            text="FACE RECOGNITION SYSTEM",
            font=("Arial", 20, "bold"),
            text_color="#4CC9F0"
        )
        title_label.pack()

        # Content frame (two columns)
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Left column - Camera preview
        left_frame = ctk.CTkFrame(content_frame, width=600, height=480)
        left_frame.pack_propagate(False)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        camera_label = ctk.CTkLabel(
            left_frame,
            text="CAMERA FEED",
            font=("Arial", 12, "bold"),
            text_color="#F72585"
        )
        camera_label.pack(pady=(5, 10))

        self.preview_label = ctk.CTkLabel(left_frame, text="", width=600, height=450)
        self.preview_label.pack()

        # Right column - Info and controls
        right_frame = ctk.CTkFrame(content_frame, width=300)
        right_frame.pack_propagate(False)
        right_frame.pack(side="right", fill="both", expand=True)

        # Recognition info frame
        info_frame = ctk.CTkFrame(right_frame, corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 15))

        info_label = ctk.CTkLabel(
            info_frame,
            text="RECOGNITION INFO",
            font=("Arial", 12, "bold"),
            text_color="#F72585"
        )
        info_label.pack(pady=(5, 10))

        # Current status
        self.status_label = ctk.CTkLabel(
            info_frame,
            text="Status: Ready",
            font=("Arial", 11),
            anchor="w",
            justify="left"
        )
        self.status_label.pack(fill="x", padx=10, pady=5)

        # Duration display
        self.duration_label = ctk.CTkLabel(
            info_frame,
            text="Session Duration: 00:00:00",
            font=("Arial", 11),
            anchor="w",
            justify="left"
        )
        self.duration_label.pack(fill="x", padx=10, pady=5)

        # Recognized students frame
        self.students_frame = ctk.CTkScrollableFrame(
            right_frame,
            height=200,
            label_text="RECOGNIZED STUDENTS",
            label_font=("Arial", 12, "bold"),
            label_text_color="#F72585"
        )
        self.students_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Controls frame
        controls_frame = ctk.CTkFrame(right_frame, corner_radius=8)
        controls_frame.pack(fill="x", pady=(0, 10))

        controls_label = ctk.CTkLabel(
            controls_frame,
            text="CONTROLS",
            font=("Arial", 12, "bold"),
            text_color="#F72585"
        )
        controls_label.pack(pady=(5, 10))

        # Start/Stop buttons
        btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="Start Recognition",
            command=self.start_recognition,
            fg_color="#4CC9F0",
            hover_color="#4895EF",
            font=("Arial", 12, "bold")
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=5)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="Stop",
            command=self.stop_recognition,
            state="disabled",
            fg_color="#F72585",
            hover_color="#B5179E",
            font=("Arial", 12, "bold")
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=5)

        # Session statistics
        stats_frame = ctk.CTkFrame(right_frame, corner_radius=8)
        stats_frame.pack(fill="x")

        stats_label = ctk.CTkLabel(
            stats_frame,
            text="SESSION STATISTICS",
            font=("Arial", 12, "bold"),
            text_color="#F72585"
        )
        stats_label.pack(pady=(5, 10))

        self.stats_labels = {
            'total': self.create_stat_label(stats_frame, "Total Recognitions:", "0"),
            'unique': self.create_stat_label(stats_frame, "Unique Students:", "0"),
            'current': self.create_stat_label(stats_frame, "Currently Present:", "0")
        }

    def create_stat_label(self, parent, text, value):
        """Helper to create consistent stat labels"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=2)

        label = ctk.CTkLabel(
            frame,
            text=text,
            font=("Arial", 11),
            anchor="w",
            width=120
        )
        label.pack(side="left")

        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=("Arial", 11, "bold"),
            anchor="e"
        )
        value_label.pack(side="right", fill="x", expand=True)

        return value_label

    def load_model(self):
        """Load the face recognition model"""
        if not os.path.exists(MODEL_PATH) or not os.path.exists(LABEL_MAP_PATH):
            self.status_label.configure(text="Status: Model not found. Please train first.")
            return False

        try:
            self.model = tf.keras.models.load_model(MODEL_PATH)
            self.label_map = np.load(LABEL_MAP_PATH, allow_pickle=True).item()
            self.reverse_label_map = {v: k for k, v in self.label_map.items()}
            return True
        except Exception as e:
            self.status_label.configure(text=f"Status: Error loading model: {str(e)}")
            return False

    def start_recognition(self):
        """Start the face recognition process"""
        if not self.load_model():
            return

        self.cap = cv2.VideoCapture(FACE_CONFIG['camera_index'])
        if not self.cap.isOpened():
            self.status_label.configure(text="Status: Error: Could not open camera")
            return

        self.is_running = True
        self.recognition_start_time = time()
        self.last_recognitions = {}
        self.recognition_durations = {}
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Status: Recognition active...")

        # Clear previous student list
        for widget in self.students_frame.winfo_children():
            widget.destroy()

        # Start duration timer
        self.update_duration()
        self.update_frame()

    def update_duration(self):
        """Update the duration display"""
        if not self.is_running:
            return

        elapsed = time() - self.recognition_start_time
        duration_str = str(timedelta(seconds=int(elapsed)))
        self.duration_label.configure(text=f"Session Duration: {duration_str}")

        # Update statistics
        unique_students = len(self.recognition_durations)
        total_recognitions = sum(len(times) for times in self.last_recognitions.values())
        current_students = sum(1 for student in self.last_recognitions
                               if time() - self.last_recognitions[student][-1] < 5)  # Considered present if recognized in last 5 seconds

        self.stats_labels['total'].configure(text=str(total_recognitions))
        self.stats_labels['unique'].configure(text=str(unique_students))
        self.stats_labels['current'].configure(text=str(current_students))

        self.root.after(1000, self.update_duration)

    def update_frame(self):
        """Process each video frame"""
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            current_time = time()
            current_students = set()

            for (x, y, w, h) in faces:
                try:
                    # Face recognition
                    face_img = frame[y:y + h, x:x + w]
                    face_img = cv2.resize(face_img, (IMG_SIZE, IMG_SIZE))  # Use the imported IMG_SIZE
                    face_img = face_img / 255.0
                    face_img = np.expand_dims(face_img, axis=0)

                    predictions = self.model.predict(face_img)
                    predicted_id = np.argmax(predictions)
                    confidence = np.max(predictions)
                    student_id = self.reverse_label_map.get(predicted_id, "Unknown")

                    # Only consider high-confidence recognitions
                    if confidence > 0.8 and student_id != "Unknown":
                        current_students.add(student_id)

                        # Track recognition time
                        if student_id not in self.last_recognitions:
                            self.last_recognitions[student_id] = []
                            self.recognition_durations[student_id] = 0.0

                        self.last_recognitions[student_id].append(current_time)

                        # Update duration if this is a continuation
                        if len(self.last_recognitions[student_id]) > 1:
                            time_diff = current_time - self.last_recognitions[student_id][-2]
                            if time_diff < 2:  # Considered continuous if less than 2 seconds apart
                                self.recognition_durations[student_id] += time_diff

                        # Log recognition to database if not recently logged
                        if (student_id not in self.last_recognitions or
                                len(self.last_recognitions[student_id]) == 1 or
                                current_time - self.last_recognitions[student_id][-2] > 10):
                            if self.db_connection:
                                self.log_recognition(student_id)

                        # Draw rectangle and label with confidence
                        color = (0, 255, 0)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        label = f"{student_id} ({confidence:.2f})"
                        cv2.putText(frame, label, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                        # Update student list
                        self.update_student_list(student_id)

                except Exception as e:
                    print(f"Error processing face: {e}")

            # Update display
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ctk.CTkImage(light_image=img, size=(600, 450))
            self.preview_label.configure(image=img)
            self.preview_label.image = img

        self.root.after(30, self.update_frame)

    def update_student_list(self, student_id):
        """Update the list of recognized students"""
        # Check if student already in list
        for widget in self.students_frame.winfo_children():
            if hasattr(widget, 'student_id') and widget.student_id == student_id:
                # Update duration display
                duration = self.recognition_durations[student_id]
                duration_str = str(timedelta(seconds=int(duration)))
                widget.duration_label.configure(text=duration_str)
                return

        # Add new student to list
        student_frame = ctk.CTkFrame(self.students_frame, corner_radius=5)
        student_frame.pack(fill="x", pady=2, padx=5)
        student_frame.student_id = student_id

        # Student ID label
        id_label = ctk.CTkLabel(
            student_frame,
            text=student_id,
            font=("Arial", 11, "bold"),
            anchor="w",
            width=150
        )
        id_label.pack(side="left", padx=5)

        # Duration label
        duration_label = ctk.CTkLabel(
            student_frame,
            text="00:00:00",
            font=("Arial", 11),
            anchor="e"
        )
        duration_label.pack(side="right", padx=5)
        student_frame.duration_label = duration_label

    def log_recognition(self, student_id):
        """Log recognition to database"""
        try:
            cursor = self.db_connection.cursor()
            query = "INSERT INTO recognition_logs (student_id, recognition_time) VALUES (%s, %s)"
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(query, (student_id, current_time))
            self.db_connection.commit()
            cursor.close()
        except Error as e:
            print(f"Database error: {e}")

    def stop_recognition(self):
        """Stop the recognition process"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Ready")

        # Final duration update
        if self.recognition_start_time:
            elapsed = time() - self.recognition_start_time
            duration_str = str(timedelta(seconds=int(elapsed)))
            self.duration_label.configure(text=f"Session Duration: {duration_str} (Final)")

    def on_closing(self):
        """Cleanup when closing the application"""
        self.stop_recognition()
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
        self.root.destroy()