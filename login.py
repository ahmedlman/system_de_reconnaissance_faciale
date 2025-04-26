import customtkinter as ctk
from PIL import Image
import os
from database import DatabaseConnection, AuthDB


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success, show_sign_up_page):
        super().__init__(parent, fg_color="#f5f7fa")
        self.on_login_success = on_login_success
        self.show_sign_up_page = show_sign_up_page
        # Create DB connection and auth instance
        self.db_connection = DatabaseConnection()
        self.db_connection.connect()
        self.auth_db = AuthDB(self.db_connection)
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)

        # Login form frame
        self.login_frame = ctk.CTkFrame(
            self.container,
            width=400,
            height=500,
            corner_radius=15,
            fg_color="white"
        )
        self.login_frame.grid(row=0, column=0, sticky="")
        self.login_frame.grid_propagate(False)

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        try:
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(120, 120)
            )
            self.logo_label = ctk.CTkLabel(
                self.login_frame,
                image=self.logo_image,
                text=""
            )
        except:
            self.logo_label = ctk.CTkLabel(
                self.login_frame,
                text="🏫",
                font=("Arial", 60)
            )
        self.logo_label.grid(row=0, column=0, pady=(40, 20), padx=20, sticky="nsew")

        # Title
        self.title_label = ctk.CTkLabel(
            self.login_frame,
            text="School Management System",
            font=("Arial", 20, "bold"),
            text_color="#2c3e50"
        )
        self.title_label.grid(row=1, column=0, pady=(0, 30), padx=20)

        # Username entry
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Username",
            height=45,
            font=("Arial", 14),
            corner_radius=8,
            border_color="#bdc3c7",
            fg_color="#f8f9fa"
        )
        self.username_entry.grid(row=2, column=0, pady=(0, 15), padx=40, sticky="ew")

        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Password",
            height=45,
            font=("Arial", 14),
            corner_radius=8,
            border_color="#bdc3c7",
            fg_color="#f8f9fa",
            show="•"
        )
        self.password_entry.grid(row=3, column=0, pady=(0, 20), padx=40, sticky="ew")

        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            height=45,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.attempt_login
        )
        self.login_button.grid(row=4, column=0, pady=(0, 20), padx=40, sticky="ew")

        # Forgot password
        self.forgot_label = ctk.CTkLabel(
            self.login_frame,
            text="Forgot password?",
            font=("Arial", 12),
            text_color="#7f8c8d",
            cursor="hand2"
        )
        self.forgot_label.grid(row=5, column=0, pady=(0, 30))
        self.forgot_label.bind("<Button-1>", lambda e: print("Forgot password clicked"))

        # Sign up prompt
        self.signup_prompt = ctk.CTkLabel(
            self.login_frame,
            text="Don't have an account? Sign up",
            font=("Arial", 12),
            text_color="#7f8c8d",
            cursor="hand2"
        )
        self.signup_prompt.grid(row=6, column=0, pady=(0, 20))
        self.signup_prompt.bind("<Button-1>", lambda e: self.show_sign_up_page())

        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            self.login_frame,
            text="",
            text_color="#e74c3c",
            font=("Arial", 12)
        )
        self.error_label.grid(row=7, column=0, pady=(0, 10))

        # Center the login frame
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.attempt_login())
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

    def attempt_login(self):
        """Validate credentials and log in"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Simple validation for empty fields
        if not username or not password:
            self.show_error("Please enter both username and password")
            return

        # Validate user using the AuthDB class
        user = self.auth_db.validate_user(username, password)

        if user:
            # Login successful, proceed with the on_login_success callback
            self.on_login_success()
        else:
            # Invalid credentials
            self.show_error("Invalid username or password")

    def show_error(self, message):
        """Display error message"""
        self.error_label.configure(text=message)
        self.after(3000, lambda: self.error_label.configure(text=""))