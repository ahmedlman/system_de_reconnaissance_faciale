<<<<<<< HEAD
<<<<<<< HEAD
class CaptureFaces:
    def __init__(self, container, db_connection):
        self.db_connection = db_connection
        # Récupère les étudiants ici et les stocke dans self.all_students
        self.all_students = self.fetch_all_students()  # Assurez-vous que cette ligne est bien exécutée avant de l'utiliser
        self.create_ui()

    def fetch_all_students(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM students")  # Vérifie que cette table existe
            return cursor.fetchall()  # Retourne la liste des étudiants sous forme de liste de tuples
        except Exception as e:
            print(f"Erreur lors de la récupération des étudiants: {e}")
            return []  # Retourne une liste vide en cas d'erreur

    def create_ui(self):
        # Appelle populate_student_listbox après avoir récupéré les étudiants
        self.populate_student_listbox()

    def populate_student_listbox(self):
        if not hasattr(self, 'all_students') or not self.all_students:
            print("Aucun étudiant trouvé.")
            return
        self.populate_listbox(self.student_listbox, self.all_students)
=======
class CaptureFaces:
    def __init__(self, container, db_connection):
        self.db_connection = db_connection
        # Récupère les étudiants ici et les stocke dans self.all_students
        self.all_students = self.fetch_all_students()  # Assurez-vous que cette ligne est bien exécutée avant de l'utiliser
        self.create_ui()

    def fetch_all_students(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM students")  # Vérifie que cette table existe
            return cursor.fetchall()  # Retourne la liste des étudiants sous forme de liste de tuples
        except Exception as e:
            print(f"Erreur lors de la récupération des étudiants: {e}")
            return []  # Retourne une liste vide en cas d'erreur

    def create_ui(self):
        # Appelle populate_student_listbox après avoir récupéré les étudiants
        self.populate_student_listbox()

    def populate_student_listbox(self):
        if not hasattr(self, 'all_students') or not self.all_students:
            print("Aucun étudiant trouvé.")
            return
        self.populate_listbox(self.student_listbox, self.all_students)
>>>>>>> 9d1a541 (Initial commit - Upload project)
=======
class CaptureFaces:
    def __init__(self, container, db_connection):
        self.db_connection = db_connection
        # Récupère les étudiants ici et les stocke dans self.all_students
        self.all_students = self.fetch_all_students()  # Assurez-vous que cette ligne est bien exécutée avant de l'utiliser
        self.create_ui()

    def fetch_all_students(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM students")  # Vérifie que cette table existe
            return cursor.fetchall()  # Retourne la liste des étudiants sous forme de liste de tuples
        except Exception as e:
            print(f"Erreur lors de la récupération des étudiants: {e}")
            return []  # Retourne une liste vide en cas d'erreur

    def create_ui(self):
        # Appelle populate_student_listbox après avoir récupéré les étudiants
        self.populate_student_listbox()

    def populate_student_listbox(self):
        if not hasattr(self, 'all_students') or not self.all_students:
            print("Aucun étudiant trouvé.")
            return
        self.populate_listbox(self.student_listbox, self.all_students)
>>>>>>> 263f666345c0bcb90842933d4acc0f0751c416f0
