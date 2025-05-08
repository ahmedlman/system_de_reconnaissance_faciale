import customtkinter as ctk
from database import DatabaseConnection, ClassDB, TeacherDB, StudentDB, SubjectDB
from tkinter import messagebox


class ClassInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="#f5f7fa")
        self.parent = parent
        self.db_connection = db_connection
        self.class_db = ClassDB(self.db_connection)
        self.teacher_db = TeacherDB(self.db_connection)
        self.student_db = StudentDB(self.db_connection)
        self.subject_db = SubjectDB(self.db_connection)

        # UI Configuration
        self.font_title = ("Arial", 24, "bold")
        self.font_subtitle = ("Arial", 14)
        self.font_normal = ("Arial", 12)
        self.primary_color = "#3498db"
        self.secondary_color = "#2c3e50"
        self.bg_color = "#f5f7fa"
        self.input_bg_color = "#ffffff"

        # Initialize variables
        self.var_class_name = ctk.StringVar()
        self.var_academic_year = ctk.StringVar()
        self.var_search = ctk.StringVar()
        self.var_subject = ctk.StringVar()
        self.selected_teacher = None
        self.selected_students = []
        self.subjects = []

        # Create UI
        self.create_ui()

    def create_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_container,
            text="🏫 Class Management System",
            font=self.font_title,
            text_color=self.secondary_color
        ).pack(pady=(0, 20))

        content_frame = ctk.CTkFrame(main_container, corner_radius=15)
        content_frame.pack(fill="both", expand=True)

        self.search_frame = ctk.CTkFrame(content_frame, corner_radius=10, width=250)
        self.search_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.input_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        self.input_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        self.create_search_panel(self.search_frame)
        self.create_input_panel(self.input_frame)

    def create_search_panel(self, parent):
        ctk.CTkLabel(
            parent,
            text="Search Teachers/Students",
            font=self.font_subtitle,
            text_color=self.secondary_color
        ).pack(pady=(10, 20))

        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 10))

        self.teacher_tab_btn = ctk.CTkButton(
            tab_frame,
            text="Teachers",
            font=self.font_normal,
            fg_color=self.primary_color,
            hover_color="#2980b9",
            command=lambda: self.switch_tab("teacher"),
            width=110,
            corner_radius=8
        )
        self.teacher_tab_btn.pack(side="left", padx=5)

        self.student_tab_btn = ctk.CTkButton(
            tab_frame,
            text="Students",
            font=self.font_normal,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=lambda: self.switch_tab("student"),
            width=110,
            corner_radius=8
        )
        self.student_tab_btn.pack(side="left", padx=5)

        self.search_entry = ctk.CTkEntry(
            parent,
            textvariable=self.var_search,
            font=self.font_normal,
            placeholder_text="Search...",
            corner_radius=8
        )
        self.search_entry.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            parent,
            text="🔍 Search",
            font=self.font_normal,
            command=self.search,
            width=100,
            corner_radius=8
        ).pack(pady=5)

        self.results_frame = ctk.CTkScrollableFrame(
            parent,
            height=400,
            corner_radius=8,
            fg_color="#ecf0f1"
        )
        self.results_frame.pack(fill="both", expand=True, pady=5)

        self.current_tab = "teacher"
        self.search()

    def create_input_panel(self, parent):
        ctk.CTkLabel(
            parent,
            text="Class Details",
            font=self.font_subtitle,
            text_color=self.secondary_color
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            parent,
            text="Class Name:",
            font=self.font_normal,
            text_color=self.secondary_color
        ).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkEntry(
            parent,
            textvariable=self.var_class_name,
            font=self.font_normal,
            width=250,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8
        ).grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(
            parent,
            text="Academic Year:",
            font=self.font_normal,
            text_color=self.secondary_color
        ).grid(row=2, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkEntry(
            parent,
            textvariable=self.var_academic_year,
            font=self.font_normal,
            width=250,
            fg_color=self.input_bg_color,
            border_color=self.primary_color,
            corner_radius=8,
            placeholder_text="e.g., 2023-2024"
        ).grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(
            parent,
            text="Subject:",
            font=self.font_normal,
            text_color=self.secondary_color
        ).grid(row=3, column=0, sticky="w", padx=10, pady=5)

        self.subject_menu = ctk.CTkOptionMenu(
            parent,
            variable=self.var_subject,
            values=self.load_subjects(),
            font=self.font_normal,
            width=250,
            fg_color=self.input_bg_color,
            button_color=self.primary_color,
            corner_radius=8
        )
        self.subject_menu.grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkButton(
            parent,
            text="Save Class",
            font=self.font_normal,
            fg_color=self.primary_color,
            hover_color="#2980b9",
            command=self.save_class,
            width=200,
            corner_radius=8
        ).grid(row=4, column=0, columnspan=2, pady=20)

        self.selected_teacher_label = ctk.CTkLabel(
            parent,
            text="Selected Teacher: None",
            font=self.font_normal,
            text_color=self.secondary_color
        )
        self.selected_teacher_label.grid(row=5, column=0, columnspan=2, pady=5)

        self.selected_students_label = ctk.CTkLabel(
            parent,
            text="Selected Students: None",
            font=self.font_normal,
            text_color=self.secondary_color
        )
        self.selected_students_label.grid(row=6, column=0, columnspan=2, pady=5)

    def load_subjects(self):
        try:
            self.subjects = self.subject_db.get_all_subjects()
            subject_names = [subject['subject_name'] for subject in self.subjects]
            return subject_names if subject_names else ["No Subjects Available"]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subjects: {str(e)}")
            return ["No Subjects Available"]

    def switch_tab(self, tab):
        self.current_tab = tab
        self.var_search.set("")
        self.search_entry.configure(placeholder_text=f"Search {tab}s...")

        if tab == "teacher":
            self.teacher_tab_btn.configure(fg_color=self.primary_color)
            self.student_tab_btn.configure(fg_color="#95a5a6")
        else:
            self.teacher_tab_btn.configure(fg_color="#95a5a6")
            self.student_tab_btn.configure(fg_color=self.primary_color)

        self.clear_results()
        self.search()

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def search(self):
        search_term = self.var_search.get().strip()
        self.clear_results()

        try:
            if self.current_tab == "teacher":
                results = self.teacher_db.get_all_teachers(search_term)
                self.display_results(results, "teacher")
            else:
                results = self.student_db.search_student(search_term)
                self.display_results(results, "student")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search: {str(e)}")
            print(e)

    def display_results(self, results, result_type):
        if not results:
            ctk.CTkLabel(
                self.results_frame,
                text=f"No {result_type}s found",
                font=self.font_normal,
                text_color="#7f8c8d"
            ).pack(pady=10)
            return

        for item in results:
            item_frame = ctk.CTkFrame(self.results_frame, corner_radius=5, fg_color="#ffffff")
            item_frame.pack(fill="x", pady=2, padx=5, ipady=5)

            id_key = 'student_id' if result_type == 'student' else 'user_id'
            name_key = 'full_name' if result_type == 'student' else 'name'

            ctk.CTkLabel(
                item_frame,
                text=f"{item[id_key]} - {item[name_key]}",
                font=self.font_normal,
                anchor="w"
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                item_frame,
                text="Select",
                font=("Arial", 10),
                width=60,
                height=25,
                fg_color=self.primary_color,
                hover_color="#2980b9",
                command=lambda x=item: self.select_item(x, result_type)
            ).pack(side="right", padx=5)

    def select_item(self, item, item_type):
        if item_type == "teacher":
            self.selected_teacher = item
            self.selected_teacher_label.configure(
                text=f"Selected Teacher: {item['name']} (ID: {item['user_id']})"
            )
        else:
            if item not in self.selected_students:
                self.selected_students.append(item)
            self.update_selected_students_label()

    def update_selected_students_label(self):
        if not self.selected_students:
            self.selected_students_label.configure(text="Selected Students: None")
        else:
            student_names = ", ".join([f"{s['full_name']} (ID: {s['student_id']})" for s in self.selected_students])
            self.selected_students_label.configure(text=f"Selected Students: {student_names}")

    def save_class(self):
        class_name = self.var_class_name.get().strip()
        academic_year = self.var_academic_year.get().strip()
        subject_name = self.var_subject.get()

        if not class_name or not academic_year or not subject_name:
            messagebox.showerror("Error", "Class Name, Academic Year, and Subject are required!")
            return

        try:
            subject = next((s for s in self.subjects if s['subject_name'] == subject_name), None)
            if not subject:
                messagebox.showerror("Error", "Selected subject not found!")
                return
            subject_id = subject['subject_id']

            class_id = self.class_db.create_class(class_name, academic_year)
            if not class_id:
                messagebox.showerror("Error", "Failed to create class")
                return

            if self.selected_teacher:
                success = self.class_db.assign_teacher_to_class(
                    class_id,
                    self.selected_teacher['user_id'],
                    subject_id
                )
                if not success:
                    messagebox.showwarning("Warning", "Teacher assignment failed")

            if self.selected_students:
                student_ids = [s['student_id'] for s in self.selected_students]
                self.class_db.assign_students_to_class(class_id, student_ids)

            messagebox.showinfo("Success", "Class saved successfully!")
            self.var_class_name.set("")
            self.var_academic_year.set("")
            self.var_subject.set("")
            self.selected_teacher = None
            self.selected_students = []
            self.selected_teacher_label.configure(text="Selected Teacher: None")
            self.selected_students_label.configure(text="Selected Students: None")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save class: {str(e)}")
        self.clear_results()