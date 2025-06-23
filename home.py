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
        self.tree_columns = ["Name", "Email", "Type", "Class/Subject", "Status"]
        self.create_widgets()
        self.load_person_data()

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
            'total': self.create_stat_label(stats_frame, "Total Persons:", "0"),
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

        # Type filter
        ctk.CTkLabel(
            filter_frame,
            text="Filter by Type:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", pady=2)

        self.type_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All", "Student", "Teacher"],
            command=self.filter_persons,
            font=self.theme["font_normal"],
            fg_color=self.theme["sidebar"],
            button_color=self.theme["primary"],
            text_color=self.theme["secondary"],
            width=200
        )
        self.type_filter.pack(fill="x", pady=5)
        self.type_filter.set("All")

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.search_persons)
        search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Search by name...",
            font=self.theme["font_normal"],
            fg_color=self.theme["sidebar"],
            text_color=self.theme["secondary"],
            width=200
        )
        search_entry.pack(fill="x", pady=5)

        # Right frame (Person List and Details)
        right_frame = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"], corner_radius=6)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        content_frame.columnconfigure(1, weight=2)

        # Person list
        person_list_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        person_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(
            person_list_frame,
            text="Person List",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        self.person_tree = ttk.Treeview(
            person_list_frame,
            columns=self.tree_columns,
            show="headings",
            height=15
        )

        for col in self.tree_columns:
            self.person_tree.heading(col, text=col)
            self.person_tree.column(col, width=120, anchor="center")

        self.person_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.person_tree.bind("<<TreeviewSelect>>", self.display_person_details)

        # Details frame
        details_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            details_frame,
            text="Person Details",
            font=self.theme["font_title"],
            text_color=self.theme["primary"]
        ).pack(anchor="w", pady=(0, 5))

        self.photo_frame = ctk.CTkFrame(details_frame, height=200, width=200, fg_color=self.theme["sidebar"])
        self.photo_frame.pack(pady=10)
        self.photo_frame.pack_propagate(False)

        self.photo_label = ctk.CTkLabel(
            self.photo_frame,
            text="Select a person",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        )
        self.photo_label.place(relx=0.5, rely=0.5, anchor="center")

        self.details_labels = {}
        detail_fields = ["ID", "Name", "Email", "Type", "Class/Subject", "Status"]

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

            self.details_labels[field.lower().replace("/", "_").replace(" ", "_")] = ctk.CTkLabel(
                frame,
                text="",
                font=self.theme["font_normal"],
                text_color=self.theme["primary"],
                anchor="w"
            )
            self.details_labels[field.lower().replace("/", "_").replace(" ", "_")].pack(side="left", fill="x",
                                                                                        expand=True)

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

    def get_teacher_subject(self, teacher_id):
        """Get subject for a teacher"""
        try:
            cursor = self.db_connection.connection.cursor(dictionary=True)
            query = """
                SELECT s.subject_name 
                FROM teacher_subject ts
                JOIN subjects s ON ts.subject_id = s.subject_id
                WHERE ts.teacher_id = %s
            """
            cursor.execute(query, (teacher_id,))
            subjects = cursor.fetchall()
            return ", ".join([sub["subject_name"] for sub in subjects]) if subjects else "No Subject"
        except Exception as e:
            print(f"Error fetching teacher subject: {str(e)}")
            return "No Subject"

    def get_person_attendance_status(self, person_id, person_type):
        """Fetch the latest attendance status for a person"""
        try:
            seances = self.seance_db.get_all_seances()
            today = datetime.now().strftime('%Y-%m-%d')
            today_seance_ids = [s['seance_id'] for s in seances if str(s['date']) == today]

            for seance_id in today_seance_ids:
                if person_type == "student":
                    attendance_records = self.attendance_db.get_attendance_by_seance(seance_id)
                    for record in attendance_records:
                        if record['student_id'] == person_id:
                            return record['status'].capitalize()
                else:  # teacher
                    cursor = self.db_connection.connection.cursor(dictionary=True)
                    query = """
                        SELECT status 
                        FROM attendance 
                        WHERE seance_id = %s AND teachers_user_id = %s
                    """
                    cursor.execute(query, (seance_id, person_id))
                    record = cursor.fetchone()
                    if record:
                        return record['status'].capitalize()
            return "Absent"
        except Exception as e:
            print(f"Error fetching attendance status: {str(e)}")
            return "Absent"

    def load_person_data(self, filter_type=None, search_query=None):
        """Load person data with filters"""
        try:
            person_data = []
            print(f"Loading person data with filter: {filter_type}, search: {search_query}")

            # Load students
            if filter_type in [None, "All", "Student"]:
                students = self.student_db.get_all_students()
                for student in students:
                    if search_query and search_query.lower() not in student['full_name'].lower():
                        continue

                    class_info = self.get_student_class_and_teacher(student['student_id'])
                    status = self.get_person_attendance_status(student['student_id'], "student")

                    person_data.append((
                        student['full_name'],
                        student['email'],
                        "Student",
                        class_info['class_name'],
                        status,
                        student['student_id'],
                        "student"
                    ))

            # Load teachers
            if filter_type in [None, "All", "Teacher"]:
                teachers = self.teacher_db.get_all_teachers()
                for teacher in teachers:
                    if search_query and search_query.lower() not in teacher['name'].lower():
                        continue

                    subject = self.get_teacher_subject(teacher['user_id'])
                    status = self.get_person_attendance_status(teacher['user_id'], "teacher")

                    person_data.append((
                        teacher['name'],
                        teacher['email'],
                        "Teacher",
                        subject,
                        status,
                        teacher['user_id'],
                        "teacher"
                    ))

            # Clear existing data
            for item in self.person_tree.get_children():
                self.person_tree.delete(item)

            # Insert new data (only display columns, not ID and type)
            for data in person_data:
                self.person_tree.insert("", "end", values=data[:5], tags=(data[5], data[6]))

            # Update stats
            self.update_stats(person_data)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading person data: {str(e)}")

    def update_stats(self, person_data):
        """Update statistics display"""
        total = len(person_data)
        present = sum(1 for person in person_data if person[4].lower() == "present")

        self.stats_labels['total'].configure(text=str(total))
        self.stats_labels['present'].configure(text=str(present))

    def load_photo(self, person_id, person_type):
        """Load and display person photo"""
        try:
            photo_path = None

            if person_type == "student":
                student = self.student_db.get_student_by_id(person_id)
                photo_path = student.get('photo') if student else None
            else:  # teacher
                teacher = self.teacher_db.get_teacher_photo(person_id)
                photo_path = teacher.get('photo') if teacher else None
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

    def display_person_details(self, event):
        """Display selected person's details"""
        selected = self.person_tree.focus()
        if not selected:
            return

        item = self.person_tree.item(selected)
        values = item["values"]
        tags = item["tags"]

        if not values or not tags:
            return

        person_id = tags[0]
        person_type = tags[1]
        name, email, ptype, class_subject, status = values

        # Update detail labels
        self.details_labels['id'].configure(text=str(person_id))
        self.details_labels['name'].configure(text=name)
        self.details_labels['email'].configure(text=email)
        self.details_labels['type'].configure(text=ptype)
        self.details_labels['class_subject'].configure(text=class_subject)
        self.details_labels['status'].configure(text=status)

        # Load photo
        self.load_photo(person_id, person_type)

    def filter_persons(self, *args):
        """Apply type filter"""
        self.load_person_data(
            filter_type=self.type_filter.get(),
            search_query=self.search_var.get()
        )

    def search_persons(self, *args):
        """Apply search filter"""
        self.load_person_data(
            filter_type=self.type_filter.get(),
            search_query=self.search_var.get()
        )

    def update_attendance(self, status):
        """Update attendance for selected person"""
        selected = self.person_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a person")
            return

        item = self.person_tree.item(selected)
        values = item["values"]
        tags = item["tags"]

        if not values or not tags:
            return

        person_id = tags[0]
        person_type = tags[1]
        name = values[0]

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
                person_id=person_id,
                status=status.lower(),
                person_type='student' if person_type == "student" else 'teacher'
            )

            if success:
                messagebox.showinfo("Success", f"Attendance marked as {status} for {name}")
                self.load_person_data(
                    filter_type=self.type_filter.get(),
                    search_query=self.search_var.get()
                )
            else:
                messagebox.showerror("Error", "Failed to record attendance")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error updating attendance: {str(e)}")

    def get_student_class_and_teacher(self, student_id):
        """Fetch class information for a student"""
        try:
            classes = self.class_db.get_all_classes()
            for class_info in classes:
                class_details = self.class_db.get_class_details(class_info['class_id'])
                if not class_details or 'students' not in class_details or not class_details['students']:
                    continue
                for student in class_details['students']:
                    if student['student_id'] == student_id:
                        return {'class_name': class_details['class']['class_name']}
            return {'class_name': 'No Class'}
        except Exception as e:
            print(f"Error fetching class for student {student_id}: {str(e)}")
            return {'class_name': 'No Class'}