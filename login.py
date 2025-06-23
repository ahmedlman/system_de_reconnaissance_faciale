<<<<<<< HEAD
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import customtkinter as ctk
from database import DatabaseConnection, AuthDB
from config import Theme

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success, show_sign_up_page):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.show_sign_up_page = show_sign_up_page

        # Load theme
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
        self.create_login_form()

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

    def create_login_form(self):
        """Create the login form with animated GIF"""
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
        self.setup_animation(os.path.join("assets", "school.gif"))

        # Description text
        self.desc_label = ctk.CTkLabel(
            self.animation_frame,
            text="School Attendance System\nSecure Learning Platform",
            font=self.theme["font_normal"],
            justify="center"
        )
        self.desc_label.pack(pady=(10, 0))

        # Login form (right side)
        self.form_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=20,
            width=400
        )
        self.form_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nse")
        self.form_frame.grid_propagate(False)
        self.form_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.form_frame,
            text="Welcome Back",
            font=self.theme["font_title"]
        )
        self.title_label.grid(row=0, column=0, pady=(30, 20), padx=20)

        # Username entry
        self.username_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Username",
            height=50,
            font=self.theme["font_normal"],
            corner_radius=10,
            border_width=1
        )
        self.username_entry.grid(row=1, column=0, pady=(0, 15), padx=40, sticky="ew")

        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Password",
            height=50,
            font=self.theme["font_normal"],
            corner_radius=10,
            border_width=1,
            show="•"
        )
        self.password_entry.grid(row=2, column=0, pady=(0, 20), padx=40, sticky="ew")

        # Login button
        self.login_button = ctk.CTkButton(
            self.form_frame,
            text="Login",
            height=50,
            font=self.theme["font_normal"],
            corner_radius=10,
            command=self.attempt_login
        )
        self.login_button.grid(row=4, column=0, pady=(0, 20), padx=40, sticky="ew")

        # Divider
        self.divider = ctk.CTkLabel(
            self.form_frame,
            text="───────── or ─────────",
            font=self.theme["font_normal"]
        )
        self.divider.grid(row=5, column=0, pady=(10, 20))

        # Sign up prompt
        self.signup_prompt = ctk.CTkLabel(
            self.form_frame,
            text="Don't have an account? Sign up",
            font=self.theme["font_normal"],
            cursor="hand2"
        )
        self.signup_prompt.grid(row=6, column=0, pady=(0, 30))
        self.signup_prompt.bind("<Button-1>", lambda e: self.show_sign_up_page())

        # Error message label
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=self.theme["font_normal"]
        )
        self.error_label.grid(row=7, column=0, pady=(0, 10))

        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.attempt_login())
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

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
            font=self.theme["font_normal"]
        )

        # Apply to form frame
        self.form_frame.configure(
            fg_color=get_color(self.theme["background"])
        )

        # Apply to form elements
        self.title_label.configure(
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_title"]
        )

        for entry in [self.username_entry, self.password_entry]:
            entry.configure(
                fg_color=get_color(self.theme["background"]),
                border_color=get_color(self.theme["primary"]),
                text_color=get_color(self.theme["secondary"]),
                font=self.theme["font_normal"]
            )

        self.login_button.configure(
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"]
        )

        self.divider.configure(
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"]
        )

        self.signup_prompt.configure(
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

    def attempt_login(self):
        """Validate credentials and log in"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.show_error("Please enter both username and password")
            return

        user = self.auth_db.validate_user(username, password)

        if user:
            self.on_login_success(username, password)
        else:
            self.show_error("Invalid username or password")

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
>>>>>>> 263f666345c0bcb90842933d4acc0f0751c416f0
