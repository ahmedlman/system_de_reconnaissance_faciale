import customtkinter as ctk
from PIL import Image
import os
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseConnection, StudentDB, ClassDB, TeacherDB, AttendanceDB, SeanceDB
from config import Theme

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.parent = parent
        self.db_connection = db_connection
        self.student_db = StudentDB(db_connection)
        self.class_db = ClassDB(db_connection)
        self.teacher_db = TeacherDB(db_connection)
        self.attendance_db = AttendanceDB(db_connection)
        self.seance_db = SeanceDB(db_connection)

        # Load theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()

        # Configure frame
        self.configure(fg_color=self.theme["background"])

        # UI Elements
        self.tree_columns = ["Name", "Email", "Class", "Teacher", "Status"]
        self.create_widgets()
        self.load_student_data()

    def get_color(self, color_setting):
        """Helper function to get color based on appearance mode"""
        if isinstance(color_setting, list):
            return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
        return color_setting

    def create_widgets(self):
        """Create the main UI components"""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color=self.theme["frame"], corner_radius=6)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🏠 Home",
            font=self.theme["font_large"],
            text_color=self.theme["primary"]
        )
        title_label.pack(pady=(20, 10))

        # Content frame
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20)

        # Left frame (Stats and Filters)
        left_frame = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"], corner_radius=6)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Stats frame
        stats_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            stats_frame,
            text="Statistics",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        self.stats_labels = {
            'total': self.create_stat_label(stats_frame, "Total Students:", "0"),
            'present': self.create_stat_label(stats_frame, "Present Today:", "0"),
        }

        # Filter frame
        filter_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            filter_frame,
            text="Filters",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        # Teacher filter
        ctk.CTkLabel(
            filter_frame,
            text="Filter by Teacher:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", pady=2)

        self.teacher_filter = ctk.CTkComboBox(
            filter_frame,
            values=self.get_teachers(),
            command=self.filter_students,
            font=self.theme["font_normal"],
            fg_color=self.theme["sidebar"],
            button_color=self.theme["primary"],
            text_color=self.theme["secondary"],
            width=200
        )
        self.teacher_filter.pack(fill="x", pady=5)

        # Class filter
        ctk.CTkLabel(
            filter_frame,
            text="Filter by Class:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", pady=2)

        self.class_filter = ctk.CTkComboBox(
            filter_frame,
            values=self.get_classes(),
            command=self.filter_students,
            font=self.theme["font_normal"],
            fg_color=self.theme["sidebar"],
            button_color=self.theme["primary"],
            text_color=self.theme["secondary"],
            width=200
        )
        self.class_filter.pack(fill="x", pady=5)

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.search_students)
        search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Search students by name...",
            font=self.theme["font_normal"],
            fg_color=self.theme["sidebar"],
            text_color=self.theme["secondary"],
            width=200
        )
        search_entry.pack(fill="x", pady=5)

        # Right frame (Student List and Details)
        right_frame = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"], corner_radius=6)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        content_frame.columnconfigure(1, weight=2)

        # Student list
        student_list_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        student_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(
            student_list_frame,
            text="Student List",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        self.student_tree = ttk.Treeview(
            student_list_frame,
            columns=self.tree_columns,
            show="headings",
            height=15
        )

        for col in self.tree_columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120, anchor="center")

        self.student_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.student_tree.bind("<<TreeviewSelect>>", self.display_student_details)

        # Details frame
        details_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            details_frame,
            text="Student Details",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        self.photo_frame = ctk.CTkFrame(details_frame, height=200, width=200, fg_color=self.theme["sidebar"])
        self.photo_frame.pack(pady=10)
        self.photo_frame.pack_propagate(False)

        self.photo_label = ctk.CTkLabel(
            self.photo_frame,
            text="Select a student",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        )
        self.photo_label.place(relx=0.5, rely=0.5, anchor="center")

        self.details_labels = {}
        detail_fields = ["ID", "Name", "Email", "Class", "Teacher", "Status"]

        for field in detail_fields:
            frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=2)

            ctk.CTkLabel(
                frame,
                text=f"{field}:",
                font=self.theme["font_normal"],
                text_color=self.theme["secondary"],
                width=100,
                anchor="e"
            ).pack(side="left")

            self.details_labels[field.lower().replace(" ", "_")] = ctk.CTkLabel(
                frame,
                text="",
                font=self.theme["font_normal"],
                text_color=self.theme["primary"],
                anchor="w"
            )
            self.details_labels[field.lower().replace(" ", "_")].pack(side="left", fill="x", expand=True)

        # Buttons
        buttons_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkButton(
            buttons_frame,
            text="Mark Present",
            command=lambda: self.update_attendance("Present"),
            fg_color=self.theme["success"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            font=self.theme["font_normal"],
            corner_radius=6
        ).pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Mark Absent",
            command=lambda: self.update_attendance("Absent"),
            fg_color=self.theme["danger"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            font=self.theme["font_normal"],
            corner_radius=6
        ).pack(side="left", fill="x", expand=True, padx=5)

    def create_stat_label(self, parent, text, value):
        """Create a stat label for displaying metrics"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            frame,
            text=text,
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"],
            anchor="w",
            width=150
        ).pack(side="left")
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=self.theme["font_normal"],
            text_color=self.theme["primary"]
        )
        value_label.pack(side="right")
        return value_label

    def get_teachers(self):
        """Fetch all teachers using TeacherDB.get_all_teachers"""
        try:
            teachers = self.teacher_db.get_all_teachers()
            return ["All"] + [teacher['name'] for teacher in teachers]
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching teachers: {str(e)}")
            return ["All"]

    def get_classes(self):
        """Fetch all classes using ClassDB.get_all_classes"""
        try:
            classes = self.class_db.get_all_classes()
            return ["All"] + [class_info['class_name'] for class_info in classes]
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching classes: {str(e)}")
            return ["All"]

    def get_student_class_and_teacher(self, student_id):
        """Fetch class and teacher information for a student using ClassDB.get_class_details"""
        try:
            classes = self.class_db.get_all_classes()
            for class_info in classes:
                class_details = self.class_db.get_class_details(class_info['class_id'])
                if not class_details or 'students' not in class_details or not class_details['students']:
                    print(f"No students found for class {class_info['class_name']}")
                    continue
                for student in class_details['students']:
                    if student['student_id'] == student_id:
                        class_name = class_details['class']['class_name']
                        # Check teacher field and handle different key names
                        if class_details.get('teacher'):
                            teacher_name = class_details['teacher'].get('name', class_details['teacher'].get('teacher_name', 'Unknown Teacher'))
                        else:
                            teacher_name = "No Teacher Assigned"
                        print(f"Student {student_id} found in class {class_name} with teacher {teacher_name}")
                        return {'class_name': class_name, 'teacher_name': teacher_name}
            print(f"Student {student_id} not found in any class")
            return {'class_name': 'No Class', 'teacher_name': 'No Teacher Assigned'}
        except Exception as e:
            print(f"Error fetching class/teacher for student {student_id}: {str(e)}")
            return {'class_name': 'No Class', 'teacher_name': 'No Teacher Assigned'}

    def get_student_attendance_status(self, student_id):
        """Fetch the latest attendance status for a student using AttendanceDB.get_attendance_by_seance"""
        try:
            seances = self.seance_db.get_all_seances()
            today = datetime.now().strftime('%Y-%m-%d')
            today_seance_ids = [s['seance_id'] for s in seances if str(s['date']) == today]

            for seance_id in today_seance_ids:
                attendance_records = self.attendance_db.get_attendance_by_seance(seance_id)
                for record in attendance_records:
                    if record['student_id'] == student_id:
                        print(f"Attendance status for student {student_id} in seance {seance_id}: {record['status']}")
                        return record['status'].capitalize()
            print(f"No attendance record found for student {student_id} today")
            return "Absent"
        except Exception as e:
            print(f"Error fetching attendance status for student {student_id}: {str(e)}")
            return "Absent"

    def load_student_data(self, filter_teacher=None, filter_class=None, search_query=None):
        """Load student data with filters using methods from database.py"""
        try:
            # Fetch all students
            students = self.student_db.get_all_students()
            student_data = []
            print(f"Fetched {len(students)} students")

            for student in students:
                student_id = student['student_id']
                full_name = student['full_name']
                email = student['email']

                # Get class and teacher information
                class_info = self.get_student_class_and_teacher(student_id)
                class_name = class_info['class_name']
                teacher_name = class_info['teacher_name']

                # Get attendance status
                status = self.get_student_attendance_status(student_id)

                # Apply filters
                if filter_teacher and filter_teacher != "All" and teacher_name != filter_teacher:
                    continue
                if filter_class and filter_class != "All" and class_name != filter_class:
                    continue
                if search_query and search_query.lower() not in full_name.lower():
                    continue

                student_data.append((full_name, email, class_name, teacher_name, status))

            # Clear existing data
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)

            # Insert new data
            for data in student_data:
                self.student_tree.insert("", "end", values=data)

            # Update stats
            self.update_stats(student_data)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading student data: {str(e)}")

    def update_stats(self, student_data):
        """Update statistics display"""
        total = len(student_data)
        present = sum(1 for student in student_data if student[4].lower() == "present")

        self.stats_labels['total'].configure(text=str(total))
        self.stats_labels['present'].configure(text=str(present))

    def load_student_photo(self, student_id):
        """Load and display student photo"""
        try:
            student = self.student_db.get_student_by_id(student_id)
            photo_path = student.get('photo') if student else None

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
                    font=self.theme["font_normal"],
                    text_color=self.theme["secondary"]
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error loading photo: {str(e)}")

    def display_student_details(self, event):
        """Display selected student's details"""
        selected = self.student_tree.focus()
        if not selected:
            return

        student_data = self.student_tree.item(selected)["values"]
        if not student_data:
            return

        name, email, class_name, teacher_name, status = student_data

        # Fetch student ID for photo loading
        students = self.student_db.get_all_students()
        student_id = None
        for student in students:
            if student['full_name'] == name and student['email'] == email:
                student_id = student['student_id']
                break

        self.details_labels['id'].configure(text=str(student_id) if student_id else "N/A")
        self.details_labels['name'].configure(text=name)
        self.details_labels['email'].configure(text=email)
        self.details_labels['class'].configure(text=class_name)
        self.details_labels['teacher'].configure(text=teacher_name)
        self.details_labels['status'].configure(text=status)

        if student_id:
            self.load_student_photo(student_id)

    def filter_students(self, *args):
        """Apply teacher and class filters"""
        self.load_student_data(
            filter_teacher=self.teacher_filter.get(),
            filter_class=self.class_filter.get(),
            search_query=self.search_var.get()
        )

    def search_students(self, *args):
        """Apply search filter"""
        self.load_student_data(
            filter_teacher=self.teacher_filter.get(),
            filter_class=self.class_filter.get(),
            search_query=self.search_var.get()
        )

    def update_attendance(self, status):
        """Update attendance for selected student"""
        selected = self.student_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student")
            return

        student_data = self.student_tree.item(selected)["values"]
        if not student_data:
            return

        # Fetch student ID based on name and email
        name, email, _, _, _ = student_data
        students = self.student_db.get_all_students()
        student_id = None
        for student in students:
            if student['full_name'] == name and student['email'] == email:
                student_id = student['student_id']
                break

        if not student_id:
            messagebox.showerror("Error", "Student ID not found")
            return

        try:
            # Find today's active seance
            seances = self.seance_db.get_all_seances()
            today = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            active_seance = None
            for seance in seances:
                if (str(seance['date']) == today and
                        str(seance['start_time']) <= current_time <= str(seance['end_time'])):
                    active_seance = seance
                    break

            if not active_seance:
                messagebox.showwarning("Warning", "No active seance found for the current time")
                return

            success = self.attendance_db.record_attendance(
                seance_id=active_seance['seance_id'],
                person_id=student_id,
                status=status.lower(),
                person_type='student'
            )
            if success:
                messagebox.showinfo("Success", f"Attendance marked as {status} for {student_data[0]}")
                self.load_student_data(
                    filter_teacher=self.teacher_filter.get(),
                    filter_class=self.class_filter.get(),
                    search_query=self.search_var.get()
                )
            else:
                messagebox.showerror("Error", "Failed to record attendance")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error updating attendance: {str(e)}")

# This class is used in the main application to display the home page with student information.don't close the database connection