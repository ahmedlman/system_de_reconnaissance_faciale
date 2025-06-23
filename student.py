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
        return True