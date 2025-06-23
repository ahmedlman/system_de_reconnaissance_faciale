import threading
import time
import face_recognition
import customtkinter as ctk
import tkinter
import cv2
import os
import re
import queue
import logging
import joblib
import numpy as np
import pickle
from PIL import Image
from tkinter import messagebox
from database import TeacherDB, StudentDB
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from config import DATASET_PATH, TOTAL_IMAGES, IMG_SIZE, UI_CONFIG,Theme


logging.basicConfig(filename='capture_faces.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Camera:
    def __init__(self, camera_index=0, resolution=(400, 400), fps=60):
        self.camera_index = camera_index
        self.resolution = resolution
        self.fps = fps
        self.cap = None
        self._is_opened = False
        self.frame_queue = queue.Queue(maxsize=5)
        self.is_running = False
        self.capture_thread = None
        self.current_frame = None
        self.lock = threading.Lock()

    @property
    def is_opened(self):
        return self._is_opened

    def start(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                logging.error(f"Failed to open camera at index {self.camera_index}")
                return False

            with self.lock:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                self._is_opened = True
                self.is_running = True

            self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
            self.capture_thread.start()
            logging.info(f"Camera started with resolution {self.resolution} and FPS {self.fps}")
            return True
        except Exception as e:
            logging.error(f"Camera start error: {e}")
            return False

    def _capture_frames(self):
        frame_interval = 1.0 / self.fps
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                start_time = time.time()
                with self.lock:
                    ret, frame = self.cap.read()
                if not ret:
                    logging.warning("Failed to capture frame")
                    break
                frame = cv2.resize(frame, self.resolution)
                self.current_frame = frame.copy()
                if not self.frame_queue.full():
                    self.frame_queue.put(frame.copy())
                elapsed = time.time() - start_time
                time.sleep(max(0, frame_interval - elapsed))
            except Exception as e:
                logging.error(f"Error capturing frame: {e}")
                break

    def get_frame(self):
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None

    def stop(self):
        self.is_running = False
        if self.cap and self._is_opened:
            with self.lock:
                self.cap.release()
                self._is_opened = False
                self.cap = None
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        self.capture_thread = None
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        logging.info("Camera stopped")

    def __del__(self):
        self.stop()

class CaptureFaces(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.parent = parent
        self.is_capturing = False
        self.camera = None
        self.face_detection_thread = None
        self.face_queue = queue.Queue(maxsize=5)
        self.images_captured = 0
        self.current_student = None
        self.current_teacher = None
        self.db_connection = db_connection
        self.teacher_db = TeacherDB(self.db_connection)
        self.student_db = StudentDB(self.db_connection)
        self.all_students = []
        self.all_teachers = []
        self.person_type = ctk.StringVar(value="student")
        self.dataset_dir = os.path.join(DATASET_PATH, "dataset")
        self.progress_window = None
        self.training_thread = None
        self.current_image = None

        # Access theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()
        self.create_ui()
        self.load_students()
        self.load_teachers()

    def create_ui(self):
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            title_frame,
            text="Capture Faces",
            font=self.theme["font_large"],
            text_color=self.theme["primary"]
        ).pack(pady=5)

        content_frame = ctk.CTkFrame(self, fg_color=self.theme["background"])
        content_frame.pack(fill="both", expand=True, padx=2, pady=2)

        left_panel = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"])
        left_panel.pack(side="left", fill="both", padx=2, pady=2, expand=True)

        student_section = ctk.CTkFrame(left_panel, fg_color=self.theme["frame"])
        student_section.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(
            student_section,
            text="Student Selection",
            font=self.theme["font_title"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", pady=(0, 5))

        self.student_search_var = ctk.StringVar()
        self.student_search_var.trace("w", lambda *args: self.filter_students())
        student_search_frame = ctk.CTkFrame(student_section, fg_color="transparent")
        student_search_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(
            student_search_frame,
            text="Search:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).pack(side="left", padx=5)
        self.student_search_entry = ctk.CTkEntry(
            student_search_frame,
            textvariable=self.student_search_var,
            width=150,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        )
        self.student_search_entry.pack(side="left", fill="x", expand=True, padx=2)

        student_list_frame = ctk.CTkFrame(student_section, fg_color="transparent")
        student_list_frame.pack(fill="both", expand=True, pady=2)

        self.student_listbox = tkinter.Listbox(student_list_frame, height=10, selectmode="single")
        self.student_listbox.pack(side="left", fill="both", expand=True)
        self.student_listbox.bind("<<ListboxSelect>>", lambda e: self.on_student_select())
        self.student_listbox.bind("<Double-Button-1>", lambda e: self.on_student_double_click())

        student_details_frame = ctk.CTkFrame(student_section, fg_color="transparent")
        student_details_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(
            student_details_frame,
            text="Student ID:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.id_entry = ctk.CTkEntry(
            student_details_frame,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        )
        self.id_entry.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        ctk.CTkLabel(
            student_details_frame,
            text="Student Name:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ctk.CTkEntry(
            student_details_frame,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        )
        self.name_entry.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        student_details_frame.columnconfigure(1, weight=1)

        teacher_section = ctk.CTkFrame(left_panel, fg_color=self.theme["frame"])
        teacher_section.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(
            teacher_section,
            text="Teacher Selection",
            font=self.theme["font_title"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", pady=(0, 5))

        self.teacher_search_var = ctk.StringVar()
        self.teacher_search_var.trace("w", lambda *args: self.filter_teachers())
        teacher_search_frame = ctk.CTkFrame(teacher_section, fg_color="transparent")
        teacher_search_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(
            teacher_search_frame,
            text="Search:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).pack(side="left", padx=5)
        self.teacher_search_entry = ctk.CTkEntry(
            teacher_search_frame,
            textvariable=self.teacher_search_var,
            width=100,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        )
        self.teacher_search_entry.pack(side="left", fill="x", expand=True, padx=2)

        teacher_list_frame = ctk.CTkFrame(teacher_section, fg_color="transparent")
        teacher_list_frame.pack(fill="both", expand=True, pady=2)

        self.teacher_listbox = tkinter.Listbox(teacher_list_frame, height=10, selectmode="single")
        self.teacher_listbox.pack(side="left", fill="both", expand=True)
        self.teacher_listbox.bind("<<ListboxSelect>>", lambda e: self.on_teacher_select())
        self.teacher_listbox.bind("<Double-Button-1>", lambda e: self.on_teacher_double_click())

        teacher_details_frame = ctk.CTkFrame(teacher_section, fg_color="transparent")
        teacher_details_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(
            teacher_details_frame,
            text="Teacher ID:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.teacher_entry = ctk.CTkEntry(
            teacher_details_frame,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        )
        self.teacher_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(
            teacher_details_frame,
            text="Teacher Name:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.teacher_name_entry = ctk.CTkEntry(
            teacher_details_frame,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        )
        self.teacher_name_entry.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        teacher_details_frame.columnconfigure(1, weight=1)

        right_panel = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"])
        right_panel.pack(side="right", fill="both", padx=2, pady=2, expand=True)

        preview_section = ctk.CTkFrame(right_panel, fg_color=self.theme["frame"])
        preview_section.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(
            preview_section,
            text="Camera Preview",
            font=self.theme["font_title"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", pady=(0, 5))

        preview_container = ctk.CTkFrame(
            preview_section,
            fg_color=self.theme["background"],
            corner_radius=8
        )
        preview_container.pack(fill="both", expand=True, pady=2)

        preview_size = UI_CONFIG['preview_size']
        self.preview_frame = ctk.CTkFrame(
            preview_container,
            width=preview_size[0],
            height=preview_size[1],
            fg_color=self.theme["background"]
        )
        self.preview_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Camera feed will appear here",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        progress_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        progress_frame.pack(fill="x", padx=2, pady=2)

        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=200,
            fg_color=self.theme["secondary"],
            progress_color=self.theme["primary"]
        )
        self.progress_bar.pack(pady=5, fill="x")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to capture",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        )
        self.progress_label.pack()

        button_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        button_frame.pack(pady=10, fill="x")

        self.capture_btn = ctk.CTkButton(
            button_frame,
            text="Start Capture",
            command=self.start_capture,
            fg_color=self.theme["primary"],
            hover_color=self.theme["button_hover"],
            height=40,
            font=self.theme["font_title"],
            corner_radius=8
        )
        self.capture_btn.pack(side="left", padx=5, fill="x", expand=True)

        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel_capture,
            fg_color=["#95a5a6", "#7f8c8d"],
            hover_color=["#7f8c8d", "#6c757d"],
            height=40,
            font=self.theme["font_title"],
            corner_radius=8,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=5, fill="x", expand=True)

        self.train_btn = ctk.CTkButton(
            button_frame,
            text="Train Model",
            command=self.train_model,
            fg_color=self.theme["success"],
            hover_color=["#27ae60", "#219653"],
            height=40,
            font=self.theme["font_title"],
            corner_radius=8
        )
        self.train_btn.pack(side="left", padx=5, fill="x", expand=True)

    def create_progress_window(self):
        if self.progress_window is not None:
            self.progress_window.destroy()
        self.progress_window = ctk.CTkToplevel(self)
        self.progress_window.title("Training Progress")
        self.progress_window.geometry("300x150")
        self.progress_window.transient(self)
        self.progress_window.grab_set()
        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)

        ctk.CTkLabel(
            self.progress_window,
            text="Training Model...",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(pady=10)

        self.training_progress_bar = ctk.CTkProgressBar(
            self.progress_window,
            width=250,
            fg_color=self.theme["secondary"],
            progress_color=self.theme["primary"]
        )
        self.training_progress_bar.pack(pady=10)
        self.training_progress_bar.set(0)

        self.training_status_label = ctk.CTkLabel(
            self.progress_window,
            text="Initializing...",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        )
        self.training_status_label.pack(pady=5)

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', '_', name.replace(' ', '_'))

    def on_student_double_click(self, event=None):
        try:
            selected = self.student_listbox.get(self.student_listbox.curselection())
            if selected:
                student_id, student_name = selected.split(" - ", 1)
                self.id_entry.delete(0, "end")
                self.id_entry.insert(0, student_id)
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, student_name)
                self.teacher_entry.delete(0, "end")
                self.teacher_name_entry.delete(0, "end")
                self.person_type.set("student")
                if messagebox.askyesno("Start Capture", f"Do you want to capture images for {student_name}?"):
                    self.start_capture()
        except Exception as e:
            logging.error(f"Student double-click error: {e}")
            messagebox.showerror("Error", f"Failed to select student: {str(e)}")

    def on_teacher_double_click(self, event=None):
        try:
            selected = self.teacher_listbox.get(self.teacher_listbox.curselection())
            if selected:
                teacher_id, teacher_name = selected.split(" - ", 1)
                self.teacher_entry.delete(0, "end")
                self.teacher_entry.insert(0, teacher_id)
                self.teacher_name_entry.delete(0, "end")
                self.teacher_name_entry.insert(0, teacher_name)
                self.id_entry.delete(0, "end")
                self.name_entry.delete(0, "end")
                self.person_type.set("teacher")
                if messagebox.askyesno("Start Capture", f"Do you want to capture images for {teacher_name}?"):
                    self.start_capture()
        except Exception as e:
            logging.error(f"Teacher double-click error: {e}")
            messagebox.showerror("Error", f"Failed to select teacher: {str(e)}")

    def load_students(self):
        try:
            students = self.student_db.get_all_students()
            self.all_students = students
            self._populate_listbox(self.student_listbox, students)
        except Exception as e:
            logging.error(f"Error loading students: {e}")
            messagebox.showerror("Database Error", f"Failed to load students: {str(e)}")

    def load_teachers(self):
        try:
            teachers = self.teacher_db.get_all_teachers()
            self.all_teachers = teachers
            self._populate_listbox(self.teacher_listbox, teachers)
        except Exception as e:
            logging.error(f"Error loading teachers: {e}")
            messagebox.showerror("Database Error", f"Failed to load teachers: {str(e)}")

    def _populate_listbox(self, listbox, items):
        try:
            listbox.delete(0, "end")
            for item in items:
                if isinstance(item, dict) and 'student_id' in item and 'full_name' in item:
                    listbox.insert("end", f"{item['student_id']} - {item['full_name']}")
                elif isinstance(item, dict) and 'user_id' in item and 'name' in item:
                    listbox.insert("end", f"{item['user_id']} - {item['name']}")
        except Exception as e:
            logging.error(f"Error populating listbox: {e}")

    def filter_students(self):
        search_text = self.student_search_var.get().lower()
        filtered = [s for s in self.all_students if search_text in str(s['student_id']).lower() or search_text in s['full_name'].lower()]
        self._populate_listbox(self.student_listbox, filtered)

    def filter_teachers(self):
        search_text = self.teacher_search_var.get().lower()
        filtered = [t for t in self.all_teachers if search_text in str(t['user_id']).lower() or search_text in t['name'].lower()]
        self._populate_listbox(self.teacher_listbox, filtered)

    def on_student_select(self):
        try:
            selected = self.student_listbox.get(self.student_listbox.curselection())
            if selected:
                student_id, student_name = selected.split(" - ", 1)
                self.id_entry.delete(0, "end")
                self.id_entry.insert(0, student_id)
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, student_name)
                self.person_type.set("student")
        except Exception as e:
            logging.error(f"Student selection error: {e}")

    def on_teacher_select(self):
        try:
            selected = self.teacher_listbox.get(self.teacher_listbox.curselection())
            if selected:
                teacher_id, teacher_name = selected.split(" - ", 1)
                self.teacher_entry.delete(0, "end")
                self.teacher_entry.insert(0, teacher_id)
                self.teacher_name_entry.delete(0, "end")
                self.teacher_name_entry.insert(0, teacher_name)
                self.person_type.set("teacher")
        except Exception as e:
            logging.error(f"Teacher selection error: {e}")

    def validate_inputs(self):
        student_id = self.id_entry.get().strip()
        student_name = self.name_entry.get().strip()
        teacher_id = self.teacher_entry.get().strip()
        teacher_name = self.teacher_name_entry.get().strip()

        if not ((student_id and student_name) or (teacher_id and teacher_name)):
            messagebox.showwarning("Input Error", "Please select a student or teacher")
            return False

        try:
            if student_id and student_name:
                self.person_type.set("student")
                self.current_student = {"student_id": int(student_id), "full_name": student_name}
                self.current_teacher = None
            elif teacher_id and teacher_name:
                self.person_type.set("teacher")
                self.current_teacher = {"user_id": int(teacher_id), "name": teacher_name}
                self.current_student = None
        except ValueError:
            messagebox.showwarning("Input Error", "ID must be a valid integer")
            return False

        return True

    def start_capture(self):
        if not self.validate_inputs():
            return

        if self.person_type.get() == "student":
            person_id = str(self.current_student["student_id"])
            person_name = self.current_student["full_name"]
            person_type_folder = "students"
        else:
            person_id = str(self.current_teacher["user_id"])
            person_name = self.current_teacher["name"]
            person_type_folder = "teachers"

        sanitized_name = self.sanitize_filename(person_name)
        try:
            person_dir = os.path.join(DATASET_PATH, person_type_folder)
            os.makedirs(person_dir, exist_ok=True)
            self.dataset_dir = os.path.join(person_dir, f"{person_id}_{sanitized_name}")
            os.makedirs(self.dataset_dir, exist_ok=True)
        except OSError as e:
            logging.error(f"Error creating dataset directory: {e}")
            messagebox.showerror("File Error", f"Failed to create dataset directory: {str(e)}")
            return

        try:
            self.camera = Camera(camera_index=0, resolution=(400, 400), fps=30)
            if not self.camera.start():
                raise RuntimeError("Failed to initialize camera")
        except Exception as e:
            logging.error(f"Camera initialization error: {e}")
            messagebox.showerror("Camera Error", f"Failed to initialize camera: {str(e)}")
            self.camera = None
            return

        self.capture_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.train_btn.configure(state="disabled")
        self.progress_label.configure(text="Starting capture...")
        self.progress_bar.set(0)

        self.images_captured = 0
        self.is_capturing = True

        self.face_detection_thread = threading.Thread(target=self.detect_faces, daemon=True)
        self.face_detection_thread.start()
        self.update_camera_feed()

    def detect_faces(self):
        scale_factor = 0.5
        while self.is_capturing and self.camera and self.camera.is_opened:
            try:
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.05)
                    continue

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                small_frame = cv2.resize(rgb_frame, (0, 0), fx=scale_factor, fy=scale_factor)
                face_locations = face_recognition.face_locations(small_frame, model="hog")
                face_locations = [
                    (int(top / scale_factor), int(right / scale_factor), int(bottom / scale_factor), int(left / scale_factor))
                    for top, right, bottom, left in face_locations
                ]

                if not self.face_queue.full():
                    self.face_queue.put((rgb_frame, face_locations))
            except Exception as e:
                logging.error(f"Face detection error: {e}")
                if not self.face_queue.full():
                    self.face_queue.put((None, []))
            time.sleep(0.05)

    def update_camera_feed(self):
        if not self.is_capturing or not self.camera or not self.camera.is_opened:
            self.reset_capture_state()
            return

        try:
            rgb_frame, face_locations = None, []
            while not self.face_queue.empty():
                rgb_frame, face_locations = self.face_queue.get_nowait()
        except queue.Empty:
            self.after(33, self.update_camera_feed)  # ~30 FPS
            return

        if rgb_frame is None:
            self.after(33, self.update_camera_feed)
            return

        for top, right, bottom, left in face_locations:
            face_width = right - left
            face_height = bottom - top
            if face_width < 50 or face_height < 50:
                continue
            cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)

            if self.images_captured < TOTAL_IMAGES:
                face_img = rgb_frame[top:bottom, left:right]
                if face_img.size == 0:
                    continue
                face_img = cv2.resize(face_img, (IMG_SIZE, IMG_SIZE))
                img_path = os.path.join(self.dataset_dir, f"{self.images_captured}.jpg")
                face_img_bgr = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
                try:
                    cv2.imwrite(img_path, face_img_bgr)
                    self.images_captured += 1
                    progress = self.images_captured / TOTAL_IMAGES
                    self.progress_bar.set(progress)
                    self.progress_label.configure(text=f"Captured {self.images_captured}/{TOTAL_IMAGES} images")

                    if self.images_captured >= TOTAL_IMAGES:
                        self.is_capturing = False
                        self.reset_capture_state()
                        self.progress_label.configure(text="Capture complete")
                        self.update_database_with_photo()
                        messagebox.showinfo("Success", f"Successfully captured {TOTAL_IMAGES} images and updated database")
                        return
                except Exception as e:
                    logging.error(f"Error saving image: {e}")

        preview_size = UI_CONFIG['preview_size']
        img = Image.fromarray(rgb_frame)
        img = img.resize(preview_size, Image.Resampling.LANCZOS)
        img_tk = ctk.CTkImage(light_image=img, size=preview_size)
        self.preview_label.configure(image=img_tk)
        self.current_image = img_tk

        if self.is_capturing:
            self.after(33, self.update_camera_feed)

    def cancel_capture(self):
        self.is_capturing = False
        self.reset_capture_state()
        self.progress_label.configure(text="Capture cancelled")
        self.progress_bar.set(0)

    def reset_capture_state(self):
        self.is_capturing = False
        if self.camera:
            self.camera.stop()
            self.camera = None
        self.capture_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.train_btn.configure(state="normal")
        self.preview_label.configure(image=None)
        self.current_image = None
        self.preview_label.configure(text="Camera feed will appear here")

        while not self.face_queue.empty():
            try:
                self.face_queue.get_nowait()
            except queue.Empty:
                break

        if self.face_detection_thread and self.face_detection_thread.is_alive():
            self.face_detection_thread.join(timeout=1.0)
        self.face_detection_thread = None

    def update_database_with_photo(self):
        try:
            if self.person_type.get() == "student":
                student_id = self.current_student["student_id"]
                self.student_db.update_student(student_id, photo=self.dataset_dir)
            else:
                teacher_id = self.current_teacher["user_id"]
                self.teacher_db.update_teacher(teacher_id, photo=self.dataset_dir)
        except Exception as e:
            logging.error(f"Error updating database with photo: {e}")
            messagebox.showerror("Database Error", f"Failed to update database: {str(e)}")

    def update_training_progress(self, progress, status):
        if self.progress_window is not None:
            self.training_progress_bar.set(progress)
            self.training_status_label.configure(text=status)
            self.progress_window.update()

    def close_progress_window(self):
        if self.progress_window is not None:
            self.progress_window.destroy()
            self.progress_window = None

    def train_model(self):
        try:
            self.create_progress_window()
            self.update_training_progress(0.0, "Initializing...")
            self.training_thread = threading.Thread(target=self._train_model_thread, daemon=True)
            self.training_thread.start()
        except Exception as e:
            logging.error(f"Training initialization error: {e}")
            self.close_progress_window()
            messagebox.showerror("Training Error", f"Failed to start training: {str(e)}")

    def _train_model_thread(self):
        try:
            encodings = []
            labels = []
            label_map = {}
            reverse_label_map = {}
            label_id = 0
            total_images = 0

            students_path = os.path.join(DATASET_PATH, "students")
            if os.path.exists(students_path):
                for student_folder in os.listdir(students_path):
                    folder_path = os.path.join(students_path, student_folder)
                    if os.path.isdir(folder_path):
                        total_images += len([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

            teachers_path = os.path.join(DATASET_PATH, "teachers")
            if os.path.exists(teachers_path):
                for teacher_folder in os.listdir(teachers_path):
                    folder_path = os.path.join(teachers_path, teacher_folder)
                    if os.path.isdir(folder_path):
                        total_images += len([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

            if total_images == 0:
                self.after(0, lambda: self.close_progress_window())
                self.after(0, lambda: messagebox.showwarning("Training Error", "No images found for training."))
                return

            processed_images = 0
            self.update_training_progress(0.1, "Processing student images...")
            if os.path.exists(students_path):
                for student_folder in os.listdir(students_path):
                    folder_path = os.path.join(students_path, student_folder)
                    if os.path.isdir(folder_path):
                        try:
                            student_id, student_name = student_folder.split('_', 1)
                        except ValueError:
                            student_id = student_folder
                            student_name = "Unknown"

                        label_map[student_folder] = label_id
                        reverse_label_map[label_id] = {"student_id": student_id, "name": student_name, "type": "student"}

                        for img_name in os.listdir(folder_path):
                            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                                img_path = os.path.join(folder_path, img_name)
                                img = face_recognition.load_image_file(img_path)
                                face_encodings = face_recognition.face_encodings(img, model="hog")
                                if face_encodings:
                                    encodings.append(face_encodings[0])
                                    labels.append(label_id)
                                else:
                                    logging.warning(f"No faces detected in {img_path}")
                                processed_images += 1
                                progress = 0.1 + (processed_images / total_images) * 0.4
                                self.update_training_progress(progress, f"Processing image {processed_images}/{total_images}")
                        label_id += 1

            self.update_training_progress(0.5, "Processing teacher images...")
            if os.path.exists(teachers_path):
                for teacher_folder in os.listdir(teachers_path):
                    folder_path = os.path.join(teachers_path, teacher_folder)
                    if os.path.isdir(folder_path):
                        try:
                            teacher_id, teacher_name = teacher_folder.split('_', 1)
                        except ValueError:
                            teacher_id = teacher_folder
                            teacher_name = "Unknown"

                        label_map[teacher_folder] = label_id
                        reverse_label_map[label_id] = {"user_id": teacher_id, "name": teacher_name, "type": "teacher"}

                        for img_name in os.listdir(folder_path):
                            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                                img_path = os.path.join(folder_path, img_name)
                                img = face_recognition.load_image_file(img_path)
                                face_encodings = face_recognition.face_encodings(img, model="hog")
                                if face_encodings:
                                    encodings.append(face_encodings[0])
                                    labels.append(label_id)
                                else:
                                    logging.warning(f"No faces detected in {img_path}")
                                processed_images += 1
                                progress = 0.1 + (processed_images / total_images) * 0.4
                                self.update_training_progress(progress, f"Processing image {processed_images}/{total_images}")
                        label_id += 1

            if not encodings:
                self.after(0, lambda: self.close_progress_window())
                self.after(0, lambda: messagebox.showwarning("Training Error", "No valid face data found for training."))
                return

            if len(set(labels)) < 2:
                self.after(0, lambda: self.close_progress_window())
                self.after(0, lambda: messagebox.showwarning("Training Error", "Need at least 2 different people with faces detected."))
                return

            self.update_training_progress(0.6, "Preparing data for training...")
            X = np.array(encodings)
            y = np.array(labels)

            self.update_training_progress(0.7, "Splitting data...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.update_training_progress(0.8, "Training SVM model...")
            svm = SVC(kernel='linear', probability=True)
            svm.fit(X_train, y_train)

            self.update_training_progress(0.9, "Evaluating model...")
            y_pred = svm.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            self.update_training_progress(0.95, "Saving model...")
            os.makedirs("models", exist_ok=True)
            model_path = os.path.join("models", "face_recognition_svm.pkl")
            label_map_path = os.path.join("models", "label_map.pickle")

            try:
                joblib.dump(svm, model_path)
                with open(label_map_path, "wb") as f:
                    pickle.dump(reverse_label_map, f)
            except Exception as e:
                logging.error(f"Error saving model or label map: {e}")
                self.after(0, lambda: self.close_progress_window())
                self.after(0, lambda: messagebox.showerror("Training Error", f"Failed to save model: {str(e)}"))
                return

            self.update_training_progress(1.0, "Training complete!")
            time.sleep(0.5)
            self.after(0, lambda: self.close_progress_window())
            self.after(0, lambda: messagebox.showinfo("Training Complete", f"Model trained successfully!\nTest Accuracy: {accuracy:.2f}\nSamples: {len(encodings)}"))
        except Exception as e:
            logging.error(f"Training error: {e}")
            self.after(0, lambda: self.close_progress_window())
            self.after(0, lambda: messagebox.showerror("Training Error", f"Failed to train model: {str(e)}"))

    def __del__(self):
        try:
            self.is_capturing = False
            self.reset_capture_state()
            self.close_progress_window()
        except Exception as e:
            logging.error(f"Error in destructor: {e}")