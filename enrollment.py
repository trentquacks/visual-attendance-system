
import face_recognition
import os
import cv2
import numpy as np
import pickle
import pymysql
from datetime import datetime

# Paths and Global Setup
path = 'Images'
encoding_file = 'encodings.pkl'
images = []
classNames = []


def find_encodings(images):
    encode_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img)
        if encodes:
            encode_list.append(encodes[0])
    return encode_list


def enroll_student(id, name):
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    date_str = now.strftime('%Y-%m-%d')

    try:
        connection = pymysql.connect(
            host='127.0.0.1',  
            user=os.environ.get('SQL_USER'),  
            password=os.environ.get('SQL_PASS'),   
            database='attendance_db'
        )

        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO student (id, name, time_enrolled, date_enrolled) VALUES (%s, %s, %s, %s);",
            (id, name, time_str, date_str)
        )
        connection.commit()
        cursor.close()
        connection.close()

    except pymysql.MySQLError as err:
        print(f"Database error: {err}")


# Load Images from Folder
myList = os.listdir(path)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

# Load or Generate Encodings
if os.path.exists(encoding_file):
    print("Loading encodings from file...")
    with open(encoding_file, 'rb') as f:
        encode_listKnown, classNames = pickle.load(f)
    print("Encodings loaded successfully.")
else:
    print("Encodings not found. Generating...")
    encode_listKnown = find_encodings(images)
    with open(encoding_file, 'wb') as f:
        pickle.dump((encode_listKnown, classNames), f)
    print("Encodings saved to file.")

# Face Recognition from Webcam
cap = cv2.VideoCapture(0)
cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Webcam", 800, 600)

while True:
    success, img = cap.read()

    if not success:
        print("Could not access webcam.")
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    face_location = face_recognition.face_locations(imgS)
    face_encoding = face_recognition.face_encodings(imgS, face_location)

    if face_encoding:
        face_match = face_recognition.compare_faces(encode_listKnown, face_encoding[0], tolerance=0.4)
        face_location = face_location[0]
        print(encode_listKnown)
        print(face_match)

        if True in face_match:
            print("Face already registered.")
            break

        student_number = int(input("Please enter your student number: "))
        student_name = input("Please enter your full name: ")
        
        enroll_student(student_number, student_name)

        y1, x2, y2, x1 = face_location
        y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
        face_crop = img[y1:y2, x1:x2]

        save_path = os.path.join(path, f'{student_number}.jpg')
        cv2.imwrite(save_path, face_crop)
        print(f"Saved cropped face to {save_path}")

        # Update images and classNames
        images.append(face_crop)
        classNames.append(student_number)

        # Recompute encodings and save
        encode_listKnown = find_encodings(images)
        with open(encoding_file, 'wb') as f:
            pickle.dump((encode_listKnown, classNames), f)
        print("Encodings updated and saved.")

    cv2.imshow("Webcam", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


