import os
import pickle
import queue
import cv2
import joblib
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
from datetime import datetime, timedelta
import time
import face_recognition
import logging
from database import SeanceDB, AttendanceDB, StudentDB, TeacherDB
from config import Theme

logging.basicConfig(filename='face_recognition.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class CameraWindow:
    def __init__(self, parent, model, reverse_label_map):
        self.parent = parent
        self.model = model
        self.reverse_label_map = reverse_label_map
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Camera Feed")
        self.window.geometry("640x480")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()

        # Configure window background
        self.window.configure(fg_color=self.theme["background"][0 if ctk.get_appearance_mode() == "Light" else 1])

        self.camera_label = ctk.CTkLabel(self.window, text="")
        self.camera_label.pack(fill="both", expand=True)

        self.camera = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=1)
        self.detection_results = queue.Queue(maxsize=1)
        self.process_thread = None
        self.capture_thread = None
        self.display_thread = None

        # Apply theme to label
        self.apply_theme()

    def apply_theme(self):
        """Apply theme to the camera window"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        self.camera_label.configure(fg_color=get_color(self.theme["background"]))

    def start_camera(self):
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            for alt_index in range(1, 3):
                self.camera.release()
                self.camera = cv2.VideoCapture(alt_index, cv2.CAP_DSHOW)
                if self.camera.isOpened():
                    break
            if not self.camera.isOpened():
                logging.error("Failed to open camera")
                return False

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.is_running = True

        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.process_thread = threading.Thread(target=self._process_frames, daemon=True)
        self.display_thread = threading.Thread(target=self._update_display, daemon=True)
        self.capture_thread.start()
        self.process_thread.start()
        self.display_thread.start()

        return True

    def _capture_frames(self):
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                try:
                    if not self.frame_queue.full():
                        self.frame_queue.put_nowait(frame.copy())
                    else:
                        with self.frame_queue.mutex:
                            self.frame_queue.queue.clear()
                        self.frame_queue.put_nowait(frame.copy())
                except queue.Full:
                    pass
            else:
                logging.warning("Failed to capture frame")
                time.sleep(0.01)

    def _process_frames(self):
        while self.is_running:
            try:
                frame = self.frame_queue.get(timeout=0.5)
                if frame is None:
                    continue

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)

                face_locations = face_recognition.face_locations(small_frame, model="hog")
                face_locations = [
                    (int(top / 0.25), int(right / 0.25), int(bottom / 0.25), int(left / 0.25))
                    for top, right, bottom, left in face_locations
                ]

                face_names = []
                if face_locations and self.model and self.reverse_label_map:
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    for encoding in face_encodings:
                        try:
                            label_id = self.model.predict([encoding])[0]
                            prob = max(self.model.predict_proba([encoding])[0])
                            if prob < 0.6:
                                face_names.append(("Unknown", None, None))
                            else:
                                person_info = self.reverse_label_map.get(label_id, {})
                                name = person_info.get('name', 'Unknown')
                                person_id = person_info.get('student_id', person_info.get('user_id', None))
                                person_type = person_info.get('type', None)
                                face_names.append((name, person_id, person_type))
                        except Exception as e:
                            logging.error(f"Error predicting face: {e}")
                            face_names.append(("Unknown", None, None))
                else:
                    face_names = [("Unknown", None, None)] * len(face_locations)

                if not self.detection_results.full():
                    self.detection_results.put_nowait((frame, face_locations, face_names))

            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing frame: {e}")

    def _update_display(self):
        while self.is_running:
            try:
                frame, face_locations, face_names = self.detection_results.get(timeout=0.5)

                for (top, right, bottom, left), (name, _, _) in zip(face_locations, face_names):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img_tk = ctk.CTkImage(light_image=img, size=(640, 480))

                self.camera_label.configure(image=img_tk)
                self.camera_label.image = img_tk

                self.parent.update_recognized_persons(face_names, face_locations)

            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error updating display: {e}")

    def on_close(self):
        self.is_running = False
        if self.camera and self.camera.isOpened():
            self.camera.release()
        self.window.destroy()

class FaceRecognition(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.parent = parent  # MainApp instance
        self.db_connection = db_connection
        self.camera_window = None
        self.model = None
        self.reverse_label_map = None
        self.is_running = False
        self.recognition_start_time = None
        self.last_recognitions = {}
        self.recognition_durations = {}
        self.attendance_db = AttendanceDB(self.db_connection)
        self.seance_db = SeanceDB(self.db_connection)
        self.student_db = StudentDB(self.db_connection)
        self.teacher_db = TeacherDB(self.db_connection)
        self.current_seance = None
        self.seance_end_time = None
        self.after_id = None
        self.seance_widgets = []

        # Apply theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()

        # Load model and setup UI
        self.load_model()
        self.setup_ui()
        self.check_seance_and_start()

    def load_model(self):
        try:
            model_path = os.path.join("models", "face_recognition_svm.pkl")
            label_map_path = os.path.join("models", "label_map.pickle")

            if not os.path.exists(model_path) or not os.path.exists(label_map_path):
                raise FileNotFoundError("Model or label map files not found")

            self.model = joblib.load(model_path)
            with open(label_map_path, 'rb') as f:
                self.reverse_label_map = pickle.load(f)

            valid_label_map = {}
            for label_id, info in self.reverse_label_map.items():
                person_id = info.get('student_id', info.get('user_id', None))
                person_type = info.get('type', None)
                if person_id and person_type and self.validate_person_id(person_id, person_type):
                    valid_label_map[label_id] = info
                else:
                    logging.warning(f"Removing invalid entry from label map: {info}")
            self.reverse_label_map = valid_label_map

            logging.info("Model and validated label map loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load model: {e}")
            messagebox.showerror("Loading Error", f"Failed to load model: {str(e)}")
            self.model = None
            self.reverse_label_map = None

    def setup_ui(self):

        self.configure(fg_color=self.theme["background"])
        self.main_frame = ctk.CTkFrame(self, fg_color=self.theme["frame"], corner_radius=6)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Face Recognition",
            font=self.theme["font_large"],
            text_color=self.theme["primary"]
        )
        title_label.pack(pady=(20, 10))

        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20)

        left_frame = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"], corner_radius=6)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            info_frame,
            text="Seance Information",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        self.seance_label = ctk.CTkLabel(
            info_frame,
            text="Seance: None",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"],
            wraplength=200,
            anchor="w"
        )
        self.seance_label.pack(fill="x", pady=5)

        self.status_label = ctk.CTkLabel(
            info_frame,
            text="Status: Ready" if self.model else "Status: Model not loaded",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"],
            anchor="w"
        )
        self.status_label.pack(fill="x", pady=5)

        self.duration_label = ctk.CTkLabel(
            info_frame,
            text="Remaining Time: 00:00:00",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"],
            anchor="w"
        )
        self.duration_label.pack(fill="x", pady=5)

        self.progress_bar = ctk.CTkProgressBar(
            info_frame,
            height=10,
            progress_color=self.theme["primary"],
            fg_color=self.theme["sidebar"]
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)

        seance_list_frame = ctk.CTkFrame(left_frame, fg_color=self.theme["frame"])
        seance_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            seance_list_frame,
            text="Available Seances",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        self.seance_list = ctk.CTkScrollableFrame(
            seance_list_frame,
            fg_color="transparent",
            height=100
        )
        self.seance_list.pack(fill="both", expand=True)
        self.update_seance_list()

        controls_frame = ctk.CTkFrame(left_frame, fg_color=self.theme["frame"])
        controls_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            controls_frame,
            text="Controls",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        btn_frame = ctk.CTkFrame(controls_frame, fg_color=self.theme["frame"])
        btn_frame.pack(fill="x")

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="Start Recognition",
            command=self.start_recognition,
            fg_color=self.theme["success"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            font=self.theme["font_normal"],
            state="normal" if self.model else "disabled",
            corner_radius=6
        )
        self.start_btn.pack(fill="x", pady=5)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="Stop Recognition",
            command=self.stop_recognition,
            fg_color=self.theme["danger"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            font=self.theme["font_normal"],
            state="disabled",
            corner_radius=6
        )
        self.stop_btn.pack(fill="x", pady=5)

        right_frame = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"], corner_radius=6)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        content_frame.columnconfigure(1, weight=1)

        self.persons_frame = ctk.CTkScrollableFrame(
            right_frame,
            label_text="Recognized Persons",
            label_font=self.theme["font_title"],
            label_fg_color=self.theme["background"],
            label_text_color=self.theme["primary"],
            fg_color="transparent",
            height=200
        )
        self.persons_frame.pack(fill="both", expand=True, padx=10, pady=10)

        stats_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            stats_frame,
            text="Session Statistics",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 10))

        self.stats_labels = {
            'total': self.create_stat_label(stats_frame, "Total Recognitions:", "0"),
            'unique': self.create_stat_label(stats_frame, "Unique Persons:", "0"),
            'current': self.create_stat_label(stats_frame, "Currently Present:", "0")
        }

    def create_stat_label(self, parent, text, value):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            frame,
            text=text,
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"],
            anchor="w",
            width=150
        ).pack(side="left")
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=self.theme["font_normal"],
            text_color=self.theme["primary"]
        )
        value_label.pack(side="right")
        return value_label

    def select_seance(self, seance):
        self.current_seance = seance
        seance_text = f"Seance: {seance['name_seance']} ({seance['date']} {seance['start_time']}-{seance['end_time']})"
        self.seance_label.configure(text=seance_text)
        self.update_seance_list()

        try:
            seance_date = str(seance['date'])
            start_time = str(seance['start_time'])
            end_time = str(seance['end_time'])
            start_datetime = datetime.strptime(f"{seance_date} {start_time}", '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(f"{seance_date} {end_time}", '%Y-%m-%d %H:%M:%S')
            self.seance_end_time = end_datetime

            current_time = datetime.now()
            if (seance_date == current_time.strftime('%Y-%m-%d') and
                    start_time <= current_time.strftime('%H:%M:%S') <= end_time):
                if not self.is_running:
                    self.start_recognition()
                self.update_duration()
            else:
                self.stop_recognition()
                self.duration_label.configure(text=f"Seance starts at {start_time} on {seance_date}")

        except Exception as e:
            logging.error(f"Error processing seance selection: {e}")
            self.seance_label.configure(text="Seance: Error")
            self.duration_label.configure(text="Remaining Time: Error")

    def update_seance_list(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        for widget in self.seance_widgets:
            widget.destroy()
        self.seance_widgets.clear()

        try:
            seances = self.seance_db.get_all_seances()
            if not seances:
                label = ctk.CTkLabel(
                    self.seance_list,
                    text="No seances available",
                    font=self.theme["font_normal"],
                    text_color=get_color(self.theme["secondary"])
                )
                label.pack(fill="x", pady=5)
                self.seance_widgets.append(label)
                return

            for seance in seances:
                seance_text = f"{seance['name_seance']} ({seance['date']} {seance['start_time']}-{seance['end_time']})"
                button = ctk.CTkButton(
                    self.seance_list,
                    text=seance_text,
                    font=self.theme["font_normal"],
                    fg_color=get_color(self.theme["primary"]) if seance == self.current_seance else get_color(self.theme["sidebar"]),
                    hover_color=get_color(self.theme["button_hover"]),
                    text_color=get_color(self.theme["secondary"]),
                    command=lambda s=seance: self.select_seance(s),
                    anchor="w",
                    corner_radius=6
                )
                button.pack(fill="x", pady=2)
                self.seance_widgets.append(button)

        except Exception as e:
            logging.error(f"Error updating seance list: {e}")
            label = ctk.CTkLabel(
                self.seance_list,
                text="Error loading seances",
                font=self.theme["font_normal"],
                text_color=get_color(self.theme["danger"])
            )
            label.pack(fill="x", pady=5)
            self.seance_widgets.append(label)

    def check_seance_and_start(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        try:
            if not self.current_seance:
                self.seance_label.configure(text="Seance: None")
                self.duration_label.configure(text="Remaining Time: 00:00:00")
                self.progress_bar.set(0)
                if self.is_running:
                    self.stop_recognition()
                self.update_seance_list()
                return

            current_time = datetime.now()
            seance_date = str(self.current_seance['date'])
            start_time = str(self.current_seance['start_time'])
            end_time = str(self.current_seance['end_time'])

            start_datetime = datetime.strptime(f"{seance_date} {start_time}", '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(f"{seance_date} {end_time}", '%Y-%m-%d %H:%M:%S')
            self.seance_end_time = end_datetime

            self.update_seance_list()

            if (seance_date == current_time.strftime('%Y-%m-%d') and
                    start_time <= current_time.strftime('%H:%M:%S') <= end_time):
                if not self.is_running:
                    self.start_recognition()
                self.update_duration()
            else:
                if self.is_running:
                    self.stop_recognition()
                remaining = (start_datetime - current_time).total_seconds()
                if remaining > 0:
                    self.duration_label.configure(
                        text=f"Seance starts in {str(timedelta(seconds=int(remaining)))}"
                    )
                else:
                    self.duration_label.configure(
                        text=f"Seance ended at {end_time} on {seance_date}"
                    )
                self.progress_bar.set(0)

        except Exception as e:
            logging.error(f"Error checking seance: {e}")
            self.seance_label.configure(text="Seance: Error")
            self.update_seance_list()
        finally:
            if self.winfo_exists():
                self.after_id = self.after(30000, self.check_seance_and_start)

    def start_recognition(self):
        if not self.model:
            messagebox.showerror("Error", "Model not loaded")
            return

        self.camera_window = CameraWindow(self, self.model, self.reverse_label_map)
        if not self.camera_window.start_camera():
            messagebox.showerror("Camera Error", "Could not open camera")
            self.camera_window = None
            return

        self.is_running = True
        self.recognition_start_time = time.time()
        self.last_recognitions = {}
        self.recognition_durations = {}
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Status: Recognition Active", text_color=self.theme["success"])

        for widget in self.persons_frame.winfo_children():
            widget.destroy()

        self.update_duration()

    def validate_person_id(self, person_id, person_type):
        try:
            if person_type == "student":
                student = self.student_db.get_student_by_id(person_id)
                return student is not None
            elif person_type == "teacher":
                cursor = self.db_connection.get_connection().cursor(dictionary=True)
                query = "SELECT user_id FROM teachers WHERE user_id = %s"
                cursor.execute(query, (person_id,))
                teacher = cursor.fetchone()
                cursor.close()
                return teacher is not None
            return False
        except Exception as e:
            logging.error(f"Error validating {person_type} ID {person_id}: {e}")
            return False

    def update_recognized_persons(self, face_names, face_locations):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        if not self.is_running or not self.current_seance:
            return

        current_time = time.time()
        seance_id = self.current_seance['seance_id']

        for name, person_id, person_type in face_names:
            if name == "Unknown" or not person_id or not person_type:
                logging.warning(f"Skipping recognition: name={name}, person_id={person_id}, type={person_type}")
                continue

            if not self.validate_person_id(person_id, person_type):
                logging.warning(f"Invalid {person_type} ID {person_id} for {name}")
                continue

            person_key = f"{person_type}_{person_id}"
            if person_key not in self.last_recognitions:
                self.last_recognitions[person_key] = []
                self.recognition_durations[person_key] = 0

            try:
                status = "present"
                success = self.attendance_db.record_attendance(
                    seance_id, person_id, status, person_type
                )
                if success:
                    logging.info(f"Attendance recorded: {person_type} {name} (ID: {person_id}) for seance {seance_id}")
                else:
                    logging.warning(f"Failed to record attendance for {person_type} {name} (ID: {person_id})")
            except Exception as e:
                logging.error(f"Error recording attendance for {person_type} {name}: {e}")
                continue

            self.last_recognitions[person_key].append(current_time)
            self.recognition_durations[person_key] += 1

            for widget in self.persons_frame.winfo_children():
                if widget.cget("text").startswith(f"{name} ({person_type})"):
                    widget.destroy()
                    break

            person_label = ctk.CTkLabel(
                self.persons_frame,
                text=f"{name} ({person_type}) - {datetime.now().strftime('%H:%M:%S')}",
                font=self.theme["font_normal"],
                text_color=get_color(self.theme["secondary"])
            )
            person_label.pack(anchor="w", pady=2)

        unique_persons = len(self.recognition_durations)
        total_recognitions = sum(len(times) for times in self.last_recognitions.values())
        current_persons = sum(1 for person in self.last_recognitions
                              if current_time - self.last_recognitions[person][-1] < 5)

        self.stats_labels['total'].configure(text=str(total_recognitions))
        self.stats_labels['unique'].configure(text=str(unique_persons))
        self.stats_labels['current'].configure(text=str(current_persons))

    def update_duration(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        if not self.is_running or not self.current_seance:
            return

        current_time = datetime.now()
        if self.seance_end_time and current_time >= self.seance_end_time:
            self.stop_recognition()
            self.duration_label.configure(
                text=f"Seance ended at {self.current_seance['end_time']} on {self.current_seance['date']}"
            )
            self.progress_bar.set(1)
            return

        if self.seance_end_time:
            remaining = (self.seance_end_time - current_time).total_seconds()
            total_duration = (self.seance_end_time - datetime.strptime(
                f"{self.current_seance['date']} {self.current_seance['start_time']}",
                '%Y-%m-%d %H:%M:%S'
            )).total_seconds()
            progress = 1 - (remaining / total_duration) if total_duration > 0 else 0
            self.progress_bar.set(progress)
            self.duration_label.configure(
                text=f"Remaining Time: {str(timedelta(seconds=int(remaining)))}"
            )
        else:
            elapsed = time.time() - self.recognition_start_time
            self.duration_label.configure(
                text=f"Session Duration: {str(timedelta(seconds=int(elapsed)))}"
            )

        self.after(1000, self.update_duration)

    def stop_recognition(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        self.is_running = False
        if self.camera_window:
            self.camera_window.on_close()
            self.camera_window = None
        self.start_btn.configure(state="normal" if self.model else "disabled")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Idle", text_color=get_color(self.theme["secondary"]))
        self.progress_bar.set(0)

        if self.recognition_start_time:
            elapsed = time.time() - self.recognition_start_time
            self.duration_label.configure(
                text=f"Last Session: {str(timedelta(seconds=int(elapsed)))}"
            )

    def destroy(self):
        self.stop_recognition()
        if self.after_id:
            self.after_cancel(self.after_id)
        super().destroy()