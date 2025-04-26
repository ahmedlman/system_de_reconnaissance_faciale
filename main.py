from home import HomePage
from student import StudentInformation
from face_recognition import FaceRecognition
from settings import SettingsPage
from capture_faces import CaptureFaces
from teacher import TeacherInformation
from database import AuthDB
import customtkinter as ctk
from datetime import datetime
from login import LoginPage
from sign_up import SignUpPage
from database import DatabaseConnection
from classe import ClassInformation


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("School Management System")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Custom colors
        self.sidebar_color = "#2c3e50"
        self.sidebar_button_color = "#34495e"
        self.sidebar_button_hover = "#3d566e"
        self.main_bg = "#f5f7fa"
        self.accent_color = "#3498db"

        # Initial page load
        self.current_frame = None

        # Setup database and authentication
        self.db_connection = DatabaseConnection()
        self.db_connection.connect()
        self.auth_db = AuthDB(self.db_connection)

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

    def show_sign_up_page(self):
        self.clear_current_frame()
        self.sign_up_page = SignUpPage(
            self,
            self.on_signup_success,
            self.show_login_page,
        )
        self.sign_up_page.pack(fill="both", expand=True)
        self.current_frame = self.sign_up_page

    def on_login_success(self):
        self.clear_current_frame()
        self.create_main_ui()

    def on_signup_success(self):
        self.show_login_page()

    def create_main_ui(self):
        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create UI elements
        self.create_sidebar()
        self.create_main_content()
        self.create_date_label()

        # Initial page load
        self.load_home()
        self.update_date_label()

    def clear_current_frame(self):
        if hasattr(self, 'current_frame') and self.current_frame:
            self.current_frame.destroy()

    def create_sidebar(self):
        """Create static sidebar without animations"""
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=self.sidebar_color,
            width=250,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Sidebar content
        self.create_profile_section()
        self.create_navigation_buttons()

    def create_profile_section(self):
        """Create profile section"""
        self.profile_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.sidebar_button_color,
            height=120,
            corner_radius=8
        )
        self.profile_frame.pack(fill="x", pady=(15, 15), padx=10)

        # Profile picture
        self.profile_pic = ctk.CTkLabel(
            self.profile_frame,
            text="👤",
            font=("Arial", 28),
            text_color="white"
        )
        self.profile_pic.pack(pady=(10, 5))

        # Profile text
        self.name_label = ctk.CTkLabel(
            self.profile_frame,
            text="Admin User",
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        self.role_label = ctk.CTkLabel(
            self.profile_frame,
            text="Administrator",
            font=("Arial", 12),
            text_color="lightgray"
        )
        self.name_label.pack()
        self.role_label.pack()

    def create_navigation_buttons(self):
        """Create navigation buttons"""
        buttons = [
            ("🏠", "Home", self.load_home),
            ("📷", "Face Recognition", self.load_face_recognition),
            ("👨‍🎓", "Student information", self.load_student),
            ("👨‍🏫", "Teacher information", self.load_teacher),
            ("👨‍🏫", "Classe information", self.load_class),
            ("🤖", "Capture Faces", self.load_capture),
            ("⚙️", "Settings", self.load_setting),
            ("🚪", "Logout", self.show_login_page)
        ]

        for icon, text, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"   {icon}  {text}",
                font=("Arial", 14),
                fg_color=self.sidebar_button_color,
                hover_color=self.sidebar_button_hover,
                text_color="white",
                corner_radius=5,
                command=command,
                anchor="w",
                height=40
            )
            btn.pack(fill="x", padx=10, pady=5)

    def create_main_content(self):
        """Create main content area"""
        self.content = ctk.CTkFrame(
            self,
            fg_color=self.main_bg
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    def create_date_label(self):
        """Create date label"""
        self.date_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#7f8c8d"
        )
        self.date_label.place(relx=0.99, rely=0.02, anchor="ne")

    def update_date_label(self):
        """Update date label with existence check"""
        if hasattr(self, 'date_label') and self.date_label.winfo_exists():
            self.date_label.configure(text=datetime.now().strftime("%A, %B %d %Y | %I:%M:%S %p"))
        self.after(1000, self.update_date_label)

    def load_home(self):
        """Load home page"""
        self.clear_content()
        page = HomePage(self.content)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_face_recognition(self):
        """Load face recognition page"""
        self.clear_content()
        FaceRecognition(self.content)

    def load_student(self):
        """Load student management page"""
        self.clear_content()
        page = StudentInformation(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_teacher(self):
        """Load teacher management page"""
        self.clear_content()
        page = TeacherInformation(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_class(self):
        self.clear_content()
        page = ClassInformation(self.content, self.db_connection)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_setting(self):
        """Load settings page"""
        self.clear_content()
        page = SettingsPage(self.content)
        page.pack(expand=True, fill="both", padx=10, pady=10)

    def load_capture(self):
        """Load face detection page"""
        self.clear_content()
        # Create container frame first
        container = ctk.CTkFrame(self.content)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Now create CaptureFaces inside container
        page = CaptureFaces(container, self.db_connection)
        page.pack(fill="both", expand=True)

    def clear_content(self):
        """Clear content area safely"""
        if hasattr(self, 'content'):
            for widget in self.content.winfo_children():
                widget.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()