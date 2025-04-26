import mysql.connector
from mysql.connector import Error
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from datetime import datetime
from tkinter import ttk
from database import *
from student import StudentInformation


class HomePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f5f7fa")
        self.display_student_details = StudentInformation
        self.filter_students = StudentInformation
        self.db = StudentInformation
        self.search_students = StudentInformation
        self.parent = parent

        # UI Configuration
        self.font_title = ("Arial", 24, "bold")
        self.font_subtitle = ("Arial", 14)
        self.font_normal = ("Arial", 12)
        self.primary_color = "#3498db"
        self.secondary_color = "#2c3e50"
        self.accent_color = "#e74c3c"

        # Database connection
        self.connection = self.create_db_connection()

        # ✅ Fix: Define columns for Treeview
        self.tree_columns = ["ID", "Name", "Class", "Teacher", "Status", "Last Attendance"]

        # UI Elements
        self.create_widgets()
        self.load_student_data()

    def create_db_connection(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="student_management"
            )
            if connection.is_connected():
                print("Connected to MySQL database")
            return connection
        except Error as e:
            print("Error while connecting to MySQL", e)
            messagebox.showerror("Database Error", f"Failed to connect to database:\n{e}")
            return None

    def create_widgets(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(
            header_frame,
            text="🏠 Student Dashboard",
            font=self.font_title,
            text_color=self.secondary_color
        ).pack(side="left")

        stats_frame = ctk.CTkFrame(self, height=80, fg_color="white", corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.total_label = ctk.CTkLabel(stats_frame, text="Total: 0", font=self.font_subtitle)
        self.total_label.pack(side="left", padx=20, pady=10)

        self.present_label = ctk.CTkLabel(stats_frame, text="Present: 0", font=self.font_subtitle)
        self.present_label.pack(side="left", padx=20, pady=10)

        self.absent_label = ctk.CTkLabel(stats_frame, text="Absent: 0", font=self.font_subtitle)
        self.absent_label.pack(side="left", padx=20, pady=10)

        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            filter_frame,
            text="Filter by Teacher:",
            font=self.font_normal
        ).pack(side="left", padx=(0, 10))

        self.teacher_filter = ctk.CTkComboBox(
            filter_frame,
            values=self.get_teachers(),
            command=self.filter_students,
            dropdown_font=self.font_normal,
            button_color=self.primary_color,
            width=200
        )
        self.teacher_filter.pack(side="left", padx=(0, 20))

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.search_students)
        search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Search students...",
            width=250
        )
        search_entry.pack(side="right")

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        list_frame = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=10)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.student_tree = ttk.Treeview(
            list_frame,
            columns=self.tree_columns,
            show="headings",
            height=15
        )

        for col in self.tree_columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120, anchor="center")

        self.student_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.student_tree.bind("<<TreeviewSelect>>", self.display_student_details)

        details_frame = ctk.CTkFrame(content_frame, width=300, fg_color="white", corner_radius=10)
        details_frame.pack(side="right", fill="y", padx=(10, 0))
        details_frame.pack_propagate(False)

        self.photo_frame = ctk.CTkFrame(details_frame, height=200, width=200, fg_color="#ecf0f1")
        self.photo_frame.pack(pady=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = ctk.CTkLabel(
            self.photo_frame,
            text="Select a student",
            font=self.font_normal,
            text_color="#7f8c8d"
        )
        self.photo_label.place(relx=0.5, rely=0.5, anchor="center")

        self.details_labels = {}
        detail_fields = ["ID", "Name", "Class", "Teacher", "Last Attendance"]

        for field in detail_fields:
            frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(
                frame,
                text=f"{field}:",
                font=self.font_normal,
                text_color=self.secondary_color,
                width=100,
                anchor="e"
            ).pack(side="left")

            self.details_labels[field.lower()] = ctk.CTkLabel(
                frame,
                text="",
                font=self.font_normal,
                text_color="black",
                anchor="w"
            )
            self.details_labels[field.lower()].pack(side="left", fill="x", expand=True)

        buttons_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkButton(
            buttons_frame,
            text="Mark Present",
            #command=self.mark_present(),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        ).pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Mark Absent",
            #command=self.mark_absent,
            fg_color=self.accent_color,
            hover_color="#c0392b"
        ).pack(side="left", fill="x", expand=True, padx=5)

    def load_student_data(self, filter_teacher=None, search_query=None):
        try:
            students = self.db.get_students(filter_teacher, search_query)

            # Clear existing data
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)

            # Insert new data
            for student in students:
                self.student_tree.insert("", "end", values=student)

            self.update_stats(students)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def get_teachers(self):
        try:
            return self.db.get_teachers()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return ["All"]

    def load_student_photo(self, student_id):
        try:
            photo_path = self.db.get_student_photo(student_id)

            if photo_path and os.path.exists(photo_path):
                image = Image.open(photo_path)
                image = image.resize((200, 200))
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 200))
                self.photo_label.configure(image=ctk_image, text="")
                self.photo_label.image = ctk_image
            else:
                self.photo_label.configure(
                    text="No photo available",
                    image=None,
                    font=self.font_normal,
                    text_color="#7f8c8d"
                )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_attendance(self, status):
        selected = self.student_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student first")
            return

        student_data = self.student_tree.item(selected)["values"]
        if not student_data:
            return

        try:
            success = self.db.update_attendance(student_data[0], student_data[1], status)
            if success:
                self.load_student_data()
                messagebox.showinfo("Success", f"Marked {student_data[1]} as {status}")
        except Exception as e:
            messagebox.showerror("Error", str(e))