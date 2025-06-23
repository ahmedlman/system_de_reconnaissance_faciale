CREATE DATABASE student_management;

USE student_management;

CREATE TABLE students (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    class VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    teacher VARCHAR(100),
    photo VARCHAR(255)
);
select * from students;