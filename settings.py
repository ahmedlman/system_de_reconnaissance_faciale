import customtkinter as ctk
from config import Theme
from tkinter import messagebox
from database import DatabaseConnection, AdminDB, TeacherDB
from login import *
import re
from mysql.connector import Error

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, current_user=None, on_logout=None):
        super().__init__(parent)
        self.parent = parent
        self.current_user = current_user  # Store current user info (username, role)
        self.on_logout = on_logout  # Callback to handle logout after deletion

        # Initialize database connections
        self.db_connection = DatabaseConnection()
        if not self.db_connection.connect():
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            return
        self.admin_db = AdminDB(self.db_connection)
        self.teacher_db = TeacherDB(self.db_connection)

        # Access MainApp theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()
        self.setup_ui()

    def setup_ui(self):
        """Initialize all UI components with theme applied"""
        # Configure frame
        self.configure(fg_color="transparent")  # Blend with parent

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=self.theme["font_large"],
            text_color=self.theme["primary"]
        )
        self.title_label.pack(pady=20, padx=20)

        # Theme mode switch
        self.theme_frame = ctk.CTkFrame(self, fg_color=self.theme["frame"])
        self.appearance_label = ctk.CTkLabel(
            self.theme_frame,
            text="Appearance Mode:",
            font=self.theme["font_title"],
            text_color=self.theme["secondary"]
        )
        self.mode_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.light_radio = ctk.CTkRadioButton(
            self.theme_frame,
            text="Light",
            variable=self.mode_var,
            value="Light",
            command=self.change_appearance_mode,
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            text_color=self.theme["secondary"],
            hover_color=self.theme["button_hover"]
        )
        self.dark_radio = ctk.CTkRadioButton(
            self.theme_frame,
            text="Dark",
            variable=self.mode_var,
            value="Dark",
            command=self.change_appearance_mode,
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            text_color=self.theme["secondary"],
            hover_color=self.theme["button_hover"]
        )
        self.system_radio = ctk.CTkRadioButton(
            self.theme_frame,
            text="System",
            variable=self.mode_var,
            value="System",
            command=self.change_appearance_mode,
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            text_color=self.theme["secondary"],
            hover_color=self.theme["button_hover"]
        )

        # Layout theme controls
        self.appearance_label.pack(side="left", padx=5)
        self.light_radio.pack(side="left", padx=5)
        self.dark_radio.pack(side="left", padx=5)
        self.system_radio.pack(side="left", padx=5)
        self.theme_frame.pack(pady=10, padx=20, fill="x")

        # Scaling option
        self.scaling_frame = ctk.CTkFrame(self, fg_color=self.theme["frame"])
        self.scaling_label = ctk.CTkLabel(
            self.scaling_frame,
            text="UI Scaling:",
            font=self.theme["font_title"],
            text_color=self.theme["secondary"]
        )
        self.scaling_var = ctk.StringVar(value="100%")
        scaling_options = ["80%", "90%", "100%", "110%", "120%"]
        self.scaling_option = ctk.CTkOptionMenu(
            self.scaling_frame,
            values=scaling_options,
            command=self.change_scaling,
            variable=self.scaling_var,
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            button_color=self.theme["primary"],
            button_hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            dropdown_fg_color=self.theme["background"],
            dropdown_text_color=self.theme["secondary"]
        )

        # Layout scaling controls
        self.scaling_label.pack(side="left", padx=5)
        self.scaling_option.pack(side="left", padx=5)
        self.scaling_frame.pack(pady=10, padx=20, fill="x")

        # Update account information form
        self.account_frame = ctk.CTkFrame(self, fg_color=self.theme["frame"])
        self.account_label = ctk.CTkLabel(
            self.account_frame,
            text="Update Account Information",
            font=self.theme["font_title"],
            text_color=self.theme["secondary"]
        )
        self.account_label.pack(pady=10)

        # Name entry
        self.name_entry = ctk.CTkEntry(
            self.account_frame,
            placeholder_text="Full Name",
            height=40,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            text_color=self.theme["secondary"],
            border_color=self.theme["primary"],
            corner_radius=10
        )
        self.name_entry.pack(pady=5, padx=20, fill="x")

        # Email entry
        self.email_entry = ctk.CTkEntry(
            self.account_frame,
            placeholder_text="Email",
            height=40,
            font=self.theme["font_normal"],
            fg_color=self.theme["background"],
            text_color=self.theme["secondary"],
            border_color=self.theme["primary"],
            corner_radius=10
        )
        self.email_entry.pack(pady=5, padx=20, fill="x")

        # Specialization entry (for teachers only)
        self.specialization_entry = None
        if self.current_user and hasattr(self.current_user, 'role') and self.current_user.role == 'TEACHER':
            self.specialization_entry = ctk.CTkEntry(
                self.account_frame,
                placeholder_text="Specialization",
                height=40,
                font=self.theme["font_normal"],
                fg_color=self.theme["background"],
                text_color=self.theme["secondary"],
                border_color=self.theme["primary"],
                corner_radius=10
            )
            self.specialization_entry.pack(pady=5, padx=20, fill="x")

        # Update button
        self.update_button = ctk.CTkButton(
            self.account_frame,
            text="Update Account",
            height=40,
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            command=self.update_account
        )
        self.update_button.pack(pady=10)

        # Error/Success message label
        self.message_label = ctk.CTkLabel(
            self.account_frame,
            text="",
            font=self.theme["font_normal"],
            text_color=self.theme["danger"]
        )
        self.message_label.pack(pady=5)

        self.account_frame.pack(pady=10, padx=20, fill="x")

        # Admin-only teacher deletion section
        self.teacher_delete_frame = None
        if self.current_user and hasattr(self.current_user, 'role') and self.current_user.role == 'ADMIN':
            self.teacher_delete_frame = ctk.CTkFrame(self, fg_color=self.theme["frame"])
            self.teacher_delete_label = ctk.CTkLabel(
                self.teacher_delete_frame,
                text="Delete Teacher Account",
                font=self.theme["font_title"],
                text_color=self.theme["secondary"]
            )
            self.teacher_delete_label.pack(pady=10)

            # Teacher selection dropdown
            self.teacher_var = ctk.StringVar(value="Select a teacher")
            self.teacher_option = ctk.CTkOptionMenu(
                self.teacher_delete_frame,
                variable=self.teacher_var,
                values=["Select a teacher"],
                command=self.on_teacher_select,
                font=self.theme["font_normal"],
                fg_color=self.theme["primary"],
                button_color=self.theme["primary"],
                button_hover_color=self.theme["button_hover"],
                text_color=self.theme["secondary"],
                dropdown_fg_color=self.theme["background"],
                dropdown_text_color=self.theme["secondary"]
            )
            self.teacher_option.pack(pady=5, padx=20, fill="x")

            # Delete teacher button
            self.delete_teacher_button = ctk.CTkButton(
                self.teacher_delete_frame,
                text="Delete Selected Teacher",
                height=40,
                font=self.theme["font_normal"],
                fg_color=self.theme["danger"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["secondary"],
                command=self.delete_teacher_account
            )
            self.delete_teacher_button.pack(pady=10)

            self.teacher_delete_frame.pack(pady=10, padx=20, fill="x")

        # Delete account button (own account)
        self.delete_account_frame = ctk.CTkFrame(self, fg_color=self.theme["frame"])
        self.delete_account_button = ctk.CTkButton(
            self.delete_account_frame,
            text="Delete My Account",
            height=50,
            font=self.theme["font_normal"],
            fg_color=self.theme["danger"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            command=self.delete_account
        )
        self.delete_account_button.pack(pady=5, padx=5)
        self.delete_account_frame.pack(pady=10, padx=20, fill="x")

        # Populate form with current user data and teacher list
        self.populate_user_data()
        if self.current_user and hasattr(self.current_user, 'role') and self.current_user.role == 'ADMIN':
            self.populate_teacher_list()

    def populate_user_data(self):
        """Populate the form with the current user's data"""
        if not self.current_user or not hasattr(self.current_user, 'username'):
            self.show_message("No valid user data available.", error=True)
            return

        if not self.db_connection.is_connected():
            self.show_message("Database connection lost.", error=True)
            return

        cursor = None
        try:
            cursor = self.db_connection.connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id, name, email, role FROM users WHERE username = %s", (self.current_user.username,))
            user = cursor.fetchone()
            if user:
                self.name_entry.insert(0, user['name'] or "")
                self.email_entry.insert(0, user['email'] or "")
                self.current_user.user_id = user['user_id']  # Store user_id for updates
                self.current_user.role = user['role']  # Ensure role is set
                if user['role'] == 'TEACHER' and self.specialization_entry:
                    teacher = self.teacher_db.get_teacher_by_id(user['user_id'])
                    if teacher and 'specialization' in teacher:
                        self.specialization_entry.insert(0, teacher['specialization'] or "")
            else:
                self.show_message("User not found in the database.", error=True)
        except Exception as e:
            self.show_message(f"Error loading user data: {str(e)}", error=True)
        finally:
            if cursor:
                cursor.close()

    def populate_teacher_list(self):
        if not self.db_connection.is_connected():
            self.show_message("Database connection lost.", error=True)
            return
        try:
            users = self.admin_db.get_all_users()
            teachers = [u for u in users if
                        u['role'] == 'TEACHER' and u['user_id'] != getattr(self.current_user, 'user_id', None)]
            teacher_options = ["Select a teacher"] + [f"{t['name']} (ID: {t['user_id']})" for t in teachers]
            self.teacher_option.configure(values=teacher_options)
            self.teacher_var.set("Select a teacher")
            self.teacher_map = {f"{t['name']} (ID: {t['user_id']})": t['user_id'] for t in teachers}
        except Exception as e:
            self.show_message(f"Error loading teacher list: {str(e)}", error=True)

    def on_teacher_select(self, selected_teacher):
        """Store the selected teacher's user_id"""
        self.selected_teacher_id = self.teacher_map.get(selected_teacher)

    def change_appearance_mode(self):
        """Change appearance mode"""
        ctk.set_appearance_mode(self.mode_var.get())

    def change_scaling(self, new_scaling: str):
        """Change UI scaling"""
        scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(scaling_float)

    def update_account(self):
        """Update the current user's account information"""
        if not self.db_connection.is_connected():
            self.show_message("Database connection lost.", error=True)
            return

        # Verify user exists
        users = self.admin_db.get_all_users()
        if not any(user['user_id'] == self.current_user.user_id for user in users):
            self.show_message("User not found.", error=True)
            return

        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        specialization = self.specialization_entry.get().strip() if self.current_user.role == 'TEACHER' and self.specialization_entry else None

        # Basic validation
        if not name or not email:
            self.show_message("Name and email cannot be empty.", error=True)
            return

        # Check email uniqueness
        if any(user['email'] == email and user['user_id'] != self.current_user.user_id for user in users):
            self.show_message("Email already in use.", error=True)
            return

        try:
            self.db_connection.connection.start_transaction()
            success = False

            if self.current_user.role == 'TEACHER':
                success = self.teacher_db.update_teacher(
                    user_id=self.current_user.user_id,
                    name=name,
                    email=email,
                    specialization=specialization
                )
            elif self.current_user.role == 'ADMIN':
                success = self.admin_db.update_user(
                    user_id=self.current_user.user_id,
                    name=name,
                    email=email
                )
            else:
                self.show_message("Unsupported role.", error=True)
                self.db_connection.connection.rollback()
                return

            if success:
                self.db_connection.connection.commit()
                self.show_message("Account updated successfully.")
                self.current_user.name = name
                self.current_user.email = email
                if self.current_user.role == 'TEACHER':
                    self.current_user.specialization = specialization
            else:
                self.db_connection.connection.rollback()
                self.show_message("Failed to update account.", error=True)

        except Error as e:
            self.db_connection.connection.rollback()
            self.show_message(f"Error: {str(e)}", error=True)

    def delete_account(self):
        """Delete the currently logged-in user's account and redirect to login page"""
        if not self.db_connection.is_connected():
            self.show_message("Database connection lost.", error=True)
            return

        # Verify user exists
        users = self.admin_db.get_all_users()
        if not any(user['user_id'] == self.current_user.user_id for user in users):
            self.show_message("User not found.", error=True)
            return

        confirm = messagebox.askyesno(
            title="Confirm Deletion",
            message="Are you sure you want to delete your account? This action cannot be undone."
        )
        if not confirm:
            return

        try:
            self.db_connection.connection.start_transaction()
            success = False

            if self.current_user.role == 'TEACHER':
                success = self.teacher_db.remove_teacher(self.current_user.user_id)
            elif self.current_user.role == 'ADMIN':
                success = self.admin_db.delete_user(self.current_user.user_id)
            else:
                self.show_message("Unsupported role.", error=True)
                self.db_connection.connection.rollback()
                return

            if success:
                self.db_connection.connection.commit()
                self.show_message("Account deleted successfully.")
                # Clear logged-in user data
                self.current_user = None
                # Call on_logout to navigate to login page
                if self.on_logout:
                    self.after(1000, self.on_logout)  # Delay to show success message
            else:
                self.db_connection.connection.rollback()
                self.show_message("Failed to delete account.", error=True)

        except Error as e:
            self.db_connection.connection.rollback()
            self.show_message(f"Error: {str(e)}", error=True)

    def delete_teacher_account(self):
        """Delete the selected teacher's account (Admin only)"""
        if self.current_user.role != 'ADMIN':
            self.show_message("Only admins can delete teacher accounts.", error=True)
            return

        if not self.db_connection.is_connected():
            self.show_message("Database connection lost.", error=True)
            return

        if not self.selected_teacher_id:
            self.show_message("No teacher selected.", error=True)
            return

        if self.selected_teacher_id == getattr(self.current_user, 'user_id', None):
            self.show_message("Cannot delete your own account.", error=True)
            return

        # Verify teacher exists
        users = self.admin_db.get_all_users()
        teacher = next((u for u in users if u['user_id'] == self.selected_teacher_id and u['role'] == 'TEACHER'), None)
        if not teacher:
            self.show_message("Teacher not found.", error=True)
            return

        confirm = messagebox.askyesno(
            title="Confirm Teacher Deletion",
            message="Are you sure you want to delete this teacher's account? This action cannot be undone."
        )
        if not confirm:
            return

        try:
            self.db_connection.connection.start_transaction()
            success = self.teacher_db.remove_teacher(self.selected_teacher_id)
            if success:
                self.db_connection.connection.commit()
                self.show_message("Teacher account deleted successfully.")
                self.populate_teacher_list()
            else:
                self.db_connection.connection.rollback()
                self.show_message("Failed to delete teacher account.", error=True)
        except Error as e:
            self.db_connection.connection.rollback()
            self.show_message(f"Error: {str(e)}", error=True)

    def show_message(self, message, error=False):
        """Display a temporary message"""
        self.message_label.configure(
            text=message,
            text_color=self.theme["danger"] if error else self.theme["secondary"]
        )
        self.after(3000, lambda: self.message_label.configure(text=""))

