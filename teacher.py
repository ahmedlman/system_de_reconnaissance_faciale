<<<<<<< HEAD
import os
import shutil
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from datetime import datetime
from database import TeacherDB
from config import Theme

class TeacherInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.parent = parent
        self.db_connection = db_connection
        self.db = TeacherDB(self.db_connection)
        self.current_photo_path = None

        # Variables
        self.var_ID = ctk.StringVar()
        self.var_cin = ctk.StringVar()
        self.var_name = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_number = ctk.StringVar()
        self.var_specialization = ctk.StringVar()
        self.var_hire_date = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.var_password = ctk.StringVar()
        self.var_confirm_password = ctk.StringVar()
        self.var_username = ctk.StringVar()

        # Access theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()

        # Create UI
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
            text="👨‍🏫 Teacher Information",
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
        content_frame.grid_columnconfigure(1, weight=0)
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
            ("CIN:", "var_cin", True),
            ("Full Name:", "var_name", True),
            ("Email:", "var_email", False),
            ("Phone Number:", "var_number", False),
            ("Specialization:", "var_specialization", False),
            ("Hire Date:", "var_hire_date", False),
            ("Password:", "var_password", True),
            ("Confirm Password:", "var_confirm_password", True),
            ("Username:", "var_username", False),
        ]

        for idx, (label_text, var_name, required) in enumerate(fields):
            var = getattr(self, var_name)

            label = ctk.CTkLabel(
                parent,
                text=label_text,
                font=self.theme["font_normal"],
                text_color=get_color(self.theme["secondary"])
            )
            label.grid(row=idx, column=0, sticky="w", padx=10, pady=5)

            if var_name == "var_hire_date":
                entry = ctk.CTkEntry(
                    parent,
                    textvariable=var,
                    font=self.theme["font_normal"],
                    width=250,
                    fg_color=get_color(self.theme["background"]),
                    border_color=get_color(self.theme["primary"]),
                    text_color=get_color(self.theme["secondary"]),
                    corner_radius=8,
                    placeholder_text="YYYY-MM-DD"
                )
            elif "password" in var_name.lower():
                entry = ctk.CTkEntry(
                    parent,
                    textvariable=var,
                    font=self.theme["font_normal"],
                    width=250,
                    fg_color=get_color(self.theme["background"]),
                    border_color=get_color(self.theme["primary"]),
                    text_color=get_color(self.theme["secondary"]),
                    corner_radius=8,
                    show="•"
                )
            elif var_name == "var_username":
                entry = ctk.CTkEntry(
                    parent,
                    textvariable=var,
                    font=self.theme["font_normal"],
                    width=250,
                    fg_color=get_color(self.theme["background"]),
                    border_color=get_color(self.theme["primary"]),
                    text_color=get_color(self.theme["secondary"]),
                    corner_radius=8,
                    state="readonly"
                )
            else:
                entry = ctk.CTkEntry(
                    parent,
                    textvariable=var,
                    font=self.theme["font_normal"],
                    width=250,
                    fg_color=get_color(self.theme["background"]),
                    border_color=get_color(self.theme["primary"]),
                    text_color=get_color(self.theme["secondary"]),
                    corner_radius=8
                )

            entry.grid(row=idx, column=1, padx=10, pady=5)

            if required:
                ctk.CTkLabel(
                    parent,
                    text="*",
                    text_color=get_color(self.theme["danger"]),
                    font=("Arial", 14, "bold")
                ).grid(row=idx, column=2, sticky="w", padx=(0, 10))

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

        teachers = self.db.get_all_teachers()
        teacher_names = ["Select Teacher"] + [teacher["name"] for teacher in teachers]
        self.teacher_combobox = ctk.CTkComboBox(
            parent,
            values=teacher_names,
            font=self.theme["font_normal"],
            width=200,
            fg_color=get_color(self.theme["background"]),
            text_color=get_color(self.theme["secondary"]),
            button_color=get_color(self.theme["primary"]),
            button_hover_color=get_color(self.theme["button_hover"]),
            dropdown_fg_color=get_color(self.theme["background"]),
            dropdown_text_color=get_color(self.theme["secondary"]),
            command=self.on_teacher_select
        )
        self.teacher_combobox.pack(pady=5)
        self.teacher_combobox.set("Select Teacher")

    def on_teacher_select(self, choice):
        if choice == "Select Teacher":
            self.clear_fields()
            return

        teachers = self.db.get_all_teachers()
        selected_teacher = next((teacher for teacher in teachers if teacher["name"] == choice), None)
        if selected_teacher:
            self.var_ID.set(str(selected_teacher["user_id"]))
            self.var_cin.set(selected_teacher["cin"] or "")
            self.var_name.set(selected_teacher["name"])
            self.var_email.set(selected_teacher["email"] or "")
            self.var_number.set(str(selected_teacher["number"]) if selected_teacher["number"] else "")
            self.var_specialization.set(selected_teacher["specialization"] or "")
            self.var_hire_date.set(selected_teacher["hire_date"] or datetime.now().strftime("%Y-%m-%d"))
            self.var_password.set("")
            self.var_confirm_password.set("")
            self.var_username.set(
                self.generate_username(
                    selected_teacher["name"],
                    str(selected_teacher["number"]) if selected_teacher["number"] else ""
                )
            )
            self.current_photo_path = selected_teacher["photo"]
            self.display_photo(selected_teacher["photo"])

    def display_photo(self, photo_path):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        try:
            if photo_path:
                image = Image.open(photo_path)
                image = image.resize((200, 200))
                ctk_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(200, 200)
                )
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
        buttons_frame.grid(row=9, column=0, columnspan=3, pady=20)

        buttons = [
            ("➕ Add Teacher", self.theme["success"], self.theme["button_hover"], self.add_teacher),
            ("🔄 Update", self.theme["warning"], self.theme["button_hover"], self.update_teacher),
            ("🗑️ Remove", self.theme["danger"], self.theme["button_hover"], self.remove_teacher),
            ("🧹 Clear", self.theme["sidebar"], self.theme["button_hover"], self.clear_fields)
        ]

        for text, fg_color, hover_color, command in buttons:
            ctk.CTkButton(
                buttons_frame,
                text=text,
                font=self.theme["font_normal"],
                fg_color=get_color(fg_color),
                hover_color=get_color(hover_color),
                text_color=get_color(self.theme["secondary"]),
                command=command,
                width=120,
                height=40,
                corner_radius=8
            ).pack(side="left", padx=1)

    def generate_username(self, name, number):
        name_part = (name[:3] if len(name) >= 3 else name + "x" * (3 - len(name))).lower()
        number_str = str(number) if number is not None else ""
        digits = ''.join(filter(str.isdigit, number_str))
        number_part = digits[:3] if len(digits) >= 3 else digits + "0" * (3 - len(digits))
        return name_part + number_part

    def upload_photo(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            teacher_cin = self.var_cin.get()
            if not teacher_cin:
                messagebox.showwarning("Warning", "Please enter CIN first!")
                return

            try:
                os.makedirs("photo/teachers", exist_ok=True)
                filename = f"{teacher_cin}_{os.path.basename(file_path)}"
                target_path = f"photo/teachers/{filename}"
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

    def add_teacher(self):
        if not self.validate_fields():
            return

        if self.var_password.get() != self.var_confirm_password.get():
            messagebox.showerror("Error", "Passwords do not match!")
            return

        username = self.generate_username(self.var_name.get(), self.var_number.get())
        self.var_username.set(username)

        teacher_data = {
            "cin": self.var_cin.get(),
            "name": self.var_name.get(),
            "email": self.var_email.get(),
            "username": username,
            "password": self.var_password.get(),
            "number": self.var_number.get(),
            "specialization": self.var_specialization.get(),
            "hire_date": self.var_hire_date.get(),
            "photo": self.current_photo_path
        }

        try:
            self.db.add_teacher(**teacher_data)
            messagebox.showinfo("Success", "Teacher added successfully!")
            self.clear_fields()
            self.refresh_combobox()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add teacher: {str(e)}")

    def update_teacher(self):
        if not self.validate_fields():
            return

        teacher_id = self.var_ID.get()
        if not teacher_id:
            messagebox.showwarning("Warning", "Please search for a teacher first!")
            return

        password = self.var_password.get()
        if password:
            if password != self.var_confirm_password.get():
                messagebox.showerror("Error", "Passwords do not match!")
                return
        else:
            password = None

        teacher_data = {
            "user_id": teacher_id,
            "name": self.var_name.get(),
            "email": self.var_email.get(),
            "specialization": self.var_specialization.get(),
            "hire_date": self.var_hire_date.get(),
            "photo": self.current_photo_path
        }

        if password:
            teacher_data["password"] = password

        try:
            success = self.db.update_teacher(**teacher_data)
            if success:
                messagebox.showinfo("Success", "Teacher updated successfully!")
                self.refresh_combobox()
            else:
                messagebox.showerror("Error", "Failed to update teacher")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def remove_teacher(self):
        teacher_id = self.var_ID.get()
        if not teacher_id:
            messagebox.showwarning("Warning", "Please search for a teacher first!")
            return

        try:
            success = self.db.remove_teacher(teacher_id)
            if success:
                messagebox.showinfo("Success", "Teacher removed successfully!")
                self.clear_fields()
                self.refresh_combobox()
            else:
                messagebox.showerror("Error", "Failed to remove teacher")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear_fields(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        self.var_ID.set("")
        self.var_cin.set("")
        self.var_name.set("")
        self.var_email.set("")
        self.var_number.set("")
        self.var_specialization.set("")
        self.var_hire_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.var_password.set("")
        self.var_confirm_password.set("")
        self.var_username.set("")
        self.current_photo_path = None
        self.photo_label.configure(text="No Image Selected", image=None, text_color=get_color(self.theme["secondary"]))
        self.teacher_combobox.set("Select Teacher")

    def refresh_combobox(self):
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        teachers = self.db.get_all_teachers()
        teacher_names = ["Select Teacher"] + [teacher["name"] for teacher in teachers]
        self.teacher_combobox.configure(
            values=teacher_names,
            fg_color=get_color(self.theme["background"]),
            text_color=get_color(self.theme["secondary"]),
            button_color=get_color(self.theme["primary"]),
            button_hover_color=get_color(self.theme["button_hover"]),
            dropdown_fg_color=get_color(self.theme["background"]),
            dropdown_text_color=get_color(self.theme["secondary"])
        )

    def validate_fields(self):
        errors = []
        if not self.var_cin.get():
            errors.append("CIN is required")
        if not self.var_name.get():
            errors.append("Full Name is required")
        if not self.var_password.get() and not self.var_ID.get():
            errors.append("Password is required")
        if self.var_password.get() and len(self.var_password.get()) < 6:
            errors.append("Password must be at least 6 characters")

        hire_date = self.var_hire_date.get()
        if hire_date:
            try:
                datetime.strptime(hire_date, "%Y-%m-%d")
            except ValueError:
                errors.append("Hire Date must be in YYYY-MM-DD format")

        if errors:
            messagebox.showwarning("Validation Error", "\n".join(errors))
            return False
        return True
=======
import os
import shutil
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from database import TeacherDB


class TeacherInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="#f5f7fa")
        self.parent = parent
        self.db_connection = db_connection
        self.db = TeacherDB(self.db_connection)

        # UI Configuration
        self.font_title = ("Arial", 24, "bold")
        self.font_subtitle = ("Arial", 14)
        self.font_normal = ("Arial", 12)
        self.primary_color = "#3498db"
        self.secondary_color = "#2c3e50"
        self.success_color = "#2ecc71"
        self.warning_color = "#f39c12"
        self.danger_color = "#e74c3c"

        # Teacher photo path
        self.current_photo_path = None

        # Variables
        self.var_ID = ctk.StringVar()
        self.var_CIN = ctk.StringVar()
        self.var_nom = ctk.StringVar()
        self.var_classe = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_telephone = ctk.StringVar()

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Creates the teacher management UI"""
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_container,
            text="👨‍🏫 Teacher Management System",
            font=self.font_title,
            text_color=self.secondary_color
        ).pack(pady=(0, 20))

        # Content frame
        content_frame = ctk.CTkFrame(main_container, corner_radius=15)
        content_frame.pack(fill="both", expand=True)

        # Form section
        form_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Photo section
        photo_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        photo_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Configure grid weights
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=0)
        content_frame.grid_rowconfigure(0, weight=1)

        # Form fields
        self.create_form_fields(form_frame)
        self.create_photo_section(photo_frame)
        self.create_action_buttons(form_frame)

    def create_form_fields(self, parent):
        fields = [
            ("Teacher ID:", "var_ID", True),
            ("CIN:", "var_CIN", True),
            ("Full Name:", "var_nom", True),
            ("Class:", "var_classe", False),
            ("Email:", "var_email", False),
            ("Phone:", "var_telephone", False),
        ]

        for idx, (label_text, var_name, required) in enumerate(fields):
            var = getattr(self, var_name)

            label = ctk.CTkLabel(
                parent,
                text=label_text,
                font=self.font_normal,
                text_color=self.secondary_color
            )
            label.grid(row=idx, column=0, sticky="w", padx=10, pady=5)

            entry = ctk.CTkEntry(
                parent,
                textvariable=var,
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

        # Upload button
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

        # Search button
        ctk.CTkButton(
            parent,
            text="🔍 Search Teacher",
            font=self.font_normal,
            fg_color=self.secondary_color,
            hover_color="#34495e",
            command=self.search_teacher,
            width=200,
            height=40,
            corner_radius=8
        ).pack(pady=10)

    def create_action_buttons(self, parent):
        """Creates the action buttons"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=20)

        buttons = [
            ("➕ Add Teacher", self.success_color, "#27ae60", self.add_teacher),
            ("🔄 Update", self.warning_color, "#e67e22", self.update_teacher),
            ("🗑️ Remove", self.danger_color, "#c0392b", self.remove_teacher),
            ("🧹 Clear", "#95a5a6", "#7f8c8d", self.clear_fields)
        ]

        for text, fg_color, hover_color, command in buttons:
            ctk.CTkButton(
                buttons_frame,
                text=text,
                font=self.font_normal,
                fg_color=fg_color,
                hover_color=hover_color,
                command=command,
                width=120,
                height=40
            ).pack(side="left", padx=5)

    def upload_photo(self):
        """Handles teacher photo upload"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            teacher_id = self.var_ID.get()
            if not teacher_id:
                messagebox.showwarning("Warning", "Please enter Teacher ID first!")
                return

            try:
                os.makedirs(f"dataset/teachers/{teacher_id}", exist_ok=True)
                target_path = f"dataset/teachers/{teacher_id}/{os.path.basename(file_path)}"
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

    def add_teacher(self):
        """Adds a new teacher to the database"""
        if not self.validate_fields():
            return

        teacher_data = self.get_teacher_data()
        try:
            success = self.db.add_teacher(**teacher_data)
            if success:
                messagebox.showinfo("Success", "Teacher added successfully!")
                self.clear_fields()
            else:
                messagebox.showerror("Error", "Failed to add teacher")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def update_teacher(self):
        """Updates an existing teacher"""
        if not self.validate_fields():
            return

        teacher_data = self.get_teacher_data()
        try:
            success = self.db.update_teacher(**teacher_data)
            if success:
                messagebox.showinfo("Success", "Teacher updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update teacher")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def remove_teacher(self):
        """Removes a teacher from the database"""
        teacher_id = self.var_ID.get()
        if not teacher_id:
            messagebox.showwarning("Warning", "Please enter a Teacher ID!")
            return

        if messagebox.askyesno("Confirm", f"Delete teacher {teacher_id}?"):
            try:
                success = self.db.remove_teacher(teacher_id)
                if success:
                    messagebox.showinfo("Success", "Teacher removed successfully!")
                    self.clear_fields()
                else:
                    messagebox.showerror("Error", "Failed to remove teacher")
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def search_teacher(self):
        """Searches for a teacher by ID"""
        teacher_id = self.var_ID.get()
        if not teacher_id:
            messagebox.showwarning("Warning", "Please enter a Teacher ID!")
            return

        try:
            teacher = self.db.get_teacher_by_id(teacher_id)
            if teacher:
                self.var_CIN.set(teacher['cin'])
                self.var_nom.set(teacher['name'])
                self.var_classe.set(teacher['classe'])
                self.var_email.set(teacher['email'])
                self.var_telephone.set(teacher['phone'])

                if teacher.get('photo') and os.path.exists(teacher['photo']):
                    image = Image.open(teacher['photo'])
                    image = image.resize((200, 200))
                    ctk_image = ctk.CTkImage(
                        light_image=image,
                        dark_image=image,
                        size=(200, 200)
                    )
                    self.photo_label.configure(image=ctk_image, text="")
                    self.photo_label.image = ctk_image
                    self.current_photo_path = teacher['photo']
                else:
                    self.photo_label.configure(image=None, text="No Image Selected")
                    self.current_photo_path = None

                messagebox.showinfo("Found", f"Teacher {teacher_id} found!")
            else:
                messagebox.showinfo("Not Found", f"Teacher {teacher_id} not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear_fields(self):
        """Clears all form fields and resets photo"""
        for var in [
            self.var_ID,
            self.var_CIN,
            self.var_nom,
            self.var_classe,
            self.var_email,
            self.var_telephone,
        ]:
            var.set("")

        self.current_photo_path = None
        self.photo_label.configure(text="No Image Selected", image=None)

    def validate_fields(self):
        """Validates required fields"""
        if not self.var_ID.get():
            messagebox.showwarning("Validation Error", "Teacher ID is required!")
            return False
        if not self.var_CIN.get():
            messagebox.showwarning("Validation Error", "CIN is required!")
            return False
        if not self.var_nom.get():
            messagebox.showwarning("Validation Error", "Full Name is required!")
            return False
        return True

    def get_teacher_data(self):
        """Returns teacher data as a dictionary"""
        return {
            "teacher_id": self.var_ID.get(),
            "cin": self.var_CIN.get(),
            "name": self.var_nom.get(),
            "classe": self.var_classe.get(),
            "email": self.var_email.get(),
            "phone": self.var_telephone.get(),
            "photo": self.current_photo_path
        }
>>>>>>> 263f666345c0bcb90842933d4acc0f0751c416f0
