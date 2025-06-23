import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import hashlib
class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="", database="student_management"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    @staticmethod
    def _hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return self.connection
            return False
        except Error as e:
            print("Error while connecting to MySQL", e)
            messagebox.showerror("Database Error", f"Failed to connect to database:\n{e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def get_connection(self):
        return self.connection if self.connection and self.connection.is_connected() else None

    def is_connected(self):
        return self.connection and self.connection.is_connected()
class AuthDB:
    def __init__(self, db_connection):
        self.db = db_connection

    def validate_user(self, username, password):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            if user and user['password'] == DatabaseConnection._hash_password(password):
                return user
            return False
        except Error as e:
            print(f"Error validating user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def create_user(self, name, email, username, password, role):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()

            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return "username_exists"

            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return "email_exists"

            query = """
                INSERT INTO users (name, email, username, password, role)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                name,
                email,
                username,
                DatabaseConnection._hash_password(password),
                role
            ))

            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
class AdminDB:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_users(self):
        if not self.db.is_connected():
            print("Database connection not active")
            return []

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT user_id, name, email, role FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            return users
        except Error as e:
            print(f"Error fetching all users: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    def delete_user(self, user_id):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            self.db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error deleting user: {e}")
            return False

    def update_user_role(self, user_id, new_role):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("UPDATE users SET role = %s WHERE user_id = %s", (new_role, user_id))
            self.db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error updating user role: {e}")
            return False

    def update_user(self, user_id, name, email):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("UPDATE users SET name = %s, email = %s WHERE user_id = %s", (name, email, user_id))
            self.db.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error updating user: {e}")
            return False

class TeacherDB:
    def __init__(self, db_connection):
        self.db = db_connection
    def add_teacher(self, name, email, username, password, cin=None, number=None, specialization=None, hire_date=None,photo=None):
        if not self.db.is_connected():
            return False
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            user_query = """
                INSERT INTO users (name, email, username, password, role)
                VALUES (%s, %s, %s, %s, 'TEACHER')
            """
            cursor.execute(user_query, (name, email, username, DatabaseConnection._hash_password(password)))
            user_id = cursor.lastrowid
            teacher_query = """
                INSERT INTO teachers (user_id, cin, name, email, number, specialization, hire_date, photo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(teacher_query, (user_id, cin, name, email, number, specialization, hire_date, photo))
            self.db.connection.commit()
            return user_id
        except Error as e:
            print(f"Error adding teacher: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    def get_teacher_by_id(self, user_id):
        if not self.db.is_connected():
            return None

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT u.*, t.specialization, t.hire_date, t.is_active
                FROM users u
                JOIN teachers t ON u.user_id = t.user_id
                WHERE u.user_id = %s AND u.role = 'TEACHER'
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching teacher by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    def update_teacher(self, user_id, name=None, email=None, specialization=None):
        if not self.db.is_connected():
            return False
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            if name or email:
                user_updates = []
                user_params = []
                if name:
                    user_updates.append("name = %s")
                    user_params.append(name)
                if email:
                    user_updates.append("email = %s")
                    user_params.append(email)

                user_query = f"UPDATE users SET {', '.join(user_updates)} WHERE user_id = %s"
                user_params.append(user_id)
                cursor.execute(user_query, tuple(user_params))

            if specialization is not None:
                teacher_query = "UPDATE teachers SET specialization = %s WHERE user_id = %s"
                cursor.execute(teacher_query, (specialization, user_id))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating teacher: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    def get_all_teachers(self, active_only=True):
        if not self.db.is_connected():
            return []
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT u.user_id, u.name, u.email, t.cin, t.number, t.specialization, t.hire_date, t.photo
                FROM users u
                JOIN teachers t ON u.user_id = t.user_id
                WHERE u.role = 'TEACHER'
            """
            if active_only:
                query += " AND t.is_active = TRUE"
            query += " ORDER BY u.name"
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching all teachers: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    def remove_teacher(self, teacher_id):
        if not self.db.is_connected():
            return False
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            # Delete from teachers table
            cursor.execute("DELETE FROM teachers WHERE user_id = %s", (teacher_id,))
            print(f"Deleted from teachers: {cursor.rowcount}")
            # Delete from users table
            cursor.execute("DELETE FROM users WHERE user_id = %s", (teacher_id,))
            print(f"Deleted from users: {cursor.rowcount}")
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error deleting teacher: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
class StudentDB:
    def __init__(self, db_connection):
        self.db = db_connection

    def add_student(self, full_name, number, email, enrollment_date, photo=None):
        if not self.db.is_connected():
            raise ConnectionError("Database not connected")

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO students (full_name, number, email, enrollment_date, photo)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, number, email, enrollment_date, photo))
            self.db.connection.commit()
            return cursor.lastrowid
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error adding student: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_student_by_id(self, student_id):
        if not self.db.is_connected():
            raise ConnectionError("Database not connected")

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM students WHERE student_id = %s"
            cursor.execute(query, (student_id,))
            return cursor.fetchone()
        except Error as e:
            raise Exception(f"Error fetching student by ID: {e}")
        finally:
            if cursor:
                cursor.close()

    def remove_student(self, student_id):
        if not self.db.is_connected():
            raise ConnectionError("Database not connected")

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = "DELETE FROM students WHERE student_id = %s"
            cursor.execute(query, (student_id,))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error deleting student: {e}")
        finally:
            if cursor:
                cursor.close()

    def update_student(self, student_id, full_name=None, number=None, email=None, enrollment_date=None, photo=None):
        if not self.db.is_connected():
            raise ConnectionError("Database not connected")

        fields = []
        params = []

        if full_name is not None:
            fields.append("full_name = %s")
            params.append(full_name)
        if number is not None:
            fields.append("number = %s")
            params.append(number)
        if email is not None:
            fields.append("email = %s")
            params.append(email)
        if enrollment_date is not None:
            fields.append("enrollment_date = %s")
            params.append(enrollment_date)
        if photo is not None:
            fields.append("photo = %s")
            params.append(photo)

        if not fields:
            return False

        params.append(student_id)

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = f"UPDATE students SET {', '.join(fields)} WHERE student_id = %s"
            cursor.execute(query, tuple(params))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error updating student: {e}")
        finally:
            if cursor:
                cursor.close()


    def get_all_students(self):
        if not self.db.is_connected():
            raise ConnectionError("Database not connected")

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM students ORDER BY full_name"
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            raise Exception(f"Error fetching all students: {e}")
        finally:
            if cursor:
                cursor.close()
class ClassDB:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_class(self, class_name, academic_year):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()

            # Check if the class already exists
            check_query = """
                SELECT class_id FROM classes 
                WHERE class_name = %s AND academic_year = %s
            """
            cursor.execute(check_query, (class_name, academic_year))
            result = cursor.fetchone()
            if result:
                return "exists"

            # Insert if not exists
            insert_query = """
                INSERT INTO classes (class_name, academic_year)
                VALUES (%s, %s)
            """
            cursor.execute(insert_query, (class_name, academic_year))
            class_id = cursor.lastrowid
            self.db.connection.commit()
            return class_id
        except Error as e:
            print(f"Error creating class: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    def update_class(self, class_id, class_name=None, academic_year=None):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            updates = []
            params = []

            if class_name:
                updates.append("class_name = %s")
                params.append(class_name)
            if academic_year:
                updates.append("academic_year = %s")
                params.append(academic_year)

            if not updates:
                return False

            query = f"UPDATE classes SET {', '.join(updates)} WHERE class_id = %s"
            params.append(class_id)
            cursor.execute(query, tuple(params))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating class: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    def assign_seances_to_class(self, class_id, seance_ids, remove=False):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            if remove:
                # Only remove the specified sessions
                for seance_id in seance_ids:
                    cursor.execute("""
                        DELETE FROM classes_has_seances 
                        WHERE classes_class_id = %s AND seances_seance_id = %s
                    """, (class_id, seance_id))
            else:
                # Clear existing session assignments and assign new ones (current behavior)
                cursor.execute("DELETE FROM classes_has_seances WHERE classes_class_id = %s", (class_id,))
                for seance_id in seance_ids:
                    cursor.execute("""
                        INSERT INTO classes_has_seances (classes_class_id, seances_seance_id)
                        VALUES (%s, %s)
                    """, (class_id, seance_id))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error assigning seances to class: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def assign_students_to_class(self, class_id, student_ids, remove=False):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            if remove:
                # Only remove the specified students
                for student_id in student_ids:
                    cursor.execute("""
                        DELETE FROM class_students 
                        WHERE id_student_class = %s AND idclass_students = %s
                    """, (student_id, class_id))  # 🛠 Corrected order too
            else:
                # Clear existing student assignments and assign new ones
                cursor.execute("DELETE FROM class_students WHERE idclass_students = %s", (class_id,))
                for student_id in student_ids:
                    cursor.execute("""
                        INSERT INTO class_students (idclass_students, id_student_class)
                        VALUES (%s, %s)
                    """, (class_id, student_id))  # ✅ Corrected
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error assigning students to class: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def assign_teacher_to_class(self, class_id, teacher_id=None):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            if teacher_id is None:
                # Remove teacher assignment
                cursor.execute("DELETE FROM teachers_has_classes WHERE classes_class_id = %s", (class_id,))
            else:
                # Assign the teacher to the class
                assign_query = """
                    INSERT INTO teachers_has_classes (classes_class_id, teachers_user_id)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE teachers_user_id = VALUES(teachers_user_id)
                """
                cursor.execute(assign_query, (class_id, teacher_id))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error assigning teacher to class: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def get_class_details(self, class_id):
        if not self.db.is_connected():
            return None

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)

            # Fetch class details
            class_query = "SELECT * FROM classes WHERE class_id = %s"
            cursor.execute(class_query, (class_id,))
            class_data = cursor.fetchone()
            if not class_data:
                return None

            # Fetch associated seances
            seance_query = """
                SELECT s.seance_id, s.name_seance
                FROM classes_has_seances chs
                JOIN seances s ON chs.seances_seance_id = s.seance_id
                WHERE chs.classes_class_id = %s
            """
            cursor.execute(seance_query, (class_id,))
            seances = cursor.fetchall()

            # Fetch associated students
            student_query = """
                SELECT s.student_id, s.full_name
                FROM class_students cs
                JOIN students s ON cs.id_student_class = s.student_id
                WHERE cs.idclass_students = %s
            """
            cursor.execute(student_query, (class_id,))
            students = cursor.fetchall()

            # Fetch associated teacher and subject
            teacher_query = """
                SELECT u.user_id, u.name AS teacher_name, sub.subject_id, sub.subject_name
                FROM teachers_has_classes thc
                JOIN users u ON thc.teachers_user_id = u.user_id
                JOIN teacher_subject ts ON u.user_id = ts.teacher_id
                JOIN subjects sub ON ts.subject_id = sub.subject_id
                WHERE thc.classes_class_id = %s
            """
            cursor.execute(teacher_query, (class_id,))
            teacher_data = cursor.fetchone()

            return {
                'class': class_data,
                'seances': seances,
                'students': students,
                'teacher': teacher_data
            }
        except Error as e:
            print(f"Error fetching class details: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def delete_class(self, class_id):
        if not self.db.is_connected():
            print("Database connection not active")
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            # Verify the class exists
            cursor.execute("SELECT 1 FROM classes WHERE class_id = %s", (class_id,))
            if not cursor.fetchone():
                return False

            # Start transaction
            cursor.execute("START TRANSACTION")

            # Debug: Check classes_has_seances before deletion
            cursor.execute("SELECT * FROM classes_has_seances WHERE classes_class_id = %s", (class_id,))
            seance_records = cursor.fetchall()
            print(f"Records in classes_has_seances for class_id {class_id}: {seance_records}")

            # Delete related records
            cursor.execute("DELETE FROM classes_has_seances WHERE classes_class_id = %s", (class_id,))
            print(f"Deleted {cursor.rowcount} records from classes_has_seances")

            cursor.execute("DELETE FROM class_students WHERE idclass_students = %s", (class_id,))
            print(f"Deleted {cursor.rowcount} records from class_students")

            cursor.execute("DELETE FROM teachers_has_classes WHERE classes_class_id = %s", (class_id,))
            print(f"Deleted {cursor.rowcount} records from teachers_has_classes")

            # Delete the class
            cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
            deleted_rows = cursor.rowcount
            print(f"Deleted {deleted_rows} records from classes")

            self.db.connection.commit()
            return deleted_rows > 0

        except Error as e:
            print(f"Error deleting class: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()


    def get_all_classes(self):
        if not self.db.is_connected():
            return []

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM classes"
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching all classes: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
class SubjectDB:
    def __init__(self, db_connection):
        self.db = db_connection

    def add_subject(self, subject_name):
        if not self.db.is_connected():
            return False

        # Check subject_name length due to VARCHAR(100) constraint
        if len(subject_name) > 100:
            raise ValueError("Subject name exceeds 100 characters")

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO subjects (subject_name)
                VALUES (%s)
            """
            cursor.execute(query, (subject_name,))
            self.db.connection.commit()
            return cursor.lastrowid
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error adding subject: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_subject_by_id(self, subject_id):
        if not self.db.is_connected():
            return None

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM subjects WHERE subject_id = %s"
            cursor.execute(query, (subject_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching subject by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()


    def get_subject_by_name(self, subject_name):
        if not self.db.is_connected():
            return None
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM subjects WHERE subject_name = %s"
            cursor.execute(query, (subject_name,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching subject by name: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
class SeanceDB:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_seance(self, subject_id, teacher_id, name_seance, date, location, start_time, end_time):
        if not self.db.is_connected():
            raise ConnectionError("Database not connected")
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
            INSERT INTO seances (subject_id, teacher_id, name_seance, date, location, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (subject_id, teacher_id, name_seance, date, location, start_time, end_time))
            self.db.connection.commit()
            return True
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error creating seance: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_all_seances(self):
        cursor = self.db.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM seances")
        results = cursor.fetchall()
        cursor.close()
        return results

    def search_seances(self, search_term):
        cursor = self.db.connection.cursor(dictionary=True)
        query = """
        SELECT * FROM seances
        WHERE location LIKE %s OR date LIKE %s OR name_seance LIKE %s
        """
        like_term = f"%{search_term}%"
        cursor.execute(query, (like_term, like_term, like_term))
        results = cursor.fetchall()
        cursor.close()
        return results

    def check_seance_conflict(self, date, start_time, end_time, teacher_id):
        if not self.db.is_connected():
            return False
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
            SELECT COUNT(*) FROM seances
            WHERE date = %s AND teacher_id = %s
            AND (
                (start_time < %s AND end_time > %s) OR
                (start_time >= %s AND start_time < %s)
            )
            """
            cursor.execute(query, (date, teacher_id, end_time, start_time, start_time, end_time))
            conflict_count = cursor.fetchone()[0]
            cursor.close()
            return conflict_count > 0
        except Error as e:
            print(f"Error checking seance conflict: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def check_seance_conflict_for_update(self, date, start_time, end_time, teacher_id, seance_id):
        if not self.db.is_connected():
            return False
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
            SELECT COUNT(*) FROM seances
            WHERE date = %s AND teacher_id = %s
            AND (
                (start_time < %s AND end_time > %s) OR
                (start_time >= %s AND start_time < %s)
            )
            AND seance_id != %s
            """
            cursor.execute(query, (date, teacher_id, end_time, start_time, start_time, end_time, seance_id))
            conflict_count = cursor.fetchone()[0]
            cursor.close()
            return conflict_count > 0
        except Error as e:
            print(f"Error checking seance conflict for update: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update_seance(self, seance_id, subject_id, teacher_id, name_seance, date, location, start_time, end_time):
        if not self.db.is_connected():
            raise ConnectionError("Database not connected")
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
            UPDATE seances 
            SET subject_id=%s, teacher_id=%s, name_seance=%s, date=%s, location=%s, start_time=%s, end_time=%s
            WHERE seance_id=%s
            """
            cursor.execute(query,
                           (subject_id, teacher_id, name_seance, date, location, start_time, end_time, seance_id))
            self.db.connection.commit()
            return True
        except Error as e:
            self.db.connection.rollback()
            raise Exception(f"Error updating seance: {e}")
        finally:
            if cursor:
                cursor.close()

    def delete_seance(self, seance_id):
        if not self.db.is_connected():
            return False
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM seances WHERE seance_id = %s", (seance_id,))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error deleting seance: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def get_seances_with_subjects(self):
        if not self.db.is_connected():
            return []
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
            SELECT s.*, sub.subject_name
            FROM seances s
            JOIN subjects sub ON s.subject_id = sub.subject_id
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching seances with subjects: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
class AttendanceDB:
    def __init__(self, db_connection):
        self.db = db_connection

    def record_attendance(self, seance_id, person_id, status, person_type='student'):
        if not self.db.is_connected():
            return False
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            if person_type == 'student':
                query = """
                    INSERT INTO attendance (seance_id, student_id, status)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status)
                """
            else:  # teacher
                query = """
                    INSERT INTO attendance (seance_id, teachers_user_id, status)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status)
                """
            cursor.execute(query, (seance_id, person_id, status))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error recording attendance: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def get_attendance_by_seance(self, seance_id):
        if not self.db.is_connected():
            return []

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT a.attendance_id, a.status, a.timestamp,
                       s.student_id, s.full_name
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.seance_id = %s
                ORDER BY s.full_name
            """
            cursor.execute(query, (seance_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting attendance by seance: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
