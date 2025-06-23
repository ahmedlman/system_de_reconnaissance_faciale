<<<<<<< HEAD
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
from database import AuthDB, DatabaseConnection
from config import Theme

class SignUpPage(ctk.CTkFrame):
    def __init__(self, parent, on_signup_success, on_back_to_login):
        super().__init__(parent)
        self.on_signup_success = on_signup_success
        self.on_back_to_login = on_back_to_login

        # Load theme from config.py
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()

        # Setup database
        self.db_connection = DatabaseConnection()
        self.db_connection.connect()
        self.auth_db = AuthDB(self.db_connection)

        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create UI
        self.create_main_container()
        self.create_signup_form()

        # Apply theme to all widgets
        self.apply_theme()

    def create_main_container(self):
        """Create the main container with gradient background"""
        # Main container frame
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Background canvas for gradient
        self.bg_canvas = ctk.CTkCanvas(self.main_frame, highlightthickness=0)
        self.bg_canvas.grid(row=0, column=0, sticky="nsew")
        self.create_gradient()

        # Form container
        self.form_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            border_width=1
        )
        self.form_container.grid(row=0, column=0, sticky="nsew")
        self.form_container.grid_propagate(False)
        self.form_container.grid_rowconfigure(0, weight=1)
        self.form_container.grid_columnconfigure(0, weight=1)

    def create_signup_form(self):
        """Create the signup form with animated GIF and two-column layout"""
        # Main content frame
        content_frame = ctk.CTkFrame(
            self.form_container,
            fg_color="transparent"
        )
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Animation frame (left side)
        self.animation_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent",
            width=350,
            height=350
        )
        self.animation_frame.grid(row=0, column=0, padx=200, pady=60, sticky="nsw")
        self.animation_frame.grid_propagate(False)

        # Create canvas for animation
        self.canvas = tk.Canvas(
            self.animation_frame,
            width=350,
            height=350,
            highlightthickness=0
        )
        self.canvas.pack()

        # Load and setup animation
        self.setup_animation(os.path.join("assets", "schools.gif"))

        # Description text
        self.desc_label = ctk.CTkLabel(
            self.animation_frame,
            text="School Management\nSecure Platform",
            font=("Arial", 14, "bold"),
            justify="center"
        )
        self.desc_label.pack(pady=(10, 0))

        # Signup form (right side)
        self.form_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=20,
            width=450
        )
        self.form_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nse")
        self.form_frame.grid_propagate(False)
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Back button
        self.back_button = ctk.CTkButton(
            self.form_frame,
            text="←",
            width=30,
            height=30,
            corner_radius=15,
            font=("Arial", 14, "bold"),
            command=self.handle_back_to_login
        )
        self.back_button.grid(row=0, column=0, pady=(10, 0), padx=20, sticky="nw", columnspan=2)

        # Logo
        logo_path = os.path.join("assets", "detect.jpeg")
        try:
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(80, 80)
            )
            self.logo_label = ctk.CTkLabel(
                self.form_frame,
                image=self.logo_image,
                text=""
            )
        except:
            self.logo_label = ctk.CTkLabel(
                self.form_frame,
                text="🏫",
                font=self.theme["font_large"]
            )
        self.logo_label.grid(row=1, column=0, pady=(5, 5), padx=20, columnspan=2)

        # Title
        self.title_label = ctk.CTkLabel(
            self.form_frame,
            text="Create an Account",
            font=("Arial", 14, "bold")
        )
        self.title_label.grid(row=2, column=0, pady=(0, 15), padx=20, columnspan=2)

        # Form fields organized in two columns
        left_fields = [
            ("Full Name", "text", "John Doe"),
            ("Username", "text", "username"),
            ("Password", "password", "")
        ]
        right_fields = [
            ("Email", "email", "example@school.com"),
            ("Confirm Password", "password", ""),
            ("Role", "combobox", ["ADMIN", "TEACHER"])
        ]

        self.entries = {}

        # Left column fields
        for i, (label, field_type, placeholder) in enumerate(left_fields):
            # Label above the field
            lbl = ctk.CTkLabel(
                self.form_frame,
                text=label,
                font=("Arial", 14, "bold"),
                anchor="w"
            )
            lbl.grid(row=3 + i*2, column=0, pady=(5, 0), padx=(30, 10), sticky="w")

            # Input field below the label
            if field_type in ["text", "email", "password"]:
                entry = ctk.CTkEntry(
                    self.form_frame,
                    placeholder_text=placeholder,
                    height=35,
                    font=self.theme["font_normal"],
                    corner_radius=8,
                    border_width=2
                )
                if field_type == "password":
                    entry.configure(show="•")
                entry.grid(row=3 + i*2 + 1, column=0, pady=(2, 5), padx=(30, 10), sticky="ew")
                self.entries[label.lower().replace(" ", "_")] = entry

        # Right column fields
        for i, (label, field_type, placeholder) in enumerate(right_fields):
            # Label above the field
            lbl = ctk.CTkLabel(
                self.form_frame,
                text=label,
                font=("Arial", 14, "bold"),
                anchor="w"
            )
            lbl.grid(row=3 + i*2, column=1, pady=(5, 0), padx=(10, 30), sticky="w")

            # Input field below the label
            if field_type in ["text", "email", "password"]:
                entry = ctk.CTkEntry(
                    self.form_frame,
                    placeholder_text=placeholder,
                    height=35,
                    font=self.theme["font_normal"],
                    corner_radius=8,
                    border_width=2
                )
                if field_type == "password":
                    entry.configure(show="•")
                entry.grid(row=3 + i*2 + 1, column=1, pady=(2, 5), padx=(10, 30), sticky="ew")
                self.entries[label.lower().replace(" ", "_")] = entry
            elif field_type == "combobox":
                combo = ctk.CTkComboBox(
                    self.form_frame,
                    values=placeholder,
                    height=35,
                    font=self.theme["font_normal"],
                    corner_radius=8,
                    border_width=2
                )
                combo.grid(row=3 + i*2 + 1, column=1, pady=(2, 5), padx=(10, 30), sticky="ew")
                self.entries["role"] = combo

        # Terms checkbox
        self.terms_var = ctk.StringVar(value="off")
        self.terms_check = ctk.CTkCheckBox(
            self.form_frame,
            text="I agree to the Terms and Conditions",
            variable=self.terms_var,
            onvalue="on",
            offvalue="off",
            font=self.theme["font_normal"],
            checkbox_width=16,
            checkbox_height=16
        )
        self.terms_check.grid(row=9, column=0, pady=(10, 5), padx=30, sticky="w", columnspan=2)

        # Sign up button
        self.signup_button = ctk.CTkButton(
            self.form_frame,
            text="Sign Up",
            height=35,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            command=self.attempt_signup
        )
        self.signup_button.grid(row=10, column=0, pady=(5, 5), padx=30, sticky="ew", columnspan=2)

        # Back to login prompt
        self.login_prompt = ctk.CTkLabel(
            self.form_frame,
            text="Already have an account? Login",
            font=self.theme["font_normal"],
            cursor="hand2"
        )
        self.login_prompt.grid(row=11, column=0, pady=(5, 10), columnspan=2)
        self.login_prompt.bind("<Button-1>", self.handle_back_to_login)

        # Error message label
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=self.theme["font_normal"]
        )
        self.error_label.grid(row=12, column=0, pady=(0, 5), columnspan=2)

        # Bind Enter key to signup
        for entry in self.entries.values():
            if isinstance(entry, ctk.CTkEntry):
                entry.bind("<Return>", lambda e: self.attempt_signup())

    def handle_back_to_login(self, event=None):
        """Handle click on back to login prompt or back button"""
        print("Back to login clicked")
        if callable(self.on_back_to_login):
            self.on_back_to_login()
        else:
            print("Error: on_back_to_login is not callable")

    def setup_animation(self, gif_path):
        """Load and animate GIF"""
        try:
            self.gif = Image.open(gif_path)
            self.frames = []
            for frame in ImageSequence.Iterator(self.gif):
                frame = frame.resize((350, 350))
                self.frames.append(ImageTk.PhotoImage(frame))
            self.frame_count = len(self.frames)
            self.current_frame = 0
            self.animation = None
            self.animate()
        except Exception as e:
            print(f"Error loading animation: {e}")
            # Fallback to static image
            fallback_img = ctk.CTkImage(
                light_image=Image.new("RGB", (350, 350), color=self.theme["primary"][0]),
                size=(350, 350)
            )
            ctk.CTkLabel(self.animation_frame, image=fallback_img, text="").pack()

    def animate(self):
        """Animate the GIF frames"""
        if hasattr(self, 'frames') and self.frames:
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.frames[self.current_frame], anchor="nw")
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.animation = self.after(100, self.animate)

    def apply_theme(self):
        """Apply theme colors and fonts from config.py to all widgets"""
        def get_color(color_setting):
            """Helper to select light or dark color based on appearance mode"""
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        # Apply to main containers
        self.form_container.configure(
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["sidebar"])
        )

        # Apply to animation section
        self.canvas.configure(
            bg=get_color(self.theme["background"])
        )
        self.desc_label.configure(
            text_color=get_color(self.theme["secondary"]),
            font=("Arial", 14, "bold")
        )

        # Apply to form frame
        self.form_frame.configure(
            fg_color=get_color(self.theme["background"])
        )

        # Apply to form elements
        self.title_label.configure(
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_large"]
        )

        for entry in self.entries.values():
            if isinstance(entry, ctk.CTkEntry):
                entry.configure(
                    fg_color=get_color(self.theme["background"]),
                    border_color=get_color(self.theme["primary"]),
                    text_color=get_color(self.theme["secondary"]),
                    font=self.theme["font_normal"]
                )
            elif isinstance(entry, ctk.CTkComboBox):
                entry.configure(
                    fg_color=get_color(self.theme["background"]),
                    border_color=get_color(self.theme["primary"]),
                    text_color=get_color(self.theme["secondary"]),
                    button_color=get_color(self.theme["primary"]),
                    button_hover_color=get_color(self.theme["button_hover"]),
                    font=self.theme["font_normal"]
                )

        self.terms_check.configure(
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            hover_color=get_color(self.theme["button_hover"]),
            font=self.theme["font_normal"]
        )

        self.signup_button.configure(
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=("Arial", 14, "bold")
        )

        self.back_button.configure(
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"]
        )

        self.login_prompt.configure(
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"]
        )

        self.error_label.configure(
            text_color=get_color(self.theme["danger"]),
            font=self.theme["font_normal"]
        )

    def create_gradient(self):
        """Create gradient background that matches the theme"""
        width = self.bg_canvas.winfo_width()
        height = self.bg_canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Use theme colors for gradient
        bg_start = self.theme["background"][0 if ctk.get_appearance_mode() == "Light" else 1]
        bg_end = self.theme["primary"][0 if ctk.get_appearance_mode() == "Light" else 1]

        # Convert hex to RGB
        r1, g1, b1 = tuple(int(bg_start.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(bg_end.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

        gradient = Image.new('RGB', (width, height))
        for y in range(height):
            r = int(r1 + (r2 - r1) * y / height)
            g = int(g1 + (g2 - g1) * y / height)
            b = int(b1 + (b2 - b1) * y / height)
            for x in range(width):
                gradient.putpixel((x, y), (r, g, b))

        self.bg_image = ImageTk.PhotoImage(gradient)
        self.bg_canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

    def on_resize(self, event):
        """Handle window resize"""
        self.create_gradient()

    def attempt_signup(self):
        """Validate and process sign up"""
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
            self.show_error("You must accept the terms")
            return

        # Try to create the user
        try:
            # CORRECTED PARAMETER ORDER
            result = self.auth_db.create_user(
                full_name,  # name
                email,  # email
                username,  # username
                password,  # password
                role  # role
            )

            if result == True:
                self.show_error("")
                self.on_signup_success()
            elif result == "username_exists":
                self.show_error("Username already exists")
            elif result == "email_exists":
                self.show_error("Email already exists")
            else:
                self.show_error("An error occurred. Please try again.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def show_error(self, message):
        """Display error message"""
        self.error_label.configure(text=message)
        self.after(3000, lambda: self.error_label.configure(text=""))

    def destroy(self):
        """Clean up animation when frame is destroyed"""
        if hasattr(self, 'animation') and self.animation:
            self.after_cancel(self.animation)
        super().destroy()
=======
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
>>>>>>> 263f666345c0bcb90842933d4acc0f0751c416f0
