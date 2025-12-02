# Facial Recognition (WIP)

# What
A fork of this repo
https://github.com/charvik42/Attendance-v2/

...

# TODO
- [x] Seperate Enrollment with the actual Attendance Checker | 11/26/25
- [] Create a ui for console to make the program user friendly
    - [] Attendance
    - [] Enrollment
    - [] SQL Log Viewer (Attendance, filters, etc..)
- [x] Face detection features
    - [x] Only Allow face detection when face is at center | 11/30/25
    - [x] Only allow proper orientation and making sure that image is clear by waiting x seconds before accepting face | 11/30/25
    - [x] Only allow 1 face per detection | 12/1/25
    - [x] Show recent login and indicator for when face is not properly being detected | 12/1/25
- [x] Create a enrollment of faces and their associated infos | 11/26/26
    - [x] Checking of face if it has already been enrolled | 11/27/25
    - [x] Make image name the student id for sql identification | 11/28/25
- [] Create viewer for database
    - [x] restructure database | 11/29/30
- [x] Create database of enrolled students | 11/27/25
    - [] Have an ability to delete student infos (admin)
- [x] Implementation of Arduino | 11/29/30
- [] Optimization
    - [] Optimize performance of webcam by resizing 
    - [] Rewrite codes as objects
