import os
import threading
from tkinter import messagebox
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from customtkinter import ctk_tk

from train import FaceTrainer
from config import DATASET_PATH, IMG_SIZE, FACE_CONFIG, UI_CONFIG
from database import *


class CaptureFaces(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="#f5f7fa")
        self.parent = parent
        self.is_capturing = False
        self.is_detecting = False
        self.images_captured = 0
        self.cap = None
        self.model = None
        self.label_map = None
        self.current_student = None
        self.current_teacher = None
        self.db_connection = db_connection
        self.info_fetcher = Get_info_to_capture(self.db_connection)
        self.seach_prof = TeacherDB(self.db_connection)
        self.seach_stud=StudentDB(self.db_connection)


        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Initialize database connection
        self.db = DatabaseConnection()




        # Setup UI
        self.create_ui()

    def create_ui(self):
        """Create the user interface"""
        # Setup main layout with two columns
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with improved styling
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(
            title_frame,
            text="Face Capture",
            font=("Arial", 20, "bold"),
            text_color="#1E3A8A"
        )
        title.pack(pady=10)

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Register student faces for attendance tracking",
            font=("Arial", 10),
            text_color="#6B7280"
        )
        subtitle.pack()

        # Create paned window for left and right panels
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel - Input and search lists
        left_panel = ctk.CTkFrame(content_frame, width=400)
        left_panel.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        # Right panel
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        # Student search section
        student_section = ctk.CTkFrame(left_panel)
        student_section.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(student_section, text="Student Selection", font=("Arial", 16, "bold")).pack(anchor="w",
                                                                                                 pady=(0, 5))

        # Student search box
        self.student_search_var = ctk.StringVar()
        self.student_search_var.trace("w", self.load_students)
        student_search_frame = ctk.CTkFrame(student_section)
        student_search_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(student_search_frame, text="Search:").pack(side="left", padx=5)
        self.student_search_entry = ctk.CTkEntry(student_search_frame, textvariable=self.student_search_var, width=200)
        self.student_search_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Student listbox with scrollbar
        student_list_frame = ctk.CTkFrame(student_section)
        student_list_frame.pack(fill="both", expand=True, pady=5)

        # Create listbox - handle compatibility with different versions of customtkinter
        try:
            self.student_listbox = ctk.CTkListbox(student_list_frame, height=150, command=self.on_student_select)
            self.student_listbox.pack(side="left", fill="both", expand=True)

            student_scrollbar = ctk.CTkScrollbar(student_list_frame, command=self.student_listbox.yview)
            student_scrollbar.pack(side="right", fill="y")
            self.student_listbox.configure(yscrollcommand=student_scrollbar.set)
        except AttributeError:
            # Fallback for older customtkinter versions without CTkListbox
            import tkinter as tk
            self.student_listbox = tk.Listbox(student_list_frame, height=10, exportselection=0)
            self.student_listbox.pack(side="left", fill="both", expand=True)
            self.student_listbox.bind('<<ListboxSelect>>', lambda e: self.on_student_select(
                self.student_listbox.get(
                    self.student_listbox.curselection()[0]) if self.student_listbox.curselection() else None
            ))

            student_scrollbar = tk.Scrollbar(student_list_frame, command=self.student_listbox.yview)
            student_scrollbar.pack(side="right", fill="y")
            self.student_listbox.configure(yscrollcommand=student_scrollbar.set)

        # Populate student listbox
        self.populate_student_listbox()

        # Student details frame
        student_details_frame = ctk.CTkFrame(student_section)
        student_details_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(student_details_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.id_entry = ctk.CTkEntry(student_details_frame)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(student_details_frame, text="Student Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ctk.CTkEntry(student_details_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        student_details_frame.columnconfigure(1, weight=1)

        # Teacher search section
        teacher_section = ctk.CTkFrame(left_panel)
        teacher_section.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(teacher_section, text="Teacher Selection", font=("Arial", 16, "bold")).pack(anchor="w",
                                                                                                 pady=(0, 5))

        # Teacher search box
        self.teacher_search_var = ctk.StringVar()
        self.teacher_search_var.trace("w", self.seach_prof())
        teacher_search_frame = ctk.CTkFrame(teacher_section)
        teacher_search_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(teacher_search_frame, text="Search:").pack(side="left", padx=5)
        self.teacher_search_entry = ctk.CTkEntry(teacher_search_frame, textvariable=self.teacher_search_var, width=200)
        self.teacher_search_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Teacher listbox with scrollbar
        teacher_list_frame = ctk.CTkFrame(teacher_section)
        teacher_list_frame.pack(fill="both", expand=True, pady=5)

        # Create teacher listbox with fallback
        try:
            self.teacher_listbox = ctk.CTkListbox(teacher_list_frame, height=150, command=self.on_teacher_select)
            self.teacher_listbox.pack(side="left", fill="both", expand=True)

            teacher_scrollbar = ctk.CTkScrollbar(teacher_list_frame, command=self.teacher_listbox.yview)
            teacher_scrollbar.pack(side="right", fill="y")
            self.teacher_listbox.configure(yscrollcommand=teacher_scrollbar.set)
        except AttributeError:
            # Fallback for older customtkinter versions without CTkListbox
            import tkinter as tk
            self.teacher_listbox = tk.Listbox(teacher_list_frame, height=10, exportselection=0)
            self.teacher_listbox.pack(side="left", fill="both", expand=True)
            self.teacher_listbox.bind('<<ListboxSelect>>', lambda e: self.on_teacher_select(
                self.teacher_listbox.get(
                    self.teacher_listbox.curselection()[0]) if self.teacher_listbox.curselection() else None
            ))

            teacher_scrollbar = tk.Scrollbar(teacher_list_frame, command=self.teacher_listbox.yview)
            teacher_scrollbar.pack(side="right", fill="y")
            self.teacher_listbox.configure(yscrollcommand=teacher_scrollbar.set)

        # Populate teacher listbox
        self.populate_teacher_listbox()

        # Teacher details frame
        teacher_details_frame = ctk.CTkFrame(teacher_section)
        teacher_details_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(teacher_details_frame, text="Teacher ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.teacher_entry = ctk.CTkEntry(teacher_details_frame)
        self.teacher_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(teacher_details_frame, text="Teacher Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.teacher_name_entry = ctk.CTkEntry(teacher_details_frame)
        self.teacher_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        teacher_details_frame.columnconfigure(1, weight=1)

        # Camera selection
        camera_frame = ctk.CTkFrame(left_panel)
        camera_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(camera_frame, text="Camera Settings", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 5))

        camera_select_frame = ctk.CTkFrame(camera_frame)
        camera_select_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(camera_select_frame, text="Select Camera:").pack(side="left", padx=5)

        # Add camera dropdown - using combobox
        self.camera_index_var = ctk.StringVar(value=str(FACE_CONFIG['camera_index']))
        self.camera_dropdown = ctk.CTkComboBox(
            camera_select_frame,
            variable=self.camera_index_var,
            values=[str(i) for i in range(5)],
            width=100
        )
        self.camera_dropdown.pack(side="left", padx=5)

        # Right panel - Preview and controls
        right_panel = ctk.CTkFrame(content_frame, width=500)
        right_panel.pack(side="right", fill="both", padx=10, pady=10, expand=True)

        # Preview section
        preview_section = ctk.CTkFrame(right_panel)
        preview_section.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(preview_section, text="Camera Preview", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 5))

        # Preview frame with border
        preview_container = ctk.CTkFrame(preview_section, fg_color="#D1D5DB", corner_radius=8)
        preview_container.pack(fill="both", expand=True, pady=10)

        self.preview_frame = ctk.CTkFrame(
            preview_container,
            width=UI_CONFIG['preview_size'][0],
            height=UI_CONFIG['preview_size'][1],
            fg_color="#F3F4F6"
        )
        self.preview_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Camera feed will appear here",
            font=("Arial", 14)
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Progress indicators
        progress_frame = ctk.CTkFrame(right_panel)
        progress_frame.pack(fill="x", padx=10, pady=10)

        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(pady=5, fill="x")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to capture",
            font=("Arial", 12),
            text_color="#4B5563"
        )
        self.progress_label.pack()

        # Action buttons - Using explicit buttons for better compatibility
        button_frame = ctk.CTkFrame(right_panel)
        button_frame.pack(pady=15, fill="x")

        # Create buttons using direct instantiation, not variables
        ctk.CTkButton(
            button_frame,
            text="Start Capture",
            command=self.start_capture,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=8
        ).pack(side="left", padx=10, fill="x", expand=True)

        ctk.CTkButton(
            button_frame,
            text="Train Model",
            command=self.start_training,
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=8
        ).pack(side="left", padx=10, fill="x", expand=True)

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=self.stop_process,
            fg_color="#EF4444",
            hover_color="#DC2626",
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10, fill="x", expand=True)

    def populate_student_listbox(self):
        self.populate_listbox(self.student_listbox, self.get_all_students())

    def populate_teacher_listbox(self):
        self.populate_listbox(self.teacher_listbox, self.get_all_teachers())

    def load_students(self):
        self.student_listbox.delete(0, "end")
        students = self.seach_stud.all_students()
        for student in students:
            self.student_listbox.insert("end", f"{student['id']} - {student['name']}")

    def load_teachers(self):
        self.teacher_listbox.delete(0, "end")
        teachers = self.seach_prof.all_teachers()
        for teacher in teachers:
            self.teacher_listbox.insert("end", f"{teacher['id']} - {teacher['name']}")
    def on_student_select(self, selected_item):
        """Handle student selection from listbox"""
        if selected_item:
            parts = selected_item.split(" - ", 1)
            if len(parts) == 2:
                student_id, student_name = parts
                self.id_entry.delete(0, "end")
                self.id_entry.insert(0, student_id)
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, student_name)

    def on_teacher_select(self, selected_item):
        """Handle teacher selection from listbox"""
        if selected_item:
            parts = selected_item.split(" - ", 1)
            if len(parts) == 2:
                teacher_id, teacher_name = parts
                self.teacher_entry.delete(0, "end")
                self.teacher_entry.insert(0, teacher_id)
                self.teacher_name_entry.delete(0, "end")
                self.teacher_name_entry.insert(0, teacher_name)

    def validate(self, student_id, teacher_id):
        """Validate student ID and fetch name from database"""
        if not student_id:
            messagebox.showwarning("Input Error", "Please enter a Student ID")
            return None, None
        if not teacher_id:
            messagebox.showwarning("Input Error", "Please enter a Teacher ID")
            return None, None

        try:
            student_data, teacher_data = self.info_fetcher.get_info(student_id, teacher_id)

            if not student_data or not teacher_data:
                messagebox.showerror("Error", "Student or Teacher not found")
                return None, None

            return student_data['name'], teacher_data['name']
        except Exception as e:
            messagebox.showerror("Database Error", f"Query failed: {str(e)}")
            return None, None

    def start_capture(self):
        """Start the face capture process"""
        student_id = self.id_entry.get()
        teacher_id = self.teacher_entry.get()
        student_name = self.name_entry.get()
        teacher_name = self.teacher_name_entry.get()

        if not student_id or not student_name:
            messagebox.showwarning("Input Error", "Please select a student")
            return

        if not teacher_id or not teacher_name:
            messagebox.showwarning("Input Error", "Please select a teacher")
            return

        self.current_student = {
            'id': student_id,
            'name': student_name
        }
        self.current_teacher = {
            'id': teacher_id,
            'name': teacher_name
        }

        # Create dataset directory
        self.dataset_dir = os.path.join(
            DATASET_PATH,
            f"{student_id}_{student_name}_{teacher_id}_{teacher_name}"
        )
        os.makedirs(self.dataset_dir, exist_ok=True)

        # Initialize camera
        try:
            camera_index = int(self.camera_index_var.get())
            self.cap = cv2.VideoCapture(camera_index)

            if not self.cap.isOpened():
                messagebox.showerror("Camera Error",
                                   "Could not open camera. Please check if the camera is connected and try a different camera index.")
                return

            # Start capture process
            self.is_capturing = True
            self.images_captured = 0
            self.update_ui_for_capture()
            self.update_capture()
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to initialize camera: {str(e)}")
    def update_capture(self):
        """Continuously capture frames and detect faces"""
        if not self.is_capturing or not self.cap:
            return

        try:
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Camera Error", "Failed to read frame from camera")
                self.stop_capture()
                return

            # Process frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            # Handle detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)

                if self.images_captured < FACE_CONFIG['total_images']:
                    self.save_face_image(gray, x, y, w, h)
                    self.update_progress()

            # Update preview
            self.update_preview(frame_rgb)

            # Check if capture is complete
            if self.images_captured >= FACE_CONFIG['total_images']:
                self.complete_capture()
                return

            # Continue capture
            self.parent.after(30, self.update_capture)
        except Exception as e:
            messagebox.showerror("Error", f"Error during capture: {str(e)}")
            self.stop_capture()

    def save_face_image(self, frame, x, y, w, h):
        """Save detected face image to dataset"""
        face_img = frame[y:y + h, x:x + w]
        face_img = cv2.resize(face_img, (IMG_SIZE, IMG_SIZE))
        img_path = os.path.join(
            self.dataset_dir,
            f"{self.images_captured}.jpg"
        )
        cv2.imwrite(img_path, face_img)
        self.images_captured += 1

    def update_progress(self):
        """Update progress bar and label"""
        progress = self.images_captured / FACE_CONFIG['total_images']
        self.progress_bar.set(progress)
        self.progress_label.configure(
            text=f"Captured {self.images_captured}/{FACE_CONFIG['total_images']} images"
        )

    def update_preview(self, frame):
        """Update the camera preview"""
        try:
            img = Image.fromarray(frame)
            img = img.resize(UI_CONFIG['preview_size'])
            img_tk = ImageTk.PhotoImage(image=img)
            self.preview_label.configure(image=img_tk, text="")
            self.preview_label.image = img_tk  # Keep a reference
        except Exception as e:
            print(f"Error updating preview: {e}")

    def complete_capture(self):
        """Handle completion of capture process"""
        self.stop_capture()
        messagebox.showinfo(
            "Complete",
            f"Captured {self.images_captured} images of {self.current_student['name']}"
        )

        # Optionally start training automatically
        if messagebox.askyesno(
                "Training",
                "Would you like to train the model now?"
        ):
            self.start_training()

    def stop_capture(self):
        """Stop the capture process"""
        self.is_capturing = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.update_ui_after_capture()

    def update_ui_for_capture(self):
        """Update UI when capture starts"""
        # Use button_frame children to reference buttons
        try:
            button_frame = self.stop_btn.master
            for i, child in enumerate(button_frame.winfo_children()):
                if i == 0 or i == 1:  # Start Capture and Train Model buttons
                    child.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        except Exception as e:
            print(f"Error updating UI for capture: {e}")

        self.progress_label.configure(text="Capturing images...")
        self.progress_bar.set(0)

    def update_ui_after_capture(self):
        """Update UI when capture stops"""
        # Use button_frame children to reference buttons
        try:
            button_frame = self.stop_btn.master
            for i, child in enumerate(button_frame.winfo_children()):
                if i == 0 or i == 1:  # Start Capture and Train Model buttons
                    child.configure(state="normal")
            self.stop_btn.configure(state="disabled")
        except Exception as e:
            print(f"Error updating UI after capture: {e}")

        self.progress_label.configure(text="Ready")

    def stop_process(self):
        """Stop any ongoing process"""
        if self.is_capturing:
            self.stop_capture()
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def start_training(self):
        """Start the model training process"""
        if not self.validate_training_prerequisites():
            return

        # Disable UI during training
        try:
            button_frame = self.stop_btn.master
            for i, child in enumerate(button_frame.winfo_children()):
                child.configure(state="disabled")
        except Exception as e:
            print(f"Error updating UI for training: {e}")

        self.progress_label.configure(text="Training model...")
        self.progress_bar.set(0)

        # Start training in separate thread to prevent UI freezing
        training_thread = threading.Thread(target=self.train_model)
        training_thread.daemon = True
        training_thread.start()

    def validate_training_prerequisites(self):
        """Check if training can proceed"""
        if not os.path.exists(DATASET_PATH):
            messagebox.showerror(
                "Error",
                f"Dataset directory not found at {DATASET_PATH}"
            )
            return False

        if len(os.listdir(DATASET_PATH)) < 1:
            messagebox.showerror(
                "Error",
                "No student data found in dataset directory"
            )
            return False

        return True

    def train_model(self):
        """Train the face recognition model"""
        try:
            trainer = FaceTrainer()
            trainer.train()

            # Update UI on success
            self.parent.after(0, lambda: messagebox.showinfo(
                "Success",
                "Model trained successfully!"
            ))
        except Exception as e:
            # Show error message
            self.parent.after(0, lambda: messagebox.showerror(
                "Error",
                f"Training failed: {str(e)}"
            ))
        finally:
            # Restore UI
            self.parent.after(0, self.update_ui_after_training)

    def update_ui_after_training(self):
        """Restore UI after training completes"""
        try:
            button_frame = self.stop_btn.master
            for i, child in enumerate(button_frame.winfo_children()):
                if i == 0 or i == 1:  # Start Capture and Train Model buttons
                    child.configure(state="normal")
            self.stop_btn.configure(state="disabled")
        except Exception as e:
            print(f"Error updating UI after training: {e}")

        self.progress_label.configure(text="Training completed")
        self.progress_bar.set(1)

    def __del__(self):
        """Cleanup resources"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
#--- for search----------
    def populate_listbox(self, listbox, data_list):
        """Generic function to populate any listbox with data"""
        try:
            listbox.delete(0, "end")
            for item in data_list:
                listbox.insert("end", f"{item['id']} - {item['name']}")
        except Exception as e:
            print(f"Error populating listbox: {e}")

    def filter_listbox(self, listbox, data_list, search_var):
        """Generic function to filter any listbox based on search text"""
        search_text = search_var.get().lower()
        try:
            listbox.delete(0, "end")
            for item in data_list:
                if search_text in item['id'].lower() or search_text in item['name'].lower():
                    listbox.insert("end", f"{item['id']} - {item['name']}")
        except Exception as e:
            print(f"Error filtering listbox: {e}")

    # In StudentDB
    def get_all_students(self):
        if not self.db.is_connected():
            return []
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students")
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching all students: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    # In TeacherDB
    def get_all_teachers(self):
        if not self.db.is_connected():
            return []
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM teachers")
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching all teachers: {e}")
            return []
        finally:
            if cursor:
                cursor.close()


def show_capture(parent, db_connection):
    """Entry point to show the capture interface"""
    capture_frame = CaptureFaces(parent, db_connection)
    capture_frame.pack(fill="both", expand=True)