import face_recognition
import os
import cv2
import pickle
import pymysql
from datetime import datetime
from visual_attendance import VisualAttendance

va = VisualAttendance()
stream = va.open_webcam()
connection = va.start_sql(os.environ.get('SQL_USER'),
                          os.environ.get('SQL_PASS'),
                          'attendance_db')
face_is_oriented = 0

while True:
    detected = False
    success, img = stream.read()

    if not success:
        print("Could not access webcam.")
        break

    center_img = va.crop_center(img)

    face_on_current_frame = face_recognition.face_locations(center_img)
    cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (255, 255, 255), 2)
    cv2.putText(img, "Last enrolled", (50, 540),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Name: " + va.name), (50, 580),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Student Number: " + va.student_id), (50, 620),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    face_encoding = face_recognition.face_encodings(center_img, face_on_current_frame)

    if not face_on_current_frame:
        face_is_oriented = 0

    elif len(face_on_current_frame) > 1:
        face_is_oriented = 0
        cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 0, 255), 2)
        cv2.putText(img, "Multiple face detected..", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    elif va.detect_blur(center_img, threshold=205):
        face_is_oriented = 0
        cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 165, 255), 2)
        cv2.putText(img, "Please stay still..", (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

    else:
        cv2.putText(img, "Detecting face...", (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 165, 255), 2)
        face_is_oriented += 1

        if face_is_oriented >= 30:
            face_is_oriented = 0 
            detected = True
            face_encoding = face_recognition.face_encodings(center_img, face_on_current_frame)
            print("ENCODE LIST KNOWN:", va.encode_list_known)
            print("CLASS NAMES", va.class_names)
            face_match = face_recognition.compare_faces(va.encode_list_known, face_encoding[0], tolerance=0.4)
            face_on_current_frame = face_on_current_frame[0]

            if True in face_match:
                cv2.putText(img, "Face already registered", (va.x0 + 6, va.y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 255, 0), 2)

            else:
                student_number = int(input("Please enter your student number: "))
                student_name = input("Please enter your full name: ")
                va.enroll_student(student_number, student_name, center_img, connection)
                va.save_encodings()

    va.show_webcam(img)

    if detected:
        cv2.waitKey(2000)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.release()
connection.close()
cv2.destroyAllWindows()


