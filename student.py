<<<<<<< HEAD
import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import shutil
from database import StudentDB
from datetime import datetime
from config import Theme

class StudentInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.selected_student_id = None
        self.parent = parent
        self.db = StudentDB(db_connection)
        self.current_photo_path = None

        self.var_full_name = ctk.StringVar()
        self.var_number = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_enrollment_date = ctk.StringVar()
        self.var_ID = ctk.StringVar()
        self.var_search_id = ctk.StringVar()

        # Set the application theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()
        self.create_ui()

    def create_ui(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        self.configure(fg_color=get_color(self.theme["background"]))
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_container,
            text="👨‍🎓 Student Information",
            font=self.theme["font_large"],
            text_color=get_color(self.theme["primary"])
        ).pack(pady=(0, 20))

        content_frame = ctk.CTkFrame(main_container, fg_color=get_color(self.theme["background"]), corner_radius=15)
        content_frame.pack(fill="both", expand=True)

        form_frame = ctk.CTkFrame(content_frame, fg_color=get_color(self.theme["background"]), corner_radius=10)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        photo_frame = ctk.CTkFrame(content_frame, fg_color=get_color(self.theme["background"]), corner_radius=10)
        photo_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.create_form_fields(form_frame)
        self.create_photo_section(photo_frame)
        self.create_action_buttons(form_frame)

    def create_form_fields(self, parent):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        fields = [
            ("Full Name", "var_full_name", True),
            ("Student Number", "var_number", True),
            ("Student email", "var_email", True),
            ("Enrollment Date", "var_enrollment_date", True),
        ]
        for idx, (label_text, var_name, required) in enumerate(fields):
            ctk.CTkLabel(
                parent,
                text=label_text,
                font=self.theme["font_normal"],
                text_color=get_color(self.theme["secondary"])
            ).grid(row=idx, column=0, sticky="w", padx=10, pady=5)
            ctk.CTkEntry(
                parent,
                textvariable=getattr(self, var_name),
                font=self.theme["font_normal"],
                width=250,
                fg_color=get_color(self.theme["background"]),
                border_color=get_color(self.theme["primary"]),
                text_color=get_color(self.theme["secondary"]),
                corner_radius=8
            ).grid(row=idx, column=1, padx=10, pady=5)
            if required:
                ctk.CTkLabel(
                    parent,
                    text="*",
                    text_color=get_color(self.theme["danger"]),
                    font=("Arial", 14, "bold")
                ).grid(row=idx, column=2, sticky="w", padx=(0, 10))
        self.var_enrollment_date.set(datetime.now().strftime("%Y-%m-%d"))

    def create_photo_section(self, parent):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        self.photo_frame = ctk.CTkFrame(
            parent,
            width=200,
            height=200,
            corner_radius=10,
            fg_color=get_color(self.theme["background"])
        )
        self.photo_frame.pack(pady=(20, 10))
        self.photo_frame.pack_propagate(False)
        self.photo_label = ctk.CTkLabel(
            self.photo_frame,
            text="No Image Selected",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        )
        self.photo_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(
            parent,
            text="📷 Upload Photo",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            command=self.upload_photo,
            width=200,
            height=40,
            corner_radius=8
        ).pack(pady=10)

        # Fetch students for dropdown
        students = self.db.get_all_students()
        student_names = ["Select Student"] + [student["full_name"] for student in students]
        self.student_combobox = ctk.CTkComboBox(
            parent,
            values=student_names,
            font=self.theme["font_normal"],
            width=200,
            fg_color=get_color(self.theme["background"]),
            text_color=get_color(self.theme["secondary"]),
            button_color=get_color(self.theme["primary"]),
            button_hover_color=get_color(self.theme["button_hover"]),
            dropdown_fg_color=get_color(self.theme["background"]),
            dropdown_text_color=get_color(self.theme["secondary"]),
            command=self.on_student_select
        )
        self.student_combobox.pack(pady=5)
        self.student_combobox.set("Select Student")

    def on_student_select(self, choice):
        if choice == "Select Student":
            self.clear_fields()
            return

        students = self.db.get_all_students()
        selected_student = next((student for student in students if student["full_name"] == choice), None)
        if selected_student:
            self.var_ID.set(str(selected_student["student_id"]))
            self.var_full_name.set(selected_student["full_name"])
            self.var_number.set(selected_student["number"])
            self.var_email.set(selected_student["email"])
            self.var_enrollment_date.set(selected_student["enrollment_date"])
            self.current_photo_path = selected_student["photo"]
            self.display_photo(selected_student["photo"])

    def display_photo(self, photo_path):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        try:
            if photo_path:
                image = Image.open(photo_path)
                image = image.resize((200, 200))
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 200))
                self.photo_label.configure(image=ctk_image, text="")
                self.photo_label.image = ctk_image
            else:
                self.photo_label.configure(image=None, text="No Image Selected")
        except Exception as e:
            print(f"Error displaying photo: {e}")
            self.photo_label.configure(image=None, text="Invalid Image", text_color=get_color(self.theme["danger"]))

    def create_action_buttons(self, parent):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ctk.CTkButton(
            buttons_frame,
            text="➕ Add Student",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["success"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            command=self.add_student,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="🔄 Update",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["warning"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            command=self.update_student,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="🗑️ Remove",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["danger"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            command=self.remove_student,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="🧹 Clear",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["sidebar"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            command=self.clear_fields,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5)

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            try:
                id_student = self.var_ID.get() or "temp"
                os.makedirs("photo/students", exist_ok=True)
                filename = f"{id_student}_{os.path.basename(file_path)}"
                target_path = os.path.join("photo/students", filename)
                shutil.copy(file_path, target_path)
                image = Image.open(target_path)
                image = image.resize((200, 200))
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 200))
                self.photo_label.configure(image=ctk_image, text="")
                self.photo_label.image = ctk_image
                self.current_photo_path = target_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload photo: {str(e)}")

    def add_student(self):
        if not self.validate_fields():
            return
        student_data = {
            "full_name": self.var_full_name.get(),
            "number": self.var_number.get(),
            "email": self.var_email.get(),
            "enrollment_date": self.var_enrollment_date.get(),
            "photo": self.current_photo_path
        }
        try:
            student_id = self.db.add_student(**student_data)
            if student_id:
                messagebox.showinfo("Success", f"Student added successfully! ID: {student_id}")
                self.var_ID.set(str(student_id))
                self.clear_fields()
            else:
                messagebox.showerror("Error", "Failed to add student")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def update_student(self):
        if not self.validate_fields(update=True):
            return
        try:
            success = self.db.update_student(
                self.var_ID.get(),
                full_name=self.var_full_name.get(),
                number=self.var_number.get(),
                email=self.var_email.get(),
                enrollment_date=self.var_enrollment_date.get(),
                photo=self.current_photo_path
            )
            if success:
                messagebox.showinfo("Success", "Student updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update student")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def remove_student(self):
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            return
        student_id = self.var_ID.get()
        try:
            success = self.db.remove_student(student_id)
            if success:
                messagebox.showinfo("Success", "Student removed successfully!")
                self.clear_fields()
            else:
                messagebox.showerror("Error", "Failed to remove student")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear_fields(self):
        self.var_full_name.set("")
        self.var_number.set("")
        self.var_email.set("")
        self.var_enrollment_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.var_search_id.set("")
        self.var_ID.set("")
        self.current_photo_path = None
        self.photo_label.configure(image=None, text="No Image Selected")
        self.student_combobox.set("Select Student")

    def validate_fields(self, update=False):
        errors = []
        if not self.var_full_name.get():
            errors.append("Full Name is required")
        if update and not self.var_ID.get():
            errors.append("Please search for a student first to update")
        if errors:
            messagebox.showwarning("Validation Error", "\n".join(errors))
            return False
=======
import os
import cv2
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import shutil
from database import StudentDB


class StudentInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="#f5f7fa")
        self.parent = parent
        self.db = StudentDB(db_connection)
        self.current_photo_path = None

        # UI Configuration
        self.font_title = ("Arial", 24, "bold")
        self.font_subtitle = ("Arial", 14)
        self.font_normal = ("Arial", 12)
        self.primary_color = "#3498db"
        self.secondary_color = "#2c3e50"
        self.success_color = "#2ecc71"
        self.warning_color = "#f39c12"
        self.danger_color = "#e74c3c"

        # Create variables
        self.var_ID = ctk.StringVar()
        self.var_nom = ctk.StringVar()
        self.var_classe = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_telephone = ctk.StringVar()
        self.var_enseignant = ctk.StringVar()

        self.create_ui()

    def create_ui(self):
        """Creates the student management UI"""
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_container,
            text="👨‍🎓 Student Management System",
            font=self.font_title,
            text_color=self.secondary_color
        ).pack(pady=(0, 20))

        # Content frame
        content_frame = ctk.CTkFrame(main_container, corner_radius=15)
        content_frame.pack(fill="both", expand=True)

        # Form section
        form_frame = ctk.CTkFrame(content_frame, width=400, corner_radius=10)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Photo section
        photo_frame = ctk.CTkFrame(content_frame, width=300, corner_radius=10)
        photo_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Configure grid weights
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Form fields
        self.create_form_fields(form_frame)
        self.create_photo_section(photo_frame)
        self.create_action_buttons(form_frame)

    def create_form_fields(self, parent):
        """Creates the form input fields"""
        fields = [
            ("Student ID:", "var_ID", True),
            ("Full Name:", "var_nom", True),
            ("Class:", "var_classe", False),
            ("Email:", "var_email", False),
            ("Phone:", "var_telephone", False),
            ("Teacher:", "var_enseignant", False)
        ]

        for idx, (label_text, var_name, required) in enumerate(fields):
            label = ctk.CTkLabel(
                parent,
                text=label_text,
                font=self.font_normal,
                text_color=self.secondary_color
            )
            label.grid(row=idx, column=0, sticky="w", padx=10, pady=5)

            entry = ctk.CTkEntry(
                parent,
                textvariable=getattr(self, var_name),
                font=self.font_normal,
                width=250,
                border_color=self.primary_color,
                corner_radius=8
            )
            entry.grid(row=idx, column=1, padx=10, pady=5)

            if required:
                ctk.CTkLabel(
                    parent,
                    text="*",
                    text_color=self.danger_color,
                    font=("Arial", 14, "bold")
                ).grid(row=idx, column=2, sticky="w", padx=(0, 10))

    def create_photo_section(self, parent):
        """Creates the photo upload section"""
        self.photo_frame = ctk.CTkFrame(
            parent,
            width=200,
            height=200,
            corner_radius=10,
            fg_color="#ecf0f1"
        )
        self.photo_frame.pack(pady=(20, 10))
        self.photo_frame.pack_propagate(False)

        self.photo_label = ctk.CTkLabel(
            self.photo_frame,
            text="No Image Selected",
            font=self.font_normal,
            text_color="#7f8c8d"
        )
        self.photo_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(
            parent,
            text="📷 Upload Photo",
            font=self.font_normal,
            fg_color=self.primary_color,
            hover_color="#2980b9",
            command=self.upload_photo,
            width=200,
            height=40,
            corner_radius=8
        ).pack(pady=10)

        ctk.CTkButton(
            parent,
            text="🔍 Search Student",
            font=self.font_normal,
            fg_color=self.secondary_color,
            hover_color="#34495e",
            command=self.search_student,
            width=200,
            height=40,
            corner_radius=8
        ).pack(pady=10)

    def create_action_buttons(self, parent):
        """Creates the action buttons"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=20)

        ctk.CTkButton(
            buttons_frame,
            text="➕ Add Student",
            font=self.font_normal,
            fg_color=self.success_color,
            hover_color="#27ae60",
            command=self.add_student,
            width=120,
            height=40
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="🔄 Update",
            font=self.font_normal,
            fg_color=self.warning_color,
            hover_color="#e67e22",
            command=self.update_student,
            width=120,
            height=40
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="🗑️ Remove",
            font=self.font_normal,
            fg_color=self.danger_color,
            hover_color="#c0392b",
            command=self.remove_student,
            width=120,
            height=40
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="🧹 Clear",
            font=self.font_normal,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=self.clear_fields,
            width=120,
            height=40
        ).pack(side="left", padx=5)

    def upload_photo(self):
        """Handles student photo upload"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            student_id = self.var_ID.get()
            if not student_id:
                messagebox.showwarning("Warning", "Please enter Student ID first!")
                return

            try:
                os.makedirs(f"dataset/{student_id}", exist_ok=True)
                target_path = f"dataset/{student_id}/{os.path.basename(file_path)}"
                shutil.copy(file_path, target_path)

                image = Image.open(target_path)
                image = image.resize((200, 200))
                ctk_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(200, 200)
                )
                self.photo_label.configure(image=ctk_image, text="")
                self.photo_label.image = ctk_image
                self.current_photo_path = target_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload photo: {str(e)}")

    def add_student(self):
        """Adds a new student to the database"""
        if not self.validate_fields():
            return

        student_data = {
            "student_id": self.var_ID.get(),
            "name": self.var_nom.get(),
            "student_class": self.var_classe.get(),
            "email": self.var_email.get(),
            "phone": self.var_telephone.get(),
            "teacher": self.var_enseignant.get(),
            "photo": self.current_photo_path
        }

        try:
            success = self.db.add_student(**student_data)
            if success:
                messagebox.showinfo("Success", "Student added successfully!")
                self.clear_fields()
            else:
                messagebox.showerror("Error", "Failed to add student")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def update_student(self):
        """Updates an existing student"""
        if not self.validate_fields():
            return

        try:
            success = self.db.update_student(
                name=self.var_nom.get(),
                student_class=self.var_classe.get(),
                email=self.var_email.get(),
                phone=self.var_telephone.get(),
                teacher=self.var_enseignant.get(),
                photo=self.current_photo_path,
                student_id=self.var_ID.get()
            )
            if success:
                messagebox.showinfo("Success", "Student updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update student")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def remove_student(self):
        """Removes a student from the database"""
        student_id = self.var_ID.get()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter a Student ID!")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete student {student_id}?"):
            try:
                success = self.db.remove_student(student_id)
                if success:
                    if os.path.exists(f"dataset/{student_id}"):
                        shutil.rmtree(f"dataset/{student_id}")
                    messagebox.showinfo("Success", "Student removed successfully!")
                    self.clear_fields()
                else:
                    messagebox.showerror("Error", "Failed to remove student")
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def search_student(self):
        """Searches for a student by ID"""
        student_id = self.var_ID.get()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter a Student ID!")
            return

        try:
            student = self.db.get_student_by_id(student_id)
            if student:
                self.var_nom.set(student['name'])
                self.var_classe.set(student['class'])
                self.var_email.set(student['email'])
                self.var_telephone.set(student['phone'])
                self.var_enseignant.set(student['teacher'])

                if student['photo'] and os.path.exists(student['photo']):
                    image = Image.open(student['photo'])
                    image = image.resize((200, 200))
                    ctk_image = ctk.CTkImage(
                        light_image=image,
                        dark_image=image,
                        size=(200, 200)
                    )
                    self.photo_label.configure(image=ctk_image, text="")
                    self.photo_label.image = ctk_image
                    self.current_photo_path = student['photo']

                messagebox.showinfo("Found", f"Student {student_id} found!")
            else:
                messagebox.showinfo("Not Found", f"Student {student_id} not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear_fields(self):
        """Clears all form fields and resets photo"""
        for var in [
            self.var_ID,
            self.var_nom,
            self.var_classe,
            self.var_email,
            self.var_telephone,
            self.var_enseignant
        ]:
            var.set("")

        self.current_photo_path = None
        self.photo_label.configure(text="No Image Selected", image=None)

    def validate_fields(self):
        """Validates required fields"""
        if not self.var_ID.get():
            messagebox.showwarning("Validation Error", "Student ID is required!")
            return False
        if not self.var_nom.get():
            messagebox.showwarning("Validation Error", "Full Name is required!")
            return False
>>>>>>> 263f666345c0bcb90842933d4acc0f0751c416f0
        return True