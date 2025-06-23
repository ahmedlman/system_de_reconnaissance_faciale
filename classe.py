import customtkinter as ctk
from tkinter import messagebox
from database import ClassDB, StudentDB, TeacherDB, SeanceDB, SubjectDB
import re
from config import Theme

class PatchedCTkCheckBox(ctk.CTkCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variable_callback_id = None
        if "variable" in kwargs and kwargs["variable"] is not None:
            self._variable = kwargs["variable"]
            self._variable_callback_id = self._variable.trace_add("write", self._check_state)

    def _check_state(self, *args):
        if self._variable.get():
            self.select()
        else:
            self.deselect()

    def destroy(self):
        if hasattr(self, "_variable") and self._variable is not None and self._variable_callback_id:
            self._variable.trace_remove("write", self._variable_callback_id)
        super().destroy()

class ClassInformation(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.parent = parent
        self.db_connection = db_connection
        self.class_db = ClassDB(db_connection)
        self.student_db = StudentDB(db_connection)
        self.teacher_db = TeacherDB(db_connection)
        self.seance_db = SeanceDB(db_connection)
        self.subject_db = SubjectDB(db_connection)

        # Variables
        self.var_class_id = ctk.StringVar()
        self.var_class_name = ctk.StringVar()
        self.var_academic_year = ctk.StringVar()
        self.var_selected_students = []
        self.var_selected_seances = []
        self.var_teacher = ctk.StringVar(value="Select Teacher")
        self.remove_teacher = False

        # Access MainApp theme
        theme_instance = Theme()
        self.theme = theme_instance.set_application_theme()
        self.create_ui()

    def create_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_container,
            text="📚 Classe Information",
            font=self.theme["font_large"],
            text_color=self.theme["primary"]
        ).pack(pady=(0, 20))

        content_frame = ctk.CTkFrame(main_container, fg_color=self.theme["background"], corner_radius=15)
        content_frame.pack(fill="both", expand=True)

        form_frame = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"], corner_radius=10)
        form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        selection_frame = ctk.CTkFrame(content_frame, fg_color=self.theme["frame"], corner_radius=10)
        selection_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.create_form_fields(form_frame)
        self.create_selection_section(selection_frame)
        self.create_action_buttons(form_frame)

    def create_form_fields(self, parent):
        ctk.CTkLabel(
            parent,
            text="Class Name:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkEntry(
            parent,
            textvariable=self.var_class_name,
            font=self.theme["font_normal"],
            width=250,
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        ).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(
            parent,
            text="*",
            text_color=self.theme["danger"],
            font=("Arial", 14, "bold")
        ).grid(row=0, column=2, sticky="w")

        ctk.CTkLabel(
            parent,
            text="Academic Year:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkEntry(
            parent,
            textvariable=self.var_academic_year,
            font=self.theme["font_normal"],
            width=250,
            fg_color=self.theme["background"],
            border_color=self.theme["primary"],
            corner_radius=8
        ).grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(
            parent,
            text="*",
            text_color=self.theme["danger"],
            font=("Arial", 14, "bold")
        ).grid(row=1, column=2, sticky="w")

        ctk.CTkLabel(
            parent,
            text="Teacher:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.teacher_menu = ctk.CTkOptionMenu(
            parent,
            variable=self.var_teacher,
            values=["Select Teacher"],
            font=self.theme["font_normal"],
            width=250,
            fg_color=self.theme["background"],
            button_color=self.theme["primary"],
            button_hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            dropdown_fg_color=self.theme["background"],
            dropdown_text_color=self.theme["secondary"],
            corner_radius=8
        )
        self.teacher_menu.grid(row=2, column=1, padx=10, pady=5)

        self.load_teachers()

    def create_selection_section(self, parent):
        classes = self.class_db.get_all_classes()
        class_names = ["Select Class"] + [c["class_name"] for c in classes]
        self.class_combobox = ctk.CTkComboBox(
            parent,
            values=class_names,
            font=self.theme["font_normal"],
            width=200,
            fg_color=self.theme["background"],
            button_color=self.theme["primary"],
            button_hover_color=self.theme["button_hover"],
            text_color=self.theme["secondary"],
            dropdown_fg_color=self.theme["background"],
            dropdown_text_color=self.theme["secondary"],
            command=self.on_class_select
        )
        self.class_combobox.pack(pady=5)
        self.class_combobox.set("Select Class")

        ctk.CTkLabel(
            parent,
            text="Select Students:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", padx=10, pady=5)

        self.student_listbox = ctk.CTkTextbox(
            parent,
            height=100,
            width=200,
            fg_color=self.theme["background"],
            text_color=self.theme["secondary"]
        )
        self.student_listbox.pack(pady=5)

        ctk.CTkButton(
            parent,
            text="Add/Remove Students",
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            hover_color=self.theme["button_hover"],
            command=lambda: self.open_selection_dialog("students"),
            width=200
        ).pack(pady=5)

        ctk.CTkLabel(
            parent,
            text="Select Seances:",
            font=self.theme["font_normal"],
            text_color=self.theme["secondary"]
        ).pack(anchor="w", padx=10, pady=5)

        self.seance_listbox = ctk.CTkTextbox(
            parent,
            height=100,
            width=200,
            fg_color=self.theme["background"],
            text_color=self.theme["secondary"]
        )
        self.seance_listbox.pack(pady=5)

        ctk.CTkButton(
            parent,
            text="Add/Remove Seances",
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            hover_color=self.theme["button_hover"],
            command=lambda: self.open_selection_dialog("seances"),
            width=200
        ).pack(pady=5)

    def create_action_buttons(self, parent):
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=20)

        buttons = [
            ("➕ Create", self.theme["success"], self.theme["button_hover"], self.create_class),
            ("🔄 Update", self.theme["warning"], self.theme["button_hover"], self.update_class),
            ("🗑️ Delete", self.theme["danger"], self.theme["button_hover"], self.delete_class),
            ("🧹 Clear", self.theme["sidebar"], self.theme["button_hover"], self.clear_fields),
        ]

        for text, fg_color, hover_color, command in buttons:
            ctk.CTkButton(
                buttons_frame,
                text=text,
                font=self.theme["font_normal"],
                fg_color=fg_color,
                hover_color=hover_color,
                command=command,
                width=120,
                corner_radius=8
            ).pack(side="left", padx=5)

    def load_teachers(self):
        teachers = self.teacher_db.get_all_teachers()
        teacher_options = ["Select Teacher"] + [f"{t['name']} (ID: {t['user_id']})" for t in teachers]
        self.teacher_menu.configure(values=teacher_options)

    def on_class_select(self, choice):
        if choice == "Select Class":
            self.clear_fields()
            return

        classes = self.class_db.get_all_classes()
        selected_class = next((c for c in classes if c["class_name"] == choice), None)

        if selected_class:
            self.var_class_id.set(str(selected_class["class_id"]))
            self.var_class_name.set(selected_class["class_name"])
            self.var_academic_year.set(selected_class["academic_year"])

            class_details = self.class_db.get_class_details(selected_class["class_id"])
            if class_details:
                self.var_selected_students = [s["student_id"] for s in class_details["students"]]
                self.var_selected_seances = [s["seance_id"] for s in class_details["seances"]]

                if class_details["teacher"]:
                    teacher_option = f"{class_details['teacher']['teacher_name']} (ID: {class_details['teacher']['user_id']})"
                    self.var_teacher.set(teacher_option)
                else:
                    self.var_teacher.set("Select Teacher")

                self.update_listboxes()

    def update_listboxes(self):
        self.student_listbox.delete("1.0", "end")
        students = self.student_db.get_all_students()
        for student_id in self.var_selected_students:
            student = next((s for s in students if s["student_id"] == student_id), None)
            if student:
                self.student_listbox.insert("end", f"{student['full_name']}\n")

        self.seance_listbox.delete("1.0", "end")
        seances = self.seance_db.get_all_seances()
        for seance_id in self.var_selected_seances:
            seance = next((s for s in seances if s["seance_id"] == seance_id), None)
            if seance:
                self.seance_listbox.insert("end", f"{seance['name_seance']}\n")

    def open_selection_dialog(self, selection_type):
        top = ctk.CTkToplevel(self)
        top.title(f"Select {selection_type.capitalize()}")
        top.geometry("300x400")
        top.grab_set()

        if selection_type == "students":
            items = self.student_db.get_all_students()
            current_selection = self.var_selected_students
            display_attr = "full_name"
            id_attr = "student_id"
        else:
            items = self.seance_db.get_all_seances()
            current_selection = self.var_selected_seances
            display_attr = "name_seance"
            id_attr = "seance_id"

        vars = []
        for item in items:
            var = ctk.BooleanVar(value=item[id_attr] in current_selection)
            vars.append(var)

            checkbox = PatchedCTkCheckBox(
                top,
                text=item[display_attr],
                variable=var,
                font=self.theme["font_normal"],
                fg_color=self.theme["primary"],
                text_color=self.theme["secondary"],
                hover_color=self.theme["button_hover"]
            )
            checkbox.pack(anchor="w", padx=10, pady=5)

        ctk.CTkButton(
            top,
            text="Confirm",
            font=self.theme["font_normal"],
            fg_color=self.theme["primary"],
            hover_color=self.theme["button_hover"],
            command=lambda: self.confirm_selection(top, items, vars, selection_type, id_attr)
        ).pack(pady=10)
        top.vars = vars

    def confirm_selection(self, top, items, vars, selection_type, id_attr):
        selected_ids = [item[id_attr] for item, var in zip(items, vars) if var.get()]
        if selection_type == "students":
            self.var_selected_students = selected_ids
        else:
            self.var_selected_seances = selected_ids
        self.update_listboxes()
        top.destroy()

    def create_class(self):
        if not self.validate_fields():
            return

        if not self.var_selected_students:
            messagebox.showwarning("Warning", "Please select at least one student.", parent=self)
            return

        if not self.var_selected_seances:
            messagebox.showwarning("Warning", "Please select at least one session (seance).", parent=self)
            return

        if self.var_teacher.get() == "Select Teacher":
            messagebox.showwarning("Warning", "Please assign a teacher to the class.", parent=self)
            return

        try:
            class_id = self.class_db.create_class(
                self.var_class_name.get(),
                self.var_academic_year.get()
            )

            if class_id == "exists":
                messagebox.showwarning("Warning", "Class already exists!", parent=self)
            elif class_id:
                messagebox.showinfo("Success", "Class created successfully!", parent=self)
                self.clear_fields()
                self.refresh_combobox()
            else:
                messagebox.showerror("Error", "Failed to create class", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}", parent=self)

    def update_class(self):
        if not self.var_class_id.get():
            messagebox.showwarning("Warning", "Please select a class to update", parent=self)
            return

        if not self.validate_fields():
            return

        if not messagebox.askyesno(
                "Confirm Update",
                f"Update class {self.var_class_name.get()}?",
                parent=self
        ):
            return

        try:
            class_updated = self.class_db.update_class(
                class_id=self.var_class_id.get(),
                class_name=self.var_class_name.get(),
                academic_year=self.var_academic_year.get()
            )

            students_updated = self.class_db.assign_students_to_class(
                self.var_class_id.get(),
                self.var_selected_students
            ) if self.var_selected_students else False

            seances_updated = self.class_db.assign_seances_to_class(
                self.var_class_id.get(),
                self.var_selected_seances
            ) if self.var_selected_seances else False

            teacher_updated = False
            if self.var_teacher.get() != "Select Teacher":
                teacher_id = int(self.var_teacher.get().split("ID: ")[1].rstrip(")"))
                teacher_updated = self.class_db.assign_teacher_to_class(self.var_class_id.get(), teacher_id)
            elif self.remove_teacher:
                teacher_updated = self.class_db.assign_teacher_to_class(self.var_class_id.get(), None)

            if class_updated or students_updated or seances_updated or teacher_updated:
                messagebox.showinfo("Success", "Class updated successfully!", parent=self)
                self.refresh_combobox()
            else:
                messagebox.showwarning("No Change", "Nothing was changed.", parent=self)

        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}", parent=self)

    def delete_class(self):
        if not self.var_class_id.get():
            messagebox.showwarning("Warning", "Please select a class to delete", parent=self)
            return

        if not messagebox.askyesno("Confirm", "Delete this class permanently?", parent=self):
            return

        try:
            success = self.class_db.delete_class(self.var_class_id.get())
            if success:
                messagebox.showinfo("Success", "Class deleted successfully!", parent=self)
                self.clear_fields()
                self.refresh_combobox()
            else:
                messagebox.showerror("Error", "Failed to delete class", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}", parent=self)

    def clear_fields(self):
        self.var_class_id.set("")
        self.var_class_name.set("")
        self.var_academic_year.set("")
        self.var_selected_students = []
        self.var_selected_seances = []
        self.var_teacher.set("Select Teacher")
        self.student_listbox.delete("1.0", "end")
        self.seance_listbox.delete("1.0", "end")
        self.class_combobox.set("Select Class")
        self.remove_teacher = False

    def refresh_combobox(self):
        classes = self.class_db.get_all_classes()
        class_names = ["Select Class"] + [c["class_name"] for c in classes]
        self.class_combobox.configure(values=class_names)

    def validate_fields(self):
        errors = []
        class_name = self.var_class_name.get().strip()
        academic_year = self.var_academic_year.get().strip()

        if not class_name:
            errors.append("Class name is required")
        if not academic_year:
            errors.append("Academic year is required")
        else:
            if not re.fullmatch(r'\d{4}(-\d{4})?', academic_year):
                errors.append("Academic year must be in format YYYY or YYYY-YYYY")

        if errors:
            messagebox.showwarning("Validation Error", "\n".join(errors), parent=self)
            return False
        return True