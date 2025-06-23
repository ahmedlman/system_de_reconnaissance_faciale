import PIL
import customtkinter as ctk
from datetime import datetime
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from home import HomePage
from student import StudentInformation
from face_recog import FaceRecognition
from settings import SettingsPage
from capture_faces import CaptureFaces
from teacher import TeacherInformation
from database import *
from login import LoginPage
from sign_up import SignUpPage
from classe import ClassInformation
from seance import SeanceInformation
from config import Theme

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Apply the theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()
        # Window configuration
        self.title("School Attendance System")
        self.geometry("1200x700")
        self.iconbitmap("assets/logo_soc.ico")

        # Initial page load
        self.current_frame = None

        # Setup database and authentication
        self.db_connection = DatabaseConnection()
        self.db_connection.connect()
        self.auth_db = AuthDB(self.db_connection)
        self.admin_db = AdminDB(self.db_connection)

        # Store logged-in user details
        self._logged_in_user = None

        # Show login page
        self.show_login_page()

    def show_login_page(self):
        self.clear_current_frame()
        self.login_page = LoginPage(
            self,
            self.on_login_success,
            self.show_sign_up_page,
        )
        self.login_page.pack(fill="both", expand=True)
        self.current_frame = self.login_page

    def show_login_out_page(self):
        self.clear_current_frame()
        self.show_login_page()  # Redirect to login page instead of destroying the app

    def show_sign_up_page(self):
        self.clear_current_frame()
        self.sign_up_page = SignUpPage(
            self,
            self.on_signup_success,
            self.show_login_page,
        )
        self.sign_up_page.pack(fill="both", expand=True)
        self.current_frame = self.sign_up_page

    def on_login_success(self, username, password):
        user = self.auth_db.validate_user(username, password)
        if user:
            self.logged_in_user = user
            self.clear_current_frame()
            self.create_main_ui()
        else:
            print("Login failed: Invalid credentials")

    def on_signup_success(self):
        self.show_login_page()

    def create_main_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.create_sidebar()
        self.create_main_content()
        self.create_date_label()
        self.load_home()
        self.update_date_label()

    def clear_current_frame(self):
        if hasattr(self, 'current_frame') and self.current_frame:
            self.current_frame.destroy()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=self.theme["sidebar"],
            width=250,
            corner_radius=6  # Match lavender.json
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_propagate(False)
        self.create_profile_section()
        self.create_navigation_buttons()

    def create_profile_section(self):
        self.profile_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.theme["primary"],
            corner_radius=6
        )
        self.profile_frame.pack(fill="x", pady=(15, 15), padx=10)
        self.profile_pic = ctk.CTkLabel(
            self.profile_frame,
            text="👤",
            font=self.theme["font_large"],
            text_color=self.theme["secondary"]
        )
        self.profile_pic.pack(pady=(10, 5))
        user_name = self.logged_in_user.get('name', 'Unknown User') if self.logged_in_user else 'Unknown User'
        user_role = self.logged_in_user.get('role', 'Unknown Role') if self.logged_in_user else 'Unknown Role'
        self.name_label = ctk.CTkLabel(
            self.profile_frame,
            text=user_name,
            font=self.theme["font_title"],
            text_color=self.theme["secondary"]
        )
        self.role_label = ctk.CTkLabel(
            self.profile_frame,
            text=user_role,
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        )
        self.name_label.pack()
        self.role_label.pack()

    def create_navigation_buttons(self):
        buttons = [
            ("🏠", "Home", self.load_home),
            ("📷", "Face Recognition", self.load_face_recognition),
            ("👨‍🎓", "Student information", self.load_student),
            ("👨‍🏫", "Teacher information", self.load_teacher),
            ("📅", "Seance information", self.load_seance),
            ("👨‍🏫", "Classe information", self.load_class),
            ("🤖", "Capture Faces", self.load_capture),
            ("⚙️", "Settings", self.load_setting),
            ("🚪", "Logout", self.show_login_out_page),
        ]
        for icon, text, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"   {icon}  {text}",
                font=self.theme["font_title"],
                fg_color=self.theme["primary"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["secondary"],
                corner_radius=6,
                command=command,
                anchor="w",
                height=40
            )
            btn.pack(fill="x", padx=10, pady=5)

    def create_main_content(self):
        self.content = ctk.CTkFrame(
            self,
            fg_color=self.theme["background"],
            corner_radius=6
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def create_date_label(self):
        self.date_label = ctk.CTkLabel(
            self,
            text="",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        )
        self.date_label.place(relx=0.99, rely=0.02, anchor="ne")

    def update_date_label(self):
        if hasattr(self, 'date_label') and self.date_label.winfo_exists():
            self.date_label.configure(text=datetime.now().strftime("%A, %B %d %Y | %I:%M:%S %p"))
        self.after(1000, self.update_date_label)

    def load_home(self):
        self.clear_content()
        page = HomePage(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_face_recognition(self):
        self.clear_content()
        page = FaceRecognition(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_student(self):
        self.clear_content()
        page = StudentInformation(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_teacher(self):
        self.clear_content()
        page = TeacherInformation(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_class(self):
        self.clear_content()
        page = ClassInformation(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_seance(self):
        self.clear_content()
        page = SeanceInformation(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_setting(self):
        self.clear_content()
        page = SettingsPage(self.content, self.logged_in_user, self.show_login_out_page)
        page.pack(fill="both", expand=True)

    def load_capture(self):
        self.clear_content()
        page = CaptureFaces(self.content, self.db_connection)
        page.pack(fill="both", expand=True)

    def clear_content(self):
        if hasattr(self, 'content'):
            for widget in self.content.winfo_children():
                widget.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()