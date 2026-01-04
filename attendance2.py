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

not_blur = 0
while True:
    gate_opened = False
    success, img = stream.read()

    if not success:
        print("No webcam detected")
        break
    
    center_img = va.crop_center(img)

    # Draws rectangle
    cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (255, 255, 255), 2)

    # Get face location
    facesCurFrame = face_recognition.face_locations(center_img)
    encodesCurFrame = face_recognition.face_encodings(center_img, facesCurFrame)

    # Show last log
    cv2.putText(img, "Last log", (50, 540),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Name: " + va.name), (50, 580),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Student Number: " + va.student_id), (50, 620),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        if not facesCurFrame:
            not_blur = 0
            continue

        if len(facesCurFrame) > 1:
            not_blur = 0
            cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 0, 255), 2)
            cv2.putText(img, "Multiple face detected..", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            continue
            
        if va.detect_blur(center_img, threshold=150):
            not_blur = 0
            cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 165, 255), 2)
            cv2.putText(img, "Please stay still..", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            continue

        cv2.putText(img, "Detecting face...", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 165, 255), 2)

        matches = face_recognition.compare_faces(va.encode_list_known, encodeFace, tolerance=.4)
        if not matches:
            not_blur = 0
            continue

        faceDis = face_recognition.face_distance(va.encode_list_known, encodeFace)
        matchIndex = np.argmin(faceDis)

        not_blur += 1
        if True not in matches and not_blur >= 30:
            not_blur = 0
            cv2.rectangle(img, (va.x0, va.y0), (va.x1, va.y1), (0, 0, 255), 2)
            print("Unknown Face Detected")
            continue

        if matches[matchIndex] and not_blur >= 30:
            not_blur = 0
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


