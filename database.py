# database.py
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from datetime import datetime
import hashlib
from typing import List, Dict, Optional


class DatabaseConnection:
    """Handles all database connection operations"""

    def __init__(self, host="localhost", user="root", password="", database="student_management"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    @staticmethod
    def _hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def connect(self):
        """Establish database connection with error handling"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                return True
            return False
        except Error as e:
            print("Error while connecting to MySQL", e)
            messagebox.showerror("Database Error", f"Failed to connect to database:\n{e}")
            return False

    def disconnect(self):
        """Close database connection if it exists"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def get_connection(self):
        """Get the active database connection"""
        return self.connection if self.connection and self.connection.is_connected() else None

    def is_connected(self):
        """Check if database is currently connected"""
        return self.connection and self.connection.is_connected()


class AuthDB:
    """Handles authentication-related database operations"""

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

    def create_user(self, full_name, username, password, email, role="teacher"):
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()

            # Check if the username exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return "username_exists"

            # Check if the email exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return "email_exists"

            # Insert new user into the database
            query = """
                INSERT INTO users (full_name, username, password, email, role, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (
                full_name,
                username,
                DatabaseConnection._hash_password(password),
                email,
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

    def get_user_by_id(self, user_id):
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()


class TeacherDB:
    """Handles teacher-related database operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    def add_teacher(self, teacher_id, cin, name, classe, email, phone, photo=None):
        """Create: Add a new teacher"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO teachers (id, cin, name, classe, email, phone, photo) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (teacher_id, cin, name, classe, email, phone, photo))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error adding teacher: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_teacher_by_id(self, teacher_id):
        """Read: Fetch a single teacher by ID"""
        if not self.db.is_connected():
            return None

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM teachers WHERE id = %s"
            cursor.execute(query, (teacher_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching teacher by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def update_teacher(self, teacher_id, cin, name, classe, email, phone, photo=None):
        """Update: Modify an existing teacher's data"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                UPDATE teachers 
                SET cin=%s, name=%s, classe=%s, email=%s, phone=%s, photo=%s
                WHERE id=%s
            """
            cursor.execute(query, (cin, name, classe, email, phone, photo, teacher_id))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating teacher: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def remove_teacher(self, teacher_id):
        """Delete: Remove a teacher by ID"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = "DELETE FROM teachers WHERE id = %s"
            cursor.execute(query, (teacher_id,))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting teacher: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def all_teachers(self):
        if not self.db.is_connected():
            return []
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM teachers")
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching all teachers: {e}")
            return []
        finally:
            if cursor:
                cursor.close()


class StudentDB:
    """Handles student-related database operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    def add_student(self, student_id, name, student_class, email, phone, teacher, photo):
        """Create: Add a new student"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO students (id, name, class, email, phone, teacher, photo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (student_id, name, student_class, email, phone, teacher, photo))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error adding student: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_student_by_id(self, student_id):
        """Read: Fetch a single student by ID"""
        if not self.db.is_connected():
            return None

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM students WHERE id = %s"
            cursor.execute(query, (student_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching student by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def update_student(self, name, student_class, email, phone, teacher, photo, student_id):
        """Update: Modify an existing student's data"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                UPDATE students 
                SET name=%s, class=%s, email=%s, phone=%s, teacher=%s, photo=%s
                WHERE id=%s
            """
            cursor.execute(query, (name, student_class, email, phone, teacher, photo, student_id))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating student: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def remove_student(self, student_id):
        """Delete: Remove a student by ID"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = "DELETE FROM students WHERE id = %s"
            cursor.execute(query, (student_id,))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting student: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def search_students(self, teacher_id, class_name, name):
        """Search for students by name, teacher, and class"""
        if not self.db.is_connected():
            return []

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)

            if name:
                query = """
                    SELECT * FROM students
                    WHERE teacher_id = %s AND class = %s AND name LIKE %s
                """
                cursor.execute(query, (teacher_id, class_name, '%' + name + '%'))
            else:
                query = """
                    SELECT * FROM students
                    WHERE teacher_id = %s AND class = %s
                """
                cursor.execute(query, (teacher_id, class_name))

            return cursor.fetchall()
        except Error as e:
            print(f"Error searching students: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def all_students(self):
        if not self.db.is_connected():
            return []
        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students")
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching all students: {e}")
            return []
        finally:
            if cursor:
                cursor.close()


class ClassDB:
    """Handles class-related database operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    def get_classes_by_teacher(self, teacher_id):
        """Get all classes taught by a specific teacher with student details"""
        if not self.db.is_connected():
            return []

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    c.teacher_id,
                    c.id_student,
                    c.class_name,
                    c.t_start,
                    c.t_end,
                    c.class_date,
                    s.name as student_name,
                    s.email as student_email
                FROM classes c
                JOIN students s ON c.id_student = s.id
                WHERE c.teacher_id = %s
                ORDER BY c.class_date, c.t_start
            """
            cursor.execute(query, (teacher_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting classes by teacher: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_classes_by_student(self, student_id):
        """Get all classes for a specific student with teacher details"""
        if not self.db.is_connected():
            return []

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    c.teacher_id,
                    c.id_student,
                    c.class_name,
                    c.t_start,
                    c.t_end,
                    c.class_date,
                    t.name as teacher_name,
                    t.email as teacher_email
                FROM classes c
                JOIN teachers t ON c.teacher_id = t.id
                WHERE c.id_student = %s
                ORDER BY c.class_date, c.t_start
            """
            cursor.execute(query, (student_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting classes by student: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def create_class(self, teacher_id, student_id, class_name, t_start, t_end, class_date):
        """Create a new class assignment"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO classes 
                (teacher_id, id_student, class_name, t_start, t_end, class_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (teacher_id, student_id, class_name, t_start, t_end, class_date))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error creating class: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update_class(self, teacher_id, student_id, class_name, t_start, t_end, class_date):
        """Update an existing class assignment"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                UPDATE classes 
                SET class_name = %s,
                    t_start = %s,
                    t_end = %s,
                    class_date = %s
                WHERE teacher_id = %s AND id_student = %s
            """
            cursor.execute(query, (class_name, t_start, t_end, class_date, teacher_id, student_id))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating class: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def remove_class(self, teacher_id, student_id):
        """Remove a class assignment"""
        if not self.db.is_connected():
            return False

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                DELETE FROM classes 
                WHERE teacher_id = %s AND id_student = %s
            """
            cursor.execute(query, (teacher_id, student_id))
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error removing class: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_class(self, teacher_id, student_id):
        """Get a specific class assignment"""
        if not self.db.is_connected():
            return None

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT *
                FROM classes
                WHERE teacher_id = %s AND id_student = %s
            """
            cursor.execute(query, (teacher_id, student_id))
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting class: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    def group_teacher_with_students(self):
        pass
class Get_info_to_capture:
    def __init__(self, db_connection):
        self.db = db_connection
    def get_info(self,student_id,teacher_id):
        """Read: Fetch a single student by ID"""
        if not self.db.is_connected():
            return None

        cursor = None
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM students WHERE id = %s"
            query1 = "SELECT * FROM teachers WHERE id = %s"
            cursor.execute(query,query1, (student_id,teacher_id))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching student by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()




