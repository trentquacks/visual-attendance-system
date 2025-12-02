CREATE DATABASE IF NOT EXISTS attendance_db;

USE attendance_db;

CREATE TABLE student (
    id INT NOT NULL,
    name VARCHAR(100),
    time_enrolled TIME, 
    date_enrolled DATE,

    PRIMARY KEY(id)
);

CREATE TABLE attendance (
    id INT NOT NULL AUTO_INCREMENT,
    time_attended TIME,
    date_attended DATE,
    student_id INT NOT NULL,
    PRIMARY KEY(id),

    INDEX (student_id),

    FOREIGN KEY (student_id)
        REFERENCES student(id)
        ON DELETE CASCADE
);

