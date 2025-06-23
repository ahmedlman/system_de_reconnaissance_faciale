from typing import Dict, Any
import customtkinter as ctk
from tkcalendar import Calendar
from database import SeanceDB, TeacherDB, SubjectDB
from tkinter import messagebox
from datetime import datetime, time
from config import Theme

class SeanceInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.parent = parent
        self.db_connection = db_connection
        self.seance_db = SeanceDB(self.db_connection)
        self.teacher_db = TeacherDB(self.db_connection)
        self.subject_db = SubjectDB(self.db_connection)

        # Initialize variables
        self.var_seance_id = ctk.StringVar()
        self.var_seance_name = ctk.StringVar()
        self.var_date = ctk.StringVar()
        self.var_location = ctk.StringVar()
        self.var_start_time = ctk.StringVar()
        self.var_end_time = ctk.StringVar()
        self.var_teacher = ctk.StringVar()
        self.var_subject = ctk.StringVar()
        self.var_search = ctk.StringVar()
        self.current_seance = None

        # Access theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Creates the seance management UI"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        self.configure(fg_color=get_color(self.theme["background"]))
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_container,
            text="📅 Seance Information",
            font=self.theme["font_large"],
            text_color=get_color(self.theme["primary"])
        ).pack(pady=(0, 20))

        # Content frame with two sections
        content_frame = ctk.CTkFrame(main_container, fg_color=get_color(self.theme["background"]), corner_radius=15)
        content_frame.pack(fill="both", expand=True)

        # Left panel - Form section
        form_frame = ctk.CTkFrame(content_frame, fg_color=get_color(self.theme["background"]), corner_radius=10)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Right panel - List section
        list_frame = ctk.CTkFrame(content_frame, fg_color=get_color(self.theme["background"]), corner_radius=10)
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        # Create form fields
        self.create_form_fields(form_frame)
        self.create_action_buttons(form_frame)
        self.create_list_section(list_frame)

        # Load initial data
        self.load_teachers()
        self.load_seances()

    def create_form_fields(self, parent):
        """Creates the form input fields"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        # Title
        ctk.CTkLabel(
            parent,
            text="Seance Information",
            font=self.theme["font_title"],
            text_color=get_color(self.theme["primary"])
        ).pack(pady=(10, 15))

        # Seance Name field
        ctk.CTkLabel(
            parent,
            text="Seance Name:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).pack(anchor="w", padx=10)
        ctk.CTkEntry(
            parent,
            textvariable=self.var_seance_name,
            placeholder_text="Enter seance name",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        ).pack(fill="x", padx=10, pady=(0, 10))

        # Subject field (using CTkEntry)
        ctk.CTkLabel(
            parent,
            text="Subject:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).pack(anchor="w", padx=10)
        ctk.CTkEntry(
            parent,
            textvariable=self.var_subject,
            placeholder_text="Enter subject (e.g., Math)",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        ).pack(fill="x", padx=10, pady=(0, 10))

        # Teacher field
        ctk.CTkLabel(
            parent,
            text="Teacher:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).pack(anchor="w", padx=10)
        self.teacher_menu = ctk.CTkOptionMenu(
            parent,
            variable=self.var_teacher,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            button_color=get_color(self.theme["primary"]),
            button_hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            dropdown_fg_color=get_color(self.theme["background"]),
            dropdown_text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        )
        self.teacher_menu.pack(fill="x", padx=10, pady=(0, 10))

        # Location field
        ctk.CTkLabel(
            parent,
            text="Location:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).pack(anchor="w", padx=10)
        ctk.CTkEntry(
            parent,
            textvariable=self.var_location,
            placeholder_text="Enter location",
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        ).pack(fill="x", padx=10, pady=(0, 10))

        # Date field
        ctk.CTkLabel(
            parent,
            text="Date:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).pack(anchor="w", padx=10)
        date_frame = ctk.CTkFrame(parent, fg_color="transparent")
        date_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkEntry(
            date_frame,
            textvariable=self.var_date,
            placeholder_text="YYYY-MM-DD",
            font=self.theme["font_normal"],
            width=180,
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        ).pack(side="left")

        ctk.CTkButton(
            date_frame,
            text="📅",
            width=40,
            command=self.open_date_picker,
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"],
            corner_radius=8
        ).pack(side="left", padx=10)

        # Time fields
        time_frame = ctk.CTkFrame(parent, fg_color="transparent")
        time_frame.pack(fill="x", pady=10)

        # Start Time
        ctk.CTkLabel(
            time_frame,
            text="Start Time:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).grid(row=0, column=0, padx=5)
        self.start_hour = ctk.CTkEntry(
            time_frame,
            placeholder_text="HH",
            width=50,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        )
        self.start_hour.grid(row=0, column=1, padx=5)
        ctk.CTkLabel(
            time_frame,
            text=":",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).grid(row=0, column=2)
        self.start_minute = ctk.CTkEntry(
            time_frame,
            placeholder_text="MM",
            width=50,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        )
        self.start_minute.grid(row=0, column=3, padx=5)
        ctk.CTkButton(
            time_frame,
            text="🕒",
            width=40,
            command=lambda: self.open_time_picker("start"),
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"],
            corner_radius=8
        ).grid(row=0, column=4, padx=5)

        # End Time
        ctk.CTkLabel(
            time_frame,
            text="End Time:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).grid(row=1, column=0, padx=5)
        self.end_hour = ctk.CTkEntry(
            time_frame,
            placeholder_text="HH",
            width=50,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        )
        self.end_hour.grid(row=1, column=1, padx=5)
        ctk.CTkLabel(
            time_frame,
            text=":",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).grid(row=1, column=2)
        self.end_minute = ctk.CTkEntry(
            time_frame,
            placeholder_text="MM",
            width=50,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        )
        self.end_minute.grid(row=1, column=3, padx=5)
        ctk.CTkButton(
            time_frame,
            text="🕒",
            width=40,
            command=lambda: self.open_time_picker("end"),
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"],
            corner_radius=8
        ).grid(row=1, column=4, padx=5)

    def create_action_buttons(self, parent):
        """Creates the action buttons"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        buttons = [
            ("➕ Create", self.theme["success"], self.theme["button_hover"], self.create_seance),
            ("🔄 Update", self.theme["warning"], self.theme["button_hover"], self.update_seance),
            ("🗑️ Delete", self.theme["danger"], self.theme["button_hover"], self.delete_seance),
            ("🧹 Clear", self.theme["sidebar"], self.theme["button_hover"], self.clear_form),
        ]

        for text, fg_color, hover_color, command in buttons:
            ctk.CTkButton(
                button_frame,
                text=text,
                fg_color=get_color(fg_color),
                hover_color=get_color(hover_color),
                text_color=get_color(self.theme["secondary"]),
                command=command,
                width=100,
                font=self.theme["font_normal"],
                corner_radius=8
            ).pack(side="left", padx=5)

    def create_list_section(self, parent):
        """Creates the seance list section with horizontal scrolling"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkEntry(
            search_frame,
            textvariable=self.var_search,
            placeholder_text="Search seances...",
            width=250,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            border_color=get_color(self.theme["primary"]),
            text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        ).pack(side="left")

        ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=100,
            command=self.search_seances,
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"],
            corner_radius=8
        ).pack(side="left", padx=10)

        # Create a canvas with horizontal scrollbar
        canvas = ctk.CTkCanvas(parent, height=300, highlightthickness=0, bg=get_color(self.theme["background"]))
        canvas.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ctk.CTkScrollbar(parent, orientation="horizontal", command=canvas.xview, fg_color=get_color(self.theme["background"]))
        scrollbar.pack(fill="x", padx=10, pady=(0, 10))

        canvas.configure(xscrollcommand=scrollbar.set)

        # Create an inner frame to hold the seance list
        self.seance_tree = ctk.CTkFrame(canvas, fg_color=get_color(self.theme["background"]))
        canvas.create_window((0, 0), window=self.seance_tree, anchor="nw")

        # Configure canvas to update scroll region
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.seance_tree.bind("<Configure>", configure_canvas)

    def load_teachers(self):
        """Loads teachers for the dropdown"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        try:
            teachers = self.teacher_db.get_all_teachers()
            teacher_options = [f"{t['name']} (ID: {t['user_id']})" for t in teachers]
            self.teacher_menu.configure(
                values=teacher_options,
                fg_color=get_color(self.theme["background"]),
                button_color=get_color(self.theme["primary"]),
                button_hover_color=get_color(self.theme["button_hover"]),
                text_color=get_color(self.theme["secondary"]),
                dropdown_fg_color=get_color(self.theme["background"]),
                dropdown_text_color=get_color(self.theme["secondary"])
            )
            if teacher_options:
                self.var_teacher.set(teacher_options[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load teachers: {str(e)}")

    def load_seances(self):
        """Loads all seances into the list"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        try:
            for widget in self.seance_tree.winfo_children():
                widget.destroy()

            seances = self.seance_db.get_seances_with_subjects()

            header_frame = ctk.CTkFrame(self.seance_tree, fg_color=get_color(self.theme["background"]))
            header_frame.pack(fill="x", pady=(0, 5))

            headers = ["ID", "Name", "Subject", "Teacher", "Date", "Time", "Location"]
            for i, header in enumerate(headers):
                ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=self.theme["font_normal"],
                    text_color=get_color(self.theme["secondary"]),
                    width=100 if i != 1 else 150,
                    anchor="w"
                ).grid(row=0, column=i, padx=2, sticky="w")

            for seance in seances:
                self.add_seance_to_list(seance)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load seances: {str(e)}")

    def add_seance_to_list(self, seance):
        """Adds a single seance to the list"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        seance_frame = ctk.CTkFrame(self.seance_tree, fg_color=get_color(self.theme["background"]), corner_radius=5)
        seance_frame.pack(fill="x", pady=2)

        teacher_name = self.get_teacher_name(seance['teacher_id'])
        subject = seance['subject_name']

        time_str = f"{seance['start_time']} - {seance['end_time']}"

        fields = [
            str(seance['seance_id']),
            seance['name_seance'],
            subject,
            teacher_name,
            seance['date'],
            time_str,
            seance['location']
        ]

        for i, field in enumerate(fields):
            ctk.CTkLabel(
                seance_frame,
                text=field,
                font=self.theme["font_normal"],
                text_color=get_color(self.theme["secondary"]),
                width=100 if i != 1 else 150,
                anchor="w"
            ).grid(row=0, column=i, padx=2, sticky="w")

        seance_frame.bind("<Button-1>", lambda e, s=seance: self.load_seance_details(s))
        for child in seance_frame.winfo_children():
            child.bind("<Button-1>", lambda e, s=seance: self.load_seance_details(s))

    def get_teacher_name(self, teacher_id):
        """Gets teacher name by ID"""
        try:
            teacher = self.teacher_db.get_teacher_by_id(teacher_id)
            return teacher['name'] if teacher else "Unknown"
        except:
            return "Unknown"

    def get_subject_name(self, subject_id):
        """Gets subject name by ID"""
        try:
            subject = self.subject_db.get_subject_by_id(subject_id)
            return subject['subject_name'] if subject else "Unknown"
        except:
            return "Unknown"

    def get_or_create_subject_id(self, subject_name):
        """Gets or creates a subject ID"""
        try:
            if not subject_name or not isinstance(subject_name, str):
                raise ValueError("Subject name must be a non-empty string")

            # Search for existing subject
            subject = self.subject_db.get_subject_by_name(subject_name)
            if subject:
                return subject['subject_id']

            # Create new subject if not found
            subject_id = self.subject_db.add_subject(subject_name)
            if not subject_id:
                raise Exception("Failed to create new subject")
            return subject_id
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get or create subject '{subject_name}': {str(e)}")
            return None

    def load_seance_details(self, seance):
        """Loads seance details into the form for updating"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        try:
            self.current_seance = seance

            # Set the seance ID
            self.var_seance_id.set(str(seance.get('seance_id', '')))

            # Set the seance name
            self.var_seance_name.set(seance.get('name_seance', ''))

            # Set the location
            self.var_location.set(seance.get('location', ''))

            # Set the date
            self.var_date.set(seance.get('date', ''))

            # Set the subject
            subject_id = seance.get('subject_id')
            subject_name = self.get_subject_name(subject_id) if subject_id else ''
            self.var_subject.set(subject_name)

            # Set the teacher
            teacher_id = seance.get('teacher_id')
            teacher_found = False
            for option in self.teacher_menu.cget("values"):
                if teacher_id and str(teacher_id) in option:
                    self.var_teacher.set(option)
                    teacher_found = True
                    break
            if not teacher_found:
                self.var_teacher.set('')  # Clear if teacher not found

            # Set the start and end times
            try:
                start_time_str = str(seance.get('start_time', '00:00:00'))
                end_time_str = str(seance.get('end_time', '00:00:00'))

                start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
                end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

                # Update start time fields
                self.start_hour.delete(0, "end")
                self.start_hour.insert(0, f"{start_time.hour:02d}")
                self.start_minute.delete(0, "end")
                self.start_minute.insert(0, f"{start_time.minute:02d}")

                # Update end time fields
                self.end_hour.delete(0, "end")
                self.end_hour.insert(0, f"{end_time.hour:02d}")
                self.end_minute.delete(0, "end")
                self.end_minute.insert(0, f"{end_time.minute:02d}")

            except ValueError as e:
                messagebox.showwarning("Warning", f"Invalid time format in seance data: {str(e)}")
                self.start_hour.delete(0, "end")
                self.start_minute.delete(0, "end")
                self.end_hour.delete(0, "end")
                self.end_minute.delete(0, "end")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load seance details: {str(e)}")
            self.clear_form()

    def open_date_picker(self):
        """Opens a date picker dialog"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        def set_date():
            self.var_date.set(cal.get_date())
            top.destroy()

        top = ctk.CTkToplevel(self)
        top.title("Select Date")
        top.geometry("300x300")
        top.configure(fg_color=get_color(self.theme["background"]))
        top.grab_set()

        cal = Calendar(top, selectmode="day", date_pattern="y-mm-dd")
        cal.pack(pady=10)

        ctk.CTkButton(
            top,
            text="Select",
            command=set_date,
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"],
            corner_radius=8
        ).pack(pady=10)

    def open_time_picker(self, field_type):
        """Opens a time picker dialog"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        def set_time():
            try:
                hours = int(hour_var.get())
                minutes = int(minute_var.get())
            except ValueError:
                hours = 0
                minutes = 0

            if field_type == "start":
                self.start_hour.delete(0, "end")
                self.start_hour.insert(0, f"{hours:02d}")
                self.start_minute.delete(0, "end")
                self.start_minute.insert(0, f"{minutes:02d}")
            else:
                self.end_hour.delete(0, "end")
                self.end_hour.insert(0, f"{hours:02d}")
                self.end_minute.delete(0, "end")
                self.end_minute.insert(0, f"{minutes:02d}")
            top.destroy()

        top = ctk.CTkToplevel(self)
        top.title(f"Select {field_type.capitalize()} Time")
        top.geometry("250x200")
        top.configure(fg_color=get_color(self.theme["background"]))
        top.grab_set()

        time_frame = ctk.CTkFrame(top, fg_color="transparent")
        time_frame.pack(pady=20)

        # Use StringVar instead of IntVar
        hour_var = ctk.StringVar(value="00")
        ctk.CTkLabel(
            time_frame,
            text="Hours:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).grid(row=0, column=0)
        ctk.CTkOptionMenu(
            time_frame,
            variable=hour_var,
            values=[str(i).zfill(2) for i in range(24)],
            width=60,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            button_color=get_color(self.theme["primary"]),
            button_hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            dropdown_fg_color=get_color(self.theme["background"]),
            dropdown_text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        ).grid(row=0, column=1)

        minute_var = ctk.StringVar(value="00")
        ctk.CTkLabel(
            time_frame,
            text="Minutes:",
            font=self.theme["font_normal"],
            text_color=get_color(self.theme["secondary"])
        ).grid(row=1, column=0)
        ctk.CTkOptionMenu(
            time_frame,
            variable=minute_var,
            values=[str(i).zfill(2) for i in range(60)],
            width=60,
            font=self.theme["font_normal"],
            fg_color=get_color(self.theme["background"]),
            button_color=get_color(self.theme["primary"]),
            button_hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            dropdown_fg_color=get_color(self.theme["background"]),
            dropdown_text_color=get_color(self.theme["secondary"]),
            corner_radius=8
        ).grid(row=1, column=1)

        ctk.CTkButton(
            top,
            text="Set Time",
            command=set_time,
            fg_color=get_color(self.theme["primary"]),
            hover_color=get_color(self.theme["button_hover"]),
            text_color=get_color(self.theme["secondary"]),
            font=self.theme["font_normal"],
            corner_radius=8
        ).pack(pady=10)

    def search_seances(self):
        """Searches seances based on search term"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        search_term = self.var_search.get()
        if not search_term:
            self.load_seances()
            return

        try:
            for widget in self.seance_tree.winfo_children():
                widget.destroy()

            seances = self.seance_db.search_seances(search_term)

            if not seances:
                ctk.CTkLabel(
                    self.seance_tree,
                    text="No seances found matching your search",
                    font=self.theme["font_normal"],
                    text_color=get_color(self.theme["secondary"])
                ).pack(pady=20)
                return

            for seance in seances:
                self.add_seance_to_list(seance)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to search seances: {str(e)}")

    def validate_form(self):
        """Validates the form inputs"""
        required_fields = [
            (self.var_seance_name, "Seance name"),
            (self.var_subject, "Subject"),
            (self.var_teacher, "Teacher"),
            (self.var_date, "Date"),
            (self.var_location, "Location"),
        ]

        for field, name in required_fields:
            if not field.get():
                messagebox.showwarning("Validation", f"{name} is required!")
                return False

        try:
            start_hour = self.start_hour.get()
            start_minute = self.start_minute.get()
            end_hour = self.end_hour.get()
            end_minute = self.end_minute.get()

            if not (start_hour and start_minute and end_hour and end_minute):
                messagebox.showwarning("Validation", "Start and end times are required!")
                return False

            start_time = time(int(start_hour), int(start_minute))
            end_time = time(int(end_hour), int(end_minute))

            if start_time >= end_time:
                messagebox.showwarning("Validation", "End time must be after start time!")
                return False

            self.var_start_time.set(f"{start_hour}:{start_minute}:00")
            self.var_end_time.set(f"{end_hour}:{end_minute}:00")

        except ValueError:
            messagebox.showwarning("Validation", "Invalid time format! Use HH:MM")
            return False

        return True

    def extract_id_from_option(self, option):
        """Extracts ID from teacher option (format: 'Name (ID: 123)')"""
        try:
            return int(option.split("ID: ")[1].rstrip(")"))
        except:
            return None

    def create_seance(self):
        """Creates a new seance"""
        if not self.validate_form():
            return

        teacher_id = self.extract_id_from_option(self.var_teacher.get())
        if not teacher_id:
            messagebox.showwarning("Validation", "Invalid teacher selected!")
            return

        subject_name = self.var_subject.get().strip()
        if not subject_name:
            messagebox.showwarning("Validation", "Subject name cannot be empty!")
            return

        subject_id = self.get_or_create_subject_id(subject_name)
        if not subject_id:
            messagebox.showerror("Error", "Failed to create or find subject!")
            return

        seance_data = {
            'subject_id': subject_id,
            'teacher_id': teacher_id,
            'name_seance': self.var_seance_name.get(),
            'date': self.var_date.get(),
            'location': self.var_location.get(),
            'start_time': self.var_start_time.get(),
            'end_time': self.var_end_time.get()
        }

        try:
            if self.seance_db.check_seance_conflict(
                    seance_data['date'],
                    seance_data['start_time'],
                    seance_data['end_time'],
                    teacher_id
            ):
                messagebox.showwarning("Conflict", "This teacher already has a seance scheduled at this time!")
                return

            self.seance_db.create_seance(
                seance_data['subject_id'],
                seance_data['teacher_id'],
                seance_data['name_seance'],
                seance_data['date'],
                seance_data['location'],
                seance_data['start_time'],
                seance_data['end_time']
            )
            messagebox.showinfo("Success", "Seance created successfully!")
            self.clear_form()
            self.load_seances()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create seance: {str(e)}")

    def update_seance(self):
        """Updates an existing seance"""
        if not self.current_seance:
            messagebox.showwarning("Warning", "Please select a seance to update!")
            return

        if not self.validate_form():
            return

        teacher_id = self.extract_id_from_option(self.var_teacher.get())
        if not teacher_id:
            messagebox.showwarning("Validation", "Invalid teacher selected!")
            return

        subject_name = self.var_subject.get().strip()
        if not subject_name:
            messagebox.showwarning("Validation", "Subject name cannot be empty!")
            return

        subject_id = self.get_or_create_subject_id(subject_name)
        if not subject_id:
            messagebox.showerror("Error", "Failed to create or find subject!")
            return

        seance_data = {
            'seance_id': self.current_seance['seance_id'],
            'subject_id': subject_id,
            'teacher_id': teacher_id,
            'name_seance': self.var_seance_name.get(),
            'date': self.var_date.get(),
            'location': self.var_location.get(),
            'start_time': self.var_start_time.get(),
            'end_time': self.var_end_time.get()
        }

        try:
            if self.seance_db.check_seance_conflict_for_update(
                    seance_data['date'],
                    seance_data['start_time'],
                    seance_data['end_time'],
                    teacher_id,
                    seance_data['seance_id']
            ):
                messagebox.showwarning("Conflict", "This teacher already has another seance scheduled at this time!")
                return

            self.seance_db.update_seance(
                seance_data['seance_id'],
                seance_data['subject_id'],
                seance_data['teacher_id'],
                seance_data['name_seance'],
                seance_data['date'],
                seance_data['location'],
                seance_data['start_time'],
                seance_data['end_time']
            )
            messagebox.showinfo("Success", "Seance updated successfully!")
            self.clear_form()
            self.load_seances()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update seance: {str(e)}")

    def delete_seance(self):
        """Deletes the selected seance"""
        if not self.current_seance:
            messagebox.showwarning("Warning", "Please select a seance to delete!")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this seance?"):
            return

        try:
            self.seance_db.delete_seance(self.current_seance['seance_id'])
            messagebox.showinfo("Success", "Seance deleted successfully!")
            self.clear_form()
            self.load_seances()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete seance: {str(e)}")

    def clear_form(self):
        """Clears all form fields"""
        def get_color(color_setting):
            if isinstance(color_setting, list):
                return color_setting[1] if ctk.get_appearance_mode() == "Dark" else color_setting[0]
            return color_setting

        self.var_seance_id.set("")
        self.var_seance_name.set("")
        self.var_location.set("")
        self.var_date.set("")
        self.var_subject.set("")
        self.start_hour.delete(0, "end")
        self.start_minute.delete(0, "end")
        self.end_hour.delete(0, "end")
        self.end_minute.delete(0, "end")
        self.current_seance = None
        self.load_teachers()