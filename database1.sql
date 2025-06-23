use student_management;
describe students;
select * from classes;	
describe classes;
describe teachers;
show full tables;
ALTER TABLE classes
change COLUMN tstart t_start TIME NOT NULL,
change COLUMN tend t_end TIME NOT NULL;
ALTER TABLE classes
ADD COLUMN class_date DATE NOT NULL;
ALTER TABLE attendance
ADD COLUMN teacher_id varchar(10);
describe attendance;
ALTER TABLE attendance
ADD COLUMN id_teacher VARCHAR(10),
ADD CONSTRAINT fk_attendance_teacher
FOREIGN KEY (id_teacher) REFERENCES teachers(id);
DROP TABLE recognition_logs;
-- Classes table
CREATE TABLE IF NOT EXISTS classes (
    class_id VARCHAR(50) PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    teacher_id VARCHAR(50) NOT NULL,
    time_start TIME NOT NULL,
    time_end TIME NOT NULL,
    class_date DATE NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);

-- Junction table for class-student relationship
CREATE TABLE IF NOT EXISTS class_students (
    class_id VARCHAR(50),
    student_id VARCHAR(50),
    PRIMARY KEY (class_id, student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
ALTER TABLE classes 
CHANGE teacher teacher_id VARCHAR(50),
ADD FOREIGN KEY (teacher_id) REFERENCES teachers(id);
CREATE TABLE classrooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    teacher_id INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);
SHOW TABLES;
ALTER TABLE students
ADD COLUMN classroom_id INT,
ADD FOREIGN KEY (classroom_id) REFERENCES classrooms(id);

