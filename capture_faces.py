# capture_faces.py
import threading
import time
import face_recognition
import customtkinter as ctk
import cv2
import os

import joblib
import numpy as np
import pickle

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from PIL import Image, ImageTk
from tkinter import messagebox
from config import *
from database import *

# Define constants if not in globals
if 'DATASET_PATH' not in globals():
    DATASET_PATH = "dataset"
if 'IMG_SIZE' not in globals():
    IMG_SIZE = 160
if 'TOTAL_IMAGES' not in globals():
    TOTAL_IMAGES = 20

class CaptureFaces(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="#f5f7fa")
        self.parent = parent
        self.is_capturing = False
        self.capture_thread = None
        self.images_captured = 0
        self.cap = None
        self.current_student = None
        self.current_teacher = None
        self.db_connection = db_connection
        self.info_fetcher = Get_info_to_capture(self.db_connection)
        self.teacher_db = TeacherDB(self.db_connection)
        self.student_db = StudentDB(self.db_connection)
        self.all_students = []
        self.all_teachers = []
        self.person_type = ctk.StringVar(value="student")
        self.dataset_dir = None

        # Setup UI
        self.create_ui()

    def create_ui(self):
        """Create the user interface"""
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=1, pady=1)

        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            title_frame,
            text="Face Capture",
            font=("Arial", 16, "bold"),
            text_color="#1E3A8A"
        ).pack(pady=5)

        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=2, pady=2)

        left_panel = ctk.CTkFrame(content_frame, width=100)
        left_panel.pack(side="left", fill="both", padx=2, pady=2, expand=True)

        student_section = ctk.CTkFrame(left_panel)
        student_section.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(student_section, text="Student Selection", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 5))

        self.student_search_var = ctk.StringVar()
        self.student_search_var.trace("w", lambda *args: self.filter_students())
        student_search_frame = ctk.CTkFrame(student_section)
        student_search_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(student_search_frame, text="Search:").pack(side="left", padx=5)
        self.student_search_entry = ctk.CTkEntry(student_search_frame, textvariable=self.student_search_var, width=150)
        self.student_search_entry.pack(side="left", fill="x", expand=True, padx=2)

        student_list_frame = ctk.CTkFrame(student_section)
        student_list_frame.pack(fill="both", expand=True, pady=2)

        try:
            self.student_listbox = ctk.CTkListbox(student_list_frame, height=100)
            self.student_listbox.pack(side="left", fill="both", expand=True)
            self.student_listbox.bind("<<ListboxSelect>>", lambda e: self.on_student_select())
            self.student_listbox.bind("<Double-Button-1>", lambda e: self.on_student_double_click())
        except AttributeError:
            import tkinter as tk
            self.student_listbox = tk.Listbox(student_list_frame, height=10, exportselection=0)
            self.student_listbox.pack(side="left", fill="both", expand=True)
            self.student_listbox.bind('<<ListboxSelect>>', lambda e: self.on_student_select())
            self.student_listbox.bind('<Double-Button-1>', lambda e: self.on_student_double_click())

        student_details_frame = ctk.CTkFrame(student_section)
        student_details_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(student_details_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.id_entry = ctk.CTkEntry(student_details_frame)
        self.id_entry.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        ctk.CTkLabel(student_details_frame, text="Student Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ctk.CTkEntry(student_details_frame)
        self.name_entry.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        student_details_frame.columnconfigure(1, weight=1)

        teacher_section = ctk.CTkFrame(left_panel)
        teacher_section.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(teacher_section, text="Teacher Selection", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 5))

        self.teacher_search_var = ctk.StringVar()
        self.teacher_search_var.trace("w", lambda *args: self.filter_teachers())
        teacher_search_frame = ctk.CTkFrame(teacher_section)
        teacher_search_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(teacher_search_frame, text="Search:").pack(side="left", padx=5)
        self.teacher_search_entry = ctk.CTkEntry(teacher_search_frame, textvariable=self.teacher_search_var, width=100)
        self.teacher_search_entry.pack(side="left", fill="x", expand=True, padx=2)

        teacher_list_frame = ctk.CTkFrame(teacher_section)
        teacher_list_frame.pack(fill="both", expand=True, pady=2)

        try:
            self.teacher_listbox = ctk.CTkListbox(teacher_list_frame, height=120)
            self.teacher_listbox.pack(side="left", fill="both", expand=True)
            self.teacher_listbox.bind("<<ListboxSelect>>", lambda e: self.on_teacher_select())
            self.teacher_listbox.bind("<Double-Button-1>", lambda e: self.on_teacher_double_click())
        except AttributeError:
            import tkinter as tk
            self.teacher_listbox = tk.Listbox(teacher_list_frame, height=10, exportselection=0)
            self.teacher_listbox.pack(side="left", fill="both", expand=True)
            self.teacher_listbox.bind('<<ListboxSelect>>', lambda e: self.on_teacher_select())
            self.teacher_listbox.bind('<Double-Button-1>', lambda e: self.on_teacher_double_click())

        teacher_details_frame = ctk.CTkFrame(teacher_section)
        teacher_details_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(teacher_details_frame, text="Teacher ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.teacher_entry = ctk.CTkEntry(teacher_details_frame)
        self.teacher_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(teacher_details_frame, text="Teacher Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.teacher_name_entry = ctk.CTkEntry(teacher_details_frame)
        self.teacher_name_entry.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        teacher_details_frame.columnconfigure(1, weight=1)

        camera_frame = ctk.CTkFrame(left_panel)
        camera_frame.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(camera_frame, text="Camera Settings", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 5))

        camera_select_frame = ctk.CTkFrame(camera_frame)
        camera_select_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(camera_select_frame, text="Select Camera:").pack(side="left", padx=5)
        camera_index = 0
        if 'FACE_CONFIG' in globals() and 'camera_index' in FACE_CONFIG:
            camera_index = FACE_CONFIG['camera_index']
        self.camera_index_var = ctk.StringVar(value=str(camera_index))
        self.camera_dropdown = ctk.CTkComboBox(
            camera_select_frame,
            variable=self.camera_index_var,
            values=[str(i) for i in range(5)],
            width=100
        )
        self.camera_dropdown.pack(side="left", padx=2)

        right_panel = ctk.CTkFrame(content_frame, width=300)
        right_panel.pack(side="right", fill="both", padx=2, pady=2, expand=True)

        preview_section = ctk.CTkFrame(right_panel)
        preview_section.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(preview_section, text="Camera Preview", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 5))

        preview_container = ctk.CTkFrame(preview_section, fg_color="#D1D5DB", corner_radius=8)
        preview_container.pack(fill="both", expand=True, pady=2)

        preview_size = (320, 240)
        if 'UI_CONFIG' in globals() and 'preview_size' in UI_CONFIG:
            preview_size = UI_CONFIG['preview_size']

        self.preview_frame = ctk.CTkFrame(
            preview_container,
            width=preview_size[0],
            height=preview_size[1],
            fg_color="#F3F4F6"
        )
        self.preview_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Camera feed will appear here",
            font=("Arial", 14)
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        progress_frame = ctk.CTkFrame(right_panel)
        progress_frame.pack(fill="x", padx=2, pady=2)

        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=200)
        self.progress_bar.pack(pady=5, fill="x")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to capture",
            font=("Arial", 12),
            text_color="#4B5563"
        )
        self.progress_label.pack()

        button_frame = ctk.CTkFrame(right_panel)
        button_frame.pack(pady=10, fill="x")

        self.capture_btn = ctk.CTkButton(
            button_frame,
            text="Start Capture",
            command=self.start_capture,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=8
        )
        self.capture_btn.pack(side="left", padx=5, fill="x", expand=True)

        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel_capture,
            fg_color="#6B7280",
            hover_color="#4B5563",
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=5, fill="x", expand=True)

        self.train_btn = ctk.CTkButton(
            button_frame,
            text="Train Model",
            command=self.train_model,
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=8
        )
        self.train_btn.pack(side="left", padx=5, fill="x", expand=True)

        self.load_students()
        self.load_teachers()

    def on_student_double_click(self, event=None):
        """Handle student double click - start capture for student only"""
        try:
            selected = None
            if hasattr(self.student_listbox, 'curselection'):
                selection = self.student_listbox.curselection()
                if selection:
                    selected = self.student_listbox.get(selection[0])
            else:
                selected = self.student_listbox.get()

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
            print(f"Error handling student double click: {e}")
            messagebox.showerror("Error", f"Failed to select student: {str(e)}")

    def on_teacher_double_click(self, event=None):
        """Handle teacher double click - start capture for teacher only"""
        try:
            selected = None
            if hasattr(self.teacher_listbox, 'curselection'):
                selection = self.teacher_listbox.curselection()
                if selection:
                    selected = self.teacher_listbox.get(selection[0])
            else:
                selected = self.teacher_listbox.get()

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
            print(f"Error handling teacher double click: {e}")
            messagebox.showerror("Error", f"Failed to select teacher: {str(e)}")

    def load_students(self):
        """Load all students into listbox"""
        try:
            students = self.student_db.get_all_students()
            self.all_students = students
            self._populate_listbox(self.student_listbox, students, person_type="student")
        except Exception as e:
            print(f"Error loading students: {e}")
            messagebox.showerror("Database Error", f"Failed to load students: {str(e)}")

    def load_teachers(self):
        """Load all teachers into listbox"""
        try:
            teachers = self.teacher_db.get_all_teachers()
            self.all_teachers = teachers
            self._populate_listbox(self.teacher_listbox, teachers, person_type="teacher")
        except Exception as e:
            print(f"Error loading teachers: {e}")
            messagebox.showerror("Database Error", f"Failed to load teachers: {str(e)}")

    def _populate_listbox(self, listbox, items, person_type):
        """Helper to populate listbox"""
        try:
            if hasattr(listbox, 'delete'):
                listbox.delete(0, "end")

            for item in items:
                if isinstance(item, dict):
                    if person_type == "student" and 'student_id' in item and 'full_name' in item:
                        listbox.insert("end", f"{item['student_id']} - {item['full_name']}")
                    elif person_type == "teacher" and 'user_id' in item and 'name' in item:
                        listbox.insert("end", f"{item['user_id']} - {item['name']}")
        except Exception as e:
            print(f"Error populating listbox: {e}")

    def filter_students(self):
        """Filter student list based on search"""
        search_text = self.student_search_var.get().lower()
        filtered = [s for s in self.all_students
                    if search_text in str(s['student_id']).lower() or search_text in s['full_name'].lower()]
        self._populate_listbox(self.student_listbox, filtered, person_type="student")

    def filter_teachers(self):
        """Filter teacher list based on search"""
        search_text = self.teacher_search_var.get().lower()
        filtered = [t for t in self.all_teachers
                    if search_text in str(t['user_id']).lower() or search_text in t['name'].lower()]
        self._populate_listbox(self.teacher_listbox, filtered, person_type="teacher")

    def on_student_select(self):
        """Handle student selection"""
        try:
            selected = None
            if hasattr(self.student_listbox, 'curselection'):
                selection = self.student_listbox.curselection()
                if selection:
                    selected = self.student_listbox.get(selection[0])
            else:
                selected = self.student_listbox.get()

            if selected:
                student_id, student_name = selected.split(" - ", 1)
                self.id_entry.delete(0, "end")
                self.id_entry.insert(0, student_id)
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, student_name)

                self.person_type.set("student")
        except Exception as e:
            print(f"Error handling student selection: {e}")

    def on_teacher_select(self):
        """Handle teacher selection"""
        try:
            selected = None
            if hasattr(self.teacher_listbox, 'curselection'):
                selection = self.teacher_listbox.curselection()
                if selection:
                    selected = self.teacher_listbox.get(selection[0])
            else:
                selected = self.teacher_listbox.get()

            if selected:
                teacher_id, teacher_name = selected.split(" - ", 1)
                self.teacher_entry.delete(0, "end")
                self.teacher_entry.insert(0, teacher_id)
                self.teacher_name_entry.delete(0, "end")
                self.teacher_name_entry.insert(0, teacher_name)

                self.person_type.set("teacher")
        except Exception as e:
            print(f"Error handling teacher selection: {e}")

    def validate_inputs(self):
        """Validate user inputs before starting capture"""
        student_id = self.id_entry.get().strip()
        student_name = self.name_entry.get().strip()
        teacher_id = self.teacher_entry.get().strip()
        teacher_name = self.teacher_name_entry.get().strip()

        if not ((student_id and student_name) or (teacher_id and teacher_name)):
            messagebox.showwarning("Input Error", "Please select at least one student or teacher")
            return False

        if student_id and student_name:
            self.person_type.set("student")
            self.current_student = {"id": student_id, "name": student_name}
            self.current_teacher = None
        elif teacher_id and teacher_name:
            self.person_type.set("teacher")
            self.current_teacher = {"id": teacher_id, "name": teacher_name}
            self.current_student = None

        return True

    def start_capture(self):
        """Start face capturing process"""
        if not self.validate_inputs():
            return

        if self.person_type.get() == "student":
            person_id = self.id_entry.get().strip()
            person_name = self.name_entry.get().strip()
            person_type_folder = "students"
        else:
            person_id = self.teacher_entry.get().strip()
            person_name = self.teacher_name_entry.get().strip()
            person_type_folder = "teachers"

        main_dataset_dir = DATASET_PATH
        os.makedirs(main_dataset_dir, exist_ok=True)

        person_dir = os.path.join(main_dataset_dir, person_type_folder)
        os.makedirs(person_dir, exist_ok=True)

        self.dataset_dir = os.path.join(person_dir, f"{person_id}_{person_name}")
        os.makedirs(self.dataset_dir, exist_ok=True)

        try:
            camera_index = int(self.camera_index_var.get())
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to initialize camera: {str(e)}")
            return

        self.capture_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.train_btn.configure(state="disabled")
        self.progress_label.configure(text="Starting capture...")
        self.progress_bar.set(0)

        self.images_captured = 0
        self.is_capturing = True

        self.update_camera_feed()

    def update_camera_feed(self):
        """Update camera feed and capture faces"""
        if not self.is_capturing:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.reset_capture_state()
            messagebox.showerror("Error", "Failed to read from camera")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)

        for top, right, bottom, left in face_locations:
            cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)

            if self.images_captured < TOTAL_IMAGES:
                face_img = rgb_frame[top:bottom, left:right]
                face_img = cv2.resize(face_img, (IMG_SIZE, IMG_SIZE))
                img_path = os.path.join(self.dataset_dir, f"{self.images_captured}.jpg")
                face_img_bgr = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
                cv2.imwrite(img_path, face_img_bgr)

                self.images_captured += 1
                progress = (self.images_captured / TOTAL_IMAGES)
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"Captured {self.images_captured}/{TOTAL_IMAGES} images")

                if self.images_captured >= TOTAL_IMAGES:
                    self.reset_capture_state()
                    self.progress_label.configure(text="Capture complete")
                    self.update_database_with_photo(img_path)
                    messagebox.showinfo("Success", f"Successfully captured {TOTAL_IMAGES} images and updated database")
                    return

        preview_size = (320, 240)
        if 'UI_CONFIG' in globals() and 'preview_size' in UI_CONFIG:
            preview_size = UI_CONFIG['preview_size']

        img = Image.fromarray(rgb_frame)
        img = img.resize((preview_size[0], preview_size[1]), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)
        self.preview_label.configure(image=img_tk)
        self.preview_label.image = img_tk

        if self.is_capturing:
            self.after(30, self.update_camera_feed)

    def cancel_capture(self):
        """Cancel the ongoing capture"""
        self.is_capturing = False
        self.reset_capture_state()
        self.progress_label.configure(text="Capture cancelled")
        self.progress_bar.set(0)

    def reset_capture_state(self):
        """Reset UI state after capture"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

        self.is_capturing = False
        self.capture_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.train_btn.configure(state="normal")

    def update_database_with_photo(self, img_path):
        """Update the database with the photo path after capture"""
        try:
            if self.person_type.get() == "student":
                student_id = self.current_student["id"]
                self.student_db.update_student(student_id, photo=img_path)
            else:
                teacher_id = self.current_teacher["id"]
                self.teacher_db.update_teacher(teacher_id, photo=img_path)
        except Exception as e:
            print(f"Error updating database with photo: {e}")
            messagebox.showerror("Database Error", f"Failed to update database with photo: {str(e)}")

    def train_model(self):
        """Train the face recognition model using SVM"""
        try:
            messagebox.showinfo("Training", "Starting model training. This may take a while.")

            encodings = []
            labels = []
            label_map = {}
            reverse_label_map = {}
            label_id = 0

            students_path = os.path.join(DATASET_PATH, "students")
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
                        reverse_label_map[label_id] = {
                            "id": student_id,
                            "name": student_name,
                            "type": "student"
                        }

                        for img_name in os.listdir(folder_path):
                            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                                img_path = os.path.join(folder_path, img_name)
                                img = face_recognition.load_image_file(img_path)
                                face_encodings = face_recognition.face_encodings(img)
                                if face_encodings:
                                    encodings.append(face_encodings[0])
                                    labels.append(label_id)

                        label_id += 1

            teachers_path = os.path.join(DATASET_PATH, "teachers")
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
                        reverse_label_map[label_id] = {
                            "id": teacher_id,
                            "name": teacher_name,
                            "type": "teacher"
                        }

                        for img_name in os.listdir(folder_path):
                            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                                img_path = os.path.join(folder_path, img_name)
                                img = face_recognition.load_image_file(img_path)
                                face_encodings = face_recognition.face_encodings(img)
                                if face_encodings:
                                    encodings.append(face_encodings[0])
                                    labels.append(label_id)

                        label_id += 1

            if not encodings or len(set(labels)) < 2:
                messagebox.showwarning("Training Error",
                                       "Not enough data to train. Need at least 2 different people with faces detected.")
                return

            X = np.array(encodings)
            y = np.array(labels)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            svm = SVC(kernel='linear', probability=True)
            svm.fit(X_train, y_train)

            y_pred = svm.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            os.makedirs("models", exist_ok=True)
            model_path = os.path.join("models", "face_recognition_svm.pkl")
            joblib.dump(svm, model_path)

            label_map_path = os.path.join("models", "label_map.pickle")
            with open(label_map_path, "wb") as f:
                pickle.dump(reverse_label_map, f)

            messagebox.showinfo(
                "Training Complete",
                f"Model trained successfully!\n\nTest Accuracy: {accuracy:.2f}"
            )

        except Exception as e:
            messagebox.showerror("Training Error", f"Failed to train model: {str(e)}")
            print(f"Training error: {e}")

    def __del__(self):
        """Cleanup resources"""
        self.is_capturing = False
        if hasattr(self, 'cap') and self.cap and self.cap.isOpened():
            self.cap.release()

    @staticmethod
    def show_capture(parent, db_connection):
        """Entry point to show the capture interface"""
        capture_frame = CaptureFaces(parent, db_connection)
        capture_frame.pack(fill="both", expand=True)
        return capture_frame