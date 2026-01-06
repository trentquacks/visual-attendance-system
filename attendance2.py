import face_recognition
import os
import cv2
import numpy as np
import gate
from visual_attendance import VisualAttendance

va = VisualAttendance()
stream = va.open_webcam()
connection = va.start_sql(os.environ.get('SQL_USER'),
                          os.environ.get('SQL_PASS'),
                          'attendance_db')

face_is_oriented = 0
while True:
    gate_opened = False
    success, img = stream.read()

    if not success:
        print("No webcam detected")
        break
    
    center_img = va.crop_center(img)

    cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (255, 255, 255), 2)
    cv2.putText(img, "Last log", (50, 540),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Name: " + va.name), (50, 580),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Student Number: " + va.student_id), (50, 620),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    facesCurFrame = face_recognition.face_locations(center_img)

    if not facesCurFrame:
        face_is_oriented = 0

    elif len(facesCurFrame) > 1:
        face_is_oriented = 0
        cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 0, 255), 2)
        cv2.putText(img, "Multiple face detected..", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    elif va.detect_blur(center_img, threshold=150):
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
            encodesCurFrame = face_recognition.face_encodings(center_img, facesCurFrame)
            matches = face_recognition.compare_faces(va.encode_list_known, encodesCurFrame[0], tolerance=.4)

            if not matches:
                break

            faceDis = face_recognition.face_distance(va.encode_list_known, encodesCurFrame[0])
            matchIndex = np.argmin(faceDis)

            if True not in matches:
                cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 0, 255), 2)
                print("Unknown Face Detected")

            if matches[matchIndex]:
                gate_opened = True
                cv2.putText(img, "Access granted!", (va.x0 + 6, va.y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 255, 0), 2)
                gate.open()
                va.mark_attendance(str(va.class_names[matchIndex]), connection)

    va.show_webcam(img)

    if gate_opened:
        cv2.waitKey(2000)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.release()
connection.close()
cv2.destroyAllWindows()


