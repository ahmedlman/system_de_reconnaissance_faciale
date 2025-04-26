import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime
from database import ClassDB, TeacherDB, StudentDB


class ClassInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="#f5f7fa")

        self.parent = parent
        self.db_connection = db_connection
        self.db = ClassDB(self.db_connection)
        self.teacher_db = TeacherDB(self.db_connection)
        self.student_db = StudentDB(self.db_connection)
        self.selected_students = []
        # UI Configuration
        self.font_title = ("Arial", 24, "bold")
        self.font_subtitle = ("Arial", 14)
        self.font_normal = ("Arial", 12)
        self.primary_color = "#3498db"
        self.secondary_color = "#2c3e50"
        self.success_color = "#2ecc71"
        self.warning_color = "#f39c12"
        self.danger_color = "#e74c3c"
        self.bg_color = "#f5f7fa"
        self.input_bg_color = "#ffffff"

        # Initialize variables
        self.var_teacher_id = ctk.StringVar()
        self.var_student_id = ctk.StringVar()
        self.var_class_name = ctk.StringVar()
        self.var_tstart = ctk.StringVar()
        self.var_tend = ctk.StringVar()
        self.var_date = ctk.StringVar()
        self.var_search_student = ctk.StringVar()

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Creates the class management UI"""
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_container,
            text="🏫 Class Management System",
            font=self.font_title,
            text_color=self.secondary_color
        ).pack(pady=(0, 20))

        # Content frame
        content_frame = ctk.CTkFrame(main_container, corner_radius=15)
        content_frame.pack(fill="both", expand=True)

        # Form section
        form_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # List section
        list_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        list_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Configure grid weights
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Form fields
        self.create_form_fields(form_frame)
        self.create_student_selection_section(list_frame)  # New section for student selection
        self.create_class_list_section(list_frame)  # Existing class list
        self.create_action_buttons(form_frame)

    def create_student_selection_section(self, parent):
        """Creates the student selection section above the class list"""
        # Container for student selection
        student_selection_frame = ctk.CTkFrame(parent, corner_radius=10)
        student_selection_frame.pack(fill="x", pady=(0, 10))

        # Title
        ctk.CTkLabel(
            student_selection_frame,
            text="Add Students to Class",
            font=self.font_subtitle,
            text_color=self.secondary_color
        ).pack(pady=(10, 5))

        # Search frame
        search_frame = ctk.CTkFrame(student_selection_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)

        # Search entry
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.var_search_student,
            font=self.font_normal,
            width=200,
            placeholder_text="Search students...",
            corner_radius=8
        )
        search_entry.pack(side="left", padx=5)

        # Search button
        ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            font=self.font_normal,
            width=100,
            command=self.search_students,
            corner_radius=8
        ).pack(side="left", padx=5)

        # Student list
        self.student_list_frame = ctk.CTkScrollableFrame(
            student_selection_frame,
            height=150,
            corner_radius=8,
            fg_color="#ecf0f1"
        )
        self.student_list_frame.pack(fill="x", pady=5)

        # Action buttons for student selection
        action_frame = ctk.CTkFrame(student_selection_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)

        # Add selected button
        ctk.CTkButton(
            action_frame,
            text="➕ Add Selected",
            font=self.font_normal,
            fg_color=self.success_color,
            hover_color="#27ae60",
            command=self.add_selected_students,
            width=150,
            corner_radius=8
        ).pack(side="left", padx=5)

        # Clear selection button
        ctk.CTkButton(
            action_frame,
            text="🧹 Clear Selection",
            font=self.font_normal,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=self.clear_student_selection,
            width=150,
            corner_radius=8
        ).pack(side="left", padx=5)

    def search_students(self):
        """Search for students based on search term, teacher, and class"""
        search_term = self.var_search_student.get()
        teacher_id = self.var_teacher_id.get()
        class_name = self.var_class_name.get()

        for widget in self.student_list_frame.winfo_children():
            widget.destroy()

        self.selected_students = []

        try:
            students_data = self.student_db.search_students(teacher_id, class_name, search_term)

            if not students_data:
                ctk.CTkLabel(
                    self.student_list_frame,
                    text="No students found",
                    font=self.font_normal,
                    text_color="#7f8c8d"
                ).pack(pady=10)
                return

            for student in students_data:
                student_frame = ctk.CTkFrame(self.student_list_frame, fg_color="transparent")
                student_frame.pack(fill="x", pady=2)

                var = ctk.BooleanVar()
                ctk.CTkCheckBox(
                    student_frame,
                    text="",
                    variable=var,
                    width=20,
                    onvalue=True,
                    offvalue=False
                ).pack(side="left", padx=5)

                ctk.CTkLabel(
                    student_frame,
                    text=f"{student['id']} - {student['name']} ({student['class']})",
                    font=self.font_normal
                ).pack(side="left", padx=5)

                self.selected_students.append({
                    "id": student['id'],
                    "name": student['name'],
                    "var": var
                })

        except Exception as e:
            messagebox.showerror("Error", f"Failed to search students: {str(e)}")

    def add_selected_students(self):
        """Add selected students to the class"""
        if not self.validate_class_fields():
            return

        teacher_id = self.var_teacher_id.get()
        class_name = self.var_class_name.get()
        t_start = self.var_tstart.get()
        t_end = self.var_tend.get()
        class_date = self.var_date.get()

        selected_ids = [s['id'] for s in self.selected_students if s['var'].get()]

        if not selected_ids:
            messagebox.showwarning("Warning", "No students selected!")
            return

        try:
            success_count = 0
            for student_id in selected_ids:
                # Check if this class already exists
                existing_class = self.db.get_class(teacher_id, student_id)
                if existing_class:
                    continue  # Skip if already exists

                # Create the class
                success = self.db.create_class(
                    teacher_id, student_id, class_name,
                    t_start, t_end, class_date
                )
                if success:
                    success_count += 1

            if success_count > 0:
                messagebox.showinfo(
                    "Success",
                    f"Added {success_count} students to the class!"
                )
                # Refresh the class list
                self.search_by_teacher()
            else:
                messagebox.showinfo(
                    "Info",
                    "No new students were added (may already be in class)"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add students: {str(e)}")

    def clear_student_selection(self):
        """Clear the student selection"""
        for student in self.selected_students:
            student['var'].set(False)
        self.var_search_student.set("")
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()


    def validate_class_fields(self):
        """Validates required fields for class creation (without student ID)"""
        if not self.var_teacher_id.get():
            messagebox.showwarning("Validation Error", "Teacher ID is required!")
            return False
        if not self.var_class_name.get():
            messagebox.showwarning("Validation Error", "Class Name is required!")
            return False
        if not self.var_date.get():
            messagebox.showwarning("Validation Error", "Date is required!")
            return False
        if not self.var_tstart.get():
            messagebox.showwarning("Validation Error", "Start time is required!")
            return False
        if not self.var_tend.get():
            messagebox.showwarning("Validation Error", "End time is required!")
            return False

        # Validate time format and logic
        try:
            start_time = datetime.strptime(self.var_tstart.get(), "%H:%M").time()
            end_time = datetime.strptime(self.var_tend.get(), "%H:%M").time()

            if start_time >= end_time:
                messagebox.showwarning("Validation Error", "End time must be after start time!")
                return False
        except ValueError:
            messagebox.showwarning("Validation Error", "Invalid time format! Use HH:MM")
            return False

        # Validate date format
        try:
            datetime.strptime(self.var_date.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Validation Error", "Invalid date format! Use YYYY-MM-DD")
            return False

        return True

    def create_form_fields(self, parent):
        """Creates the form input fields"""
        fields = [
            ("Teacher ID:", self.var_teacher_id, 0, True),
            ("Student ID:", self.var_student_id, 1, True),
            ("Class Name:", self.var_class_name, 2, True),
        ]

        for label_text, var, row, required in fields:
            self.create_labeled_entry(parent, label_text, var, row, required)

        # Date Field
        ctk.CTkLabel(
            parent,
            text="Date:",
            font=self.font_normal,
            text_color=self.secondary_color
        ).grid(row=3, column=0, sticky="w", padx=10, pady=5)

        date_container = ctk.CTkFrame(parent, fg_color="transparent")
        date_container.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.date_entry = ctk.CTkEntry(
            date_container,
            textvariable=self.var_date,
            font=self.font_normal,
            width=180,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.pack(side="left")

        self.date_btn = ctk.CTkButton(
            date_container,
            text="📅",
            width=40,
            height=28,
            command=self.open_date_picker,
            fg_color=self.primary_color,
            hover_color="#2980b9",
            corner_radius=8
        )
        self.date_btn.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            parent,
            text="*",
            text_color=self.danger_color,
            font=("Arial", 14, "bold")
        ).grid(row=3, column=2, sticky="w", padx=(0, 10))

        # Time Start Field
        ctk.CTkLabel(
            parent,
            text="Time Start:",
            font=self.font_normal,
            text_color=self.secondary_color
        ).grid(row=4, column=0, sticky="w", padx=10, pady=5)

        time_start_container = ctk.CTkFrame(parent, fg_color="transparent")
        time_start_container.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self.hours_start = ctk.CTkEntry(
            time_start_container,
            width=40,
            font=self.font_normal,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8,
            placeholder_text="HH"
        )
        self.hours_start.pack(side="left")

        ctk.CTkLabel(
            time_start_container,
            text=":",
            font=self.font_normal,
            text_color=self.secondary_color
        ).pack(side="left", padx=2)

        self.minutes_start = ctk.CTkEntry(
            time_start_container,
            width=40,
            font=self.font_normal,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8,
            placeholder_text="MM"
        )
        self.minutes_start.pack(side="left")

        self.time_start_btn = ctk.CTkButton(
            time_start_container,
            text="🕒",
            width=40,
            height=28,
            command=lambda: self.open_time_picker("start"),
            fg_color=self.primary_color,
            hover_color="#2980b9",
            corner_radius=8
        )
        self.time_start_btn.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            parent,
            text="*",
            text_color=self.danger_color,
            font=("Arial", 14, "bold")
        ).grid(row=4, column=2, sticky="w", padx=(0, 10))

        # Time End Field
        ctk.CTkLabel(
            parent,
            text="Time End:",
            font=self.font_normal,
            text_color=self.secondary_color
        ).grid(row=5, column=0, sticky="w", padx=10, pady=5)

        time_end_container = ctk.CTkFrame(parent, fg_color="transparent")
        time_end_container.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        self.hours_end = ctk.CTkEntry(
            time_end_container,
            width=40,
            font=self.font_normal,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8,
            placeholder_text="HH"
        )
        self.hours_end.pack(side="left")

        ctk.CTkLabel(
            time_end_container,
            text=":",
            font=self.font_normal,
            text_color=self.secondary_color
        ).pack(side="left", padx=2)

        self.minutes_end = ctk.CTkEntry(
            time_end_container,
            width=40,
            font=self.font_normal,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8,
            placeholder_text="MM"
        )
        self.minutes_end.pack(side="left")

        self.time_end_btn = ctk.CTkButton(
            time_end_container,
            text="🕒",
            width=40,
            height=28,
            command=lambda: self.open_time_picker("end"),
            fg_color=self.primary_color,
            hover_color="#2980b9",
            corner_radius=8
        )
        self.time_end_btn.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            parent,
            text="*",
            text_color=self.danger_color,
            font=("Arial", 14, "bold")
        ).grid(row=5, column=2, sticky="w", padx=(0, 10))

    def create_labeled_entry(self, parent, label_text, variable, row, required=False):
        """Helper method to create a labeled entry field"""
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=self.font_normal,
            text_color=self.secondary_color
        ).grid(row=row, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkEntry(
            parent,
            textvariable=variable,
            font=self.font_normal,
            width=250,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8
        ).grid(row=row, column=1, padx=10, pady=5)

        if required:
            ctk.CTkLabel(
                parent,
                text="*",
                text_color=self.danger_color,
                font=("Arial", 14, "bold")
            ).grid(row=row, column=2, sticky="w", padx=(0, 10))

    def create_class_list_section(self, parent):
        """Creates the class list section"""
        # Title for section
        ctk.CTkLabel(
            parent,
            text="Class List",
            font=self.font_subtitle,
            text_color=self.secondary_color
        ).pack(pady=(10, 5))

        # Search frame
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)

        ctk.CTkButton(
            search_frame,
            text="🔍 Search by Teacher",
            font=self.font_normal,
            fg_color=self.secondary_color,
            hover_color="#34495e",
            command=self.search_by_teacher,
            width=180,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="🔍 Search by Student",
            font=self.font_normal,
            fg_color=self.secondary_color,
            hover_color="#34495e",
            command=self.search_by_student,
            width=180,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5)

        # Classes list with improved styling
        self.classes_listbox = ctk.CTkScrollableFrame(
            parent,
            width=400,
            height=300,
            corner_radius=10,
            fg_color="#ecf0f1"
        )
        self.classes_listbox.pack(pady=(5, 10), fill="both", expand=True)

    def create_action_buttons(self, parent):
        """Creates the action buttons"""
        # Section title
        ctk.CTkLabel(
            parent,
            text="Class Actions",
            font=self.font_subtitle,
            text_color=self.secondary_color
        ).grid(row=6, column=0, columnspan=3, sticky="w", padx=10, pady=(20, 5))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.grid(row=7, column=0, columnspan=3, pady=(0, 10), padx=10, sticky="ew")

        # Create button
        ctk.CTkButton(
            buttons_frame,
            text="➕ Create Class",
            font=self.font_normal,
            fg_color=self.success_color,
            hover_color="#27ae60",
            command=self.create_class,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5, pady=5)

        # Update button
        ctk.CTkButton(
            buttons_frame,
            text="🔄 Update",
            font=self.font_normal,
            fg_color=self.warning_color,
            hover_color="#e67e22",
            command=self.update_class,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5, pady=5)

        # Remove button
        ctk.CTkButton(
            buttons_frame,
            text="🗑️ Remove",
            font=self.font_normal,
            fg_color=self.danger_color,
            hover_color="#c0392b",
            command=self.remove_class,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5, pady=5)

        # Clear button
        ctk.CTkButton(
            buttons_frame,
            text="🧹 Clear",
            font=self.font_normal,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=self.clear_fields,
            width=120,
            height=40,
            corner_radius=8
        ).pack(side="left", padx=5, pady=5)

    def open_date_picker(self):
        """Open a date picker dialog with improved design"""
        date_dialog = ctk.CTkToplevel(self)
        date_dialog.title("Select Date")
        date_dialog.geometry("320x350")
        date_dialog.resizable(False, False)
        date_dialog.grab_set()

        # Set dialog position relative to main window
        x = self.winfo_rootx() + 50
        y = self.winfo_rooty() + 50
        date_dialog.geometry(f"+{x}+{y}")

        # Title label
        ctk.CTkLabel(
            date_dialog,
            text="Select a Date",
            font=self.font_subtitle,
            text_color=self.secondary_color
        ).pack(pady=(15, 10))

        # Create calendar in a frame with styling
        cal_frame = ctk.CTkFrame(date_dialog, corner_radius=10, fg_color=self.bg_color)
        cal_frame.pack(padx=20, pady=10, fill="both", expand=True)

        cal = Calendar(
            cal_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            background=self.bg_color,
            foreground=self.secondary_color,
            headersbackground=self.primary_color,
            headersforeground='white',
            selectbackground=self.primary_color
        )
        cal.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons
        buttons_frame = ctk.CTkFrame(date_dialog, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15), padx=20, fill="x")

        # Cancel button
        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            corner_radius=8,
            command=date_dialog.destroy,
            width=100
        ).pack(side="left", padx=5)

        # OK button
        ctk.CTkButton(
            buttons_frame,
            text="Select",
            fg_color=self.primary_color,
            hover_color="#2980b9",
            corner_radius=8,
            command=lambda: self.set_date(cal.get_date(), date_dialog),
            width=100
        ).pack(side="right", padx=5)

    def set_date(self, date_str, window):
        """Set the selected date"""
        try:
            # Validate date format
            datetime.strptime(date_str, '%Y-%m-%d')
            self.var_date.set(date_str)
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")

    def open_time_picker(self, field_type):
        """Open a time picker dialog with improved design"""
        time_dialog = ctk.CTkToplevel(self)
        time_dialog.title(f"Select {field_type.capitalize()} Time")
        time_dialog.geometry("300x250")
        time_dialog.resizable(False, False)
        time_dialog.grab_set()

        # Set dialog position relative to main window
        x = self.winfo_rootx() + 50
        y = self.winfo_rooty() + 50
        time_dialog.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(
            time_dialog,
            text=f"Select {field_type.capitalize()} Time",
            font=self.font_subtitle,
            text_color=self.secondary_color
        ).pack(pady=(15, 20))

        # Time picker container
        time_picker_frame = ctk.CTkFrame(time_dialog, corner_radius=10, fg_color=self.bg_color)
        time_picker_frame.pack(padx=20, pady=10, fill="x")

        # Hours and minutes selectors
        time_fields_frame = ctk.CTkFrame(time_picker_frame, fg_color="transparent")
        time_fields_frame.pack(pady=20)

        # Hours
        hours_frame = ctk.CTkFrame(time_fields_frame, fg_color="transparent")
        hours_frame.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            hours_frame,
            text="Hours",
            font=self.font_normal,
            text_color=self.secondary_color
        ).pack()

        hours_container = ctk.CTkFrame(hours_frame, fg_color="transparent")
        hours_container.pack()

        hours_entry = ctk.CTkEntry(
            hours_container,
            width=40,
            height=40,
            font=self.font_normal,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            justify="center"
        )
        hours_entry.pack(pady=5)

        # Minutes
        minutes_frame = ctk.CTkFrame(time_fields_frame, fg_color="transparent")
        minutes_frame.pack(side="right", padx=(10, 0))

        ctk.CTkLabel(
            minutes_frame,
            text="Minutes",
            font=self.font_normal,
            text_color=self.secondary_color
        ).pack()

        minutes_container = ctk.CTkFrame(minutes_frame, fg_color="transparent")
        minutes_container.pack()

        minutes_entry = ctk.CTkEntry(
            minutes_container,
            width=40,
            height=40,
            font=self.font_normal,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            justify="center"
        )
        minutes_entry.pack(pady=5)

        # Initialize with current time
        current_time = datetime.now().time()
        hours_entry.insert(0, f"{current_time.hour:02d}")
        minutes_entry.insert(0, f"{current_time.minute:02d}")

        buttons_frame = ctk.CTkFrame(time_dialog, fg_color="transparent")
        buttons_frame.pack(pady=20, fill="x", padx=20)

        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            corner_radius=8,
            command=time_dialog.destroy,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Set Time",
            fg_color=self.primary_color,
            hover_color="#2980b9",
            corner_radius=8,
            command=lambda: self.set_time(field_type, hours_entry.get(), minutes_entry.get(), time_dialog),
            width=100
        ).pack(side="right", padx=5)

    def set_time(self, field_type, hours, minutes, window):
        """Set the selected time to the appropriate field"""
        try:
            # Ensure hours and minutes are integers and in valid ranges
            h = max(0, min(23, int(hours)))
            m = max(0, min(59, int(minutes)))

            time_str = f"{h:02d}:{m:02d}"

            if field_type == "start":
                self.var_tstart.set(time_str)
                # Update the entry fields
                self.hours_start.delete(0, "end")
                self.hours_start.insert(0, f"{h:02d}")
                self.minutes_start.delete(0, "end")
                self.minutes_start.insert(0, f"{m:02d}")
            else:
                self.var_tend.set(time_str)
                # Update the entry fields
                self.hours_end.delete(0, "end")
                self.hours_end.insert(0, f"{h:02d}")
                self.minutes_end.delete(0, "end")
                self.minutes_end.insert(0, f"{m:02d}")

            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid time values")

    def create_class(self):
        """Creates a new class"""
        if not self.validate_fields():
            return

        class_data = (
            self.var_teacher_id.get(),
            self.var_student_id.get(),
            self.var_class_name.get(),
            self.var_tstart.get(),
            self.var_tend.get(),
            self.var_date.get()
        )

        try:
            # Verify teacher exists
            teacher = self.teacher_db.get_teacher_by_id(self.var_teacher_id.get())
            if not teacher:
                messagebox.showerror("Error", "Teacher ID does not exist!")
                return

            # Verify student exists
            student = self.student_db.get_student_by_id(self.var_student_id.get())
            if not student:
                messagebox.showerror("Error", "Student ID does not exist!")
                return

            success = self.db.create_class(*class_data)
            if success:
                messagebox.showinfo("Success", "Class created successfully!")
                self.clear_fields()
                # Refresh the display
                self.search_by_teacher()
            else:
                messagebox.showerror("Error", "Failed to create class")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def update_class(self):
        """Updates an existing class"""
        if not self.validate_fields():
            return

        class_data = (
            self.var_teacher_id.get(),
            self.var_student_id.get(),
            self.var_class_name.get(),
            self.var_tstart.get(),
            self.var_tend.get(),
            self.var_date.get()
        )

        try:
            success = self.db.update_class(*class_data)
            if success:
                messagebox.showinfo("Success", "Class updated successfully!")
                # Refresh the display
                if self.var_teacher_id.get():
                    self.search_by_teacher()
                else:
                    self.search_by_student()
            else:
                messagebox.showerror("Error", "Failed to update class")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def remove_class(self):
        """Removes a class"""
        teacher_id = self.var_teacher_id.get()
        student_id = self.var_student_id.get()

        if not teacher_id or not student_id:
            messagebox.showwarning("Warning", "Please enter both Teacher ID and Student ID!")
            return

        if messagebox.askyesno("Confirm", f"Delete this class assignment?"):
            try:
                success = self.db.remove_class(teacher_id, student_id)
                if success:
                    messagebox.showinfo("Success", "Class removed successfully!")
                    self.clear_fields()
                    # Refresh the display
                    if teacher_id:
                        self.search_by_teacher()
                    else:
                        self.search_by_student()
                else:
                    messagebox.showerror("Error", "Failed to remove class")
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def search_by_teacher(self):
        """Searches for classes by teacher ID"""
        teacher_id = self.var_teacher_id.get()
        if not teacher_id:
            messagebox.showwarning("Warning", "Please enter a Teacher ID!")
            return

        try:
            classes = self.db.get_classes_by_teacher(teacher_id)
            self.display_classes(classes, "teacher")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def search_by_student(self):
        """Searches for classes by student ID"""
        student_id = self.var_student_id.get()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter a Student ID!")
            return

        try:
            classes = self.db.get_classes_by_student(student_id)
            self.display_classes(classes, "student")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def display_classes(self, classes, search_type):
        """Displays classes in the listbox"""
        # Clear existing display
        for widget in self.classes_listbox.winfo_children():
            widget.destroy()

        if not classes:
            ctk.CTkLabel(
                self.classes_listbox,
                text="No classes found",
                font=self.font_normal,
                text_color="#7f8c8d"
            ).pack(pady=20)
            return

        # Create headers
        headers = ["Class Name", "Date", "Time"]
        if search_type == "teacher":
            headers.insert(1, "Student")
        else:
            headers.insert(1, "Teacher")

        # Header row
        header_frame = ctk.CTkFrame(self.classes_listbox, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=self.font_subtitle,
                text_color=self.secondary_color
            ).grid(row=0, column=col, padx=5)

        # Class rows
        for idx, cls in enumerate(classes, start=1):
            row_frame = ctk.CTkFrame(self.classes_listbox, corner_radius=5)
            row_frame.pack(fill="x", pady=2)

            # Class name
            ctk.CTkLabel(
                row_frame,
                text=cls['class_name'],
                font=self.font_normal
            ).grid(row=0, column=0, padx=5)

            # Student or teacher name
            name_key = 'student_name' if search_type == 'teacher' else 'teacher_name'
            ctk.CTkLabel(
                row_frame,
                text=cls.get(name_key, 'N/A'),
                font=self.font_normal
            ).grid(row=0, column=1, padx=5)

            # Date
            ctk.CTkLabel(
                row_frame,
                text=cls['class_date'],
                font=self.font_normal
            ).grid(row=0, column=2, padx=5)

            # Time
            ctk.CTkLabel(
                row_frame,
                text=f"{cls['t_start']} - {cls['t_end']}",
                font=self.font_normal
            ).grid(row=0, column=3, padx=5)

            # Action buttons
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=4, padx=5)

            # Edit button
            ctk.CTkButton(
                action_frame,
                text="✏️",
                width=30,
                command=lambda t=cls['teacher_id'], s=cls['id_student']: self.load_class_for_edit(t, s),
                fg_color=self.warning_color,
                hover_color="#e67e22"
            ).pack(side="left", padx=2)

            # Delete button
            ctk.CTkButton(
                action_frame,
                text="🗑️",
                width=30,
                command=lambda t=cls['teacher_id'], s=cls['id_student']: self.confirm_delete_class(t, s),
                fg_color=self.danger_color,
                hover_color="#c0392b"
            ).pack(side="left", padx=2)

    def load_class_for_edit(self, teacher_id, student_id):
        """Loads a class for editing"""
        try:
            class_info = self.db.get_class(teacher_id, student_id)
            if class_info:
                self.var_teacher_id.set(class_info['teacher_id'])
                self.var_student_id.set(class_info['id_student'])
                self.var_class_name.set(class_info['class_name'])
                self.var_tstart.set(class_info['t_start'])
                self.var_tend.set(class_info['t_end'])
                self.var_date.set(class_info['class_date'])
            else:
                messagebox.showwarning("Warning", "Class not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")

    def confirm_delete_class(self, teacher_id, student_id):
        """Confirms and deletes a class"""
        if messagebox.askyesno("Confirm", "Delete this class assignment?"):
            try:
                success = self.db.remove_class(teacher_id, student_id)
                if success:
                    messagebox.showinfo("Success", "Class removed successfully!")
                    # Refresh the display
                    if self.var_teacher_id.get():
                        self.search_by_teacher()
                    else:
                        self.search_by_student()
                else:
                    messagebox.showerror("Error", "Failed to remove class")
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")

    def clear_fields(self):
        """Clears all form fields"""
        for var in [
            self.var_teacher_id,
            self.var_student_id,
            self.var_class_name,
            self.var_tstart,
            self.var_tend,
            self.var_date
        ]:
            var.set("")

    def validate_fields(self):
        """Validates required fields"""
        if not self.var_teacher_id.get():
            messagebox.showwarning("Validation Error", "Teacher ID is required!")
            return False
        if not self.var_student_id.get():
            messagebox.showwarning("Validation Error", "Student ID is required!")
            return False
        if not self.var_class_name.get():
            messagebox.showwarning("Validation Error", "Class Name is required!")
            return False
        if not self.var_date.get():
            messagebox.showwarning("Validation Error", "Date is required!")
            return False
        if not self.var_tstart.get():
            messagebox.showwarning("Validation Error", "Start time is required!")
            return False
        if not self.var_tend.get():
            messagebox.showwarning("Validation Error", "End time is required!")
            return False

        # Validate time format and logic
        try:
            start_time = datetime.strptime(self.var_tstart.get(), "%H:%M").time()
            end_time = datetime.strptime(self.var_tend.get(), "%H:%M").time()

            if start_time >= end_time:
                messagebox.showwarning("Validation Error", "End time must be after start time!")
                return False
        except ValueError:
            messagebox.showwarning("Validation Error", "Invalid time format! Use HH:MM")
            return False

        # Validate date format
        try:
            datetime.strptime(self.var_date.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Validation Error", "Invalid date format! Use YYYY-MM-DD")
            return False

        return True

    def validate_class_fields(self):
        """Validates required fields for class creation (without student ID)"""
        if not self.var_teacher_id.get():
            messagebox.showwarning("Validation Error", "Teacher ID is required!")
            return False
        if not self.var_class_name.get():
            messagebox.showwarning("Validation Error", "Class Name is required!")
            return False
        if not self.var_date.get():
            messagebox.showwarning("Validation Error", "Date is required!")
            return False
        if not self.var_tstart.get():
            messagebox.showwarning("Validation Error", "Start time is required!")
            return False
        if not self.var_tend.get():
            messagebox.showwarning("Validation Error", "End time is required!")
            return False

        # Validate time format and logic
        try:
            start_time = datetime.strptime(self.var_tstart.get(), "%H:%M").time()
            end_time = datetime.strptime(self.var_tend.get(), "%H:%M").time()

            if start_time >= end_time:
                messagebox.showwarning("Validation Error", "End time must be after start time!")
                return False
        except ValueError:
            messagebox.showwarning("Validation Error", "Invalid time format! Use HH:MM")
            return False

        # Validate date format
        try:
            datetime.strptime(self.var_date.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Validation Error", "Invalid date format! Use YYYY-MM-DD")
            return False

        return True