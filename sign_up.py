import customtkinter as ctk
from PIL import Image
import os
from database import AuthDB, DatabaseConnection


class SignUpPage(ctk.CTkFrame):
    def __init__(self, parent, on_signup_success, on_back_to_login):
        super().__init__(parent, fg_color="#f5f7fa")
        self.on_signup_success = on_signup_success
        self.on_back_to_login = on_back_to_login

        # Create DB connection and auth instance
        self.db_connection = DatabaseConnection()
        self.db_connection.connect()
        self.auth_db = AuthDB(self.db_connection)

        # Configure grid layout (2 columns - form and image)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container for the form
        self.form_container = ctk.CTkFrame(self, fg_color="transparent")
        self.form_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Sign up form frame
        self.signup_frame = ctk.CTkFrame(
            self.form_container,
            width=450,
            height=650,
            corner_radius=15,
            fg_color="white"
        )
        self.signup_frame.grid(row=0, column=0, sticky="")
        self.signup_frame.grid_propagate(False)

        # Configure form frame grid to have 2 columns
        self.signup_frame.grid_columnconfigure(0, weight=1)
        self.signup_frame.grid_columnconfigure(1, weight=1)

        # Back button
        self.back_button = ctk.CTkButton(
            self.signup_frame,
            text="←",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#e0e0e0",
            hover_color="#d0d0d0",
            text_color="#2c3e50",
            font=("Arial", 14),
            command=self.on_back_to_login
        )
        self.back_button.grid(row=0, column=0, pady=(20, 0), padx=20, sticky="nw", columnspan=2)

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "detect.jpeg")
        try:
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(100, 100)
            )
            self.logo_label = ctk.CTkLabel(
                self.signup_frame,
                image=self.logo_image,
                text=""
            )
        except:
            self.logo_label = ctk.CTkLabel(
                self.signup_frame,
                text="🏫",
                font=("Arial", 50)
            )
        self.logo_label.grid(row=1, column=0, pady=(10, 10), padx=20, columnspan=2)

        # Title
        self.title_label = ctk.CTkLabel(
            self.signup_frame,
            text="Create an Account",
            font=("Arial", 20, "bold"),
            text_color="#2c3e50"
        )
        self.title_label.grid(row=2, column=0, pady=(0, 20), padx=20, columnspan=2)

        # Form fields organized in two columns to match database structure
        left_fields = [
            ("Full Name", "text", "John Doe"),  # matches full_name in database
            ("Username", "text", "username"),  # matches username in database
            ("Password", "password", "")  # matches password in database
        ]

        right_fields = [
            ("Email", "email", "example@school.com"),  # matches email in database
            ("Confirm Password", "password", ""),
            ("Role", "combobox", ["Administrator", "Teacher", "Super Administrator"])  # matches role in database
        ]

        self.entries = {}

        # Left column fields
        for i, (label, field_type, placeholder) in enumerate(left_fields):
            # Label
            lbl = ctk.CTkLabel(
                self.signup_frame,
                text=label,
                font=("Arial", 12),
                text_color="#34495e",
                anchor="w"
            )
            lbl.grid(row=3 + i * 2, column=0, pady=(10, 0), padx=(40, 10), sticky="ew")

            # Field
            if field_type in ["text", "email", "password"]:
                entry = ctk.CTkEntry(
                    self.signup_frame,
                    placeholder_text=placeholder,
                    height=40,
                    font=("Arial", 13),
                    corner_radius=8,
                    border_color="#bdc3c7",
                    fg_color="#f8f9fa"
                )
                if field_type == "password":
                    entry.configure(show="•")
                entry.grid(row=4 + i * 2, column=0, pady=(0, 5), padx=(40, 10), sticky="ew")
                self.entries[label.lower().replace(" ", "_")] = entry

        # Right column fields
        for i, (label, field_type, placeholder) in enumerate(right_fields):
            # Label
            lbl = ctk.CTkLabel(
                self.signup_frame,
                text=label,
                font=("Arial", 12),
                text_color="#34495e",
                anchor="w"
            )
            lbl.grid(row=3 + i * 2, column=1, pady=(10, 0), padx=(10, 40), sticky="ew")

            # Field
            if field_type in ["text", "email", "password"]:
                entry = ctk.CTkEntry(
                    self.signup_frame,
                    placeholder_text=placeholder,
                    height=40,
                    font=("Arial", 13),
                    corner_radius=8,
                    border_color="#bdc3c7",
                    fg_color="#f8f9fa"
                )
                if field_type == "password":
                    entry.configure(show="•")
                entry.grid(row=4 + i * 2, column=1, pady=(0, 5), padx=(10, 40), sticky="ew")
                self.entries[label.lower().replace(" ", "_")] = entry
            elif field_type == "combobox":
                combo = ctk.CTkComboBox(
                    self.signup_frame,
                    values=placeholder,
                    height=40,
                    font=("Arial", 13),
                    corner_radius=8,
                    border_color="#bdc3c7",
                    fg_color="#f8f9fa",
                    button_color="#3498db",
                    dropdown_fg_color="white",
                    dropdown_hover_color="#f0f0f0"
                )
                combo.grid(row=4 + i * 2, column=1, pady=(0, 5), padx=(10, 40), sticky="ew")
                self.entries["role"] = combo

        # Terms checkbox (span both columns)
        self.terms_var = ctk.StringVar(value="off")
        self.terms_check = ctk.CTkCheckBox(
            self.signup_frame,
            text="I agree to the Terms and Conditions",
            variable=self.terms_var,
            onvalue="on",
            offvalue="off",
            font=("Arial", 12),
            text_color="#7f8c8d",
            checkbox_width=18,
            checkbox_height=18
        )
        self.terms_check.grid(row=9, column=0, pady=(10, 0), padx=35, sticky="w", columnspan=2)

        # Sign up button (span both columns)
        self.signup_button = ctk.CTkButton(
            self.signup_frame,
            text="Sign Up",
            height=45,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.attempt_signup
        )
        self.signup_button.grid(row=10, column=0, pady=(20, 15), padx=40, sticky="ew", columnspan=2)

        # Already have account (span both columns)
        self.login_prompt = ctk.CTkLabel(
            self.signup_frame,
            text="Already have an account? Login",
            font=("Arial", 12),
            text_color="#7f8c8d",
            cursor="hand2"
        )
        self.login_prompt.grid(row=11, column=0, pady=(0, 30), columnspan=2)
        self.login_prompt.bind("<Button-1>", lambda e: self.on_back_to_login())

        # Error message label (hidden by default, span both columns)
        self.error_label = ctk.CTkLabel(
            self.signup_frame,
            text="",
            text_color="#e74c3c",
            font=("Arial", 12)
        )
        self.error_label.grid(row=12, column=0, pady=(0, 10), columnspan=2)

        # Center the form in its container
        self.form_container.grid_rowconfigure(0, weight=1)
        self.form_container.grid_columnconfigure(0, weight=1)

    def attempt_signup(self):
        """Validate and process sign up"""
        # Get all values - matching database column names
        full_name = self.entries["full_name"].get()
        username = self.entries["username"].get()
        password = self.entries["password"].get()
        confirm_password = self.entries["confirm_password"].get()
        email = self.entries["email"].get()
        role = self.entries["role"].get()
        terms_accepted = self.terms_var.get() == "on"

        # Validate
        if not all([full_name, username, password, confirm_password, email, role]):
            self.show_error("Please fill in all fields")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match")
            return

        if len(password) < 6:
            self.show_error("Password must be at least 6 characters")
            return

        if not terms_accepted:
            self.show_error("You must accept the terms and conditions")
            return

        # Try to create the user
        try:
            result = self.auth_db.create_user(full_name, username, password, email, role)

            if result == True:
                # User created successfully
                self.show_error("")  # Clear any errors
                self.on_signup_success()  # Proceed with the signup success callback
            elif result == "username_exists":
                self.show_error("Username already exists")
            elif result == "email_exists":
                self.show_error("Email already exists")
            else:
                self.show_error("An error occurred. Please try again later.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def show_error(self, message):
        """Display error message"""
        self.error_label.configure(text=message)
        self.after(3000, lambda: self.error_label.configure(text=""))