import face_recognition
import os
import cv2
import numpy as np
import pickle
import pymysql
import gate
import serial.tools.list_ports
from time import sleep
from datetime import datetime

# Paths and Global Setup
path = 'Images'
encoding_file = 'encodings.pkl'
images = []
classNames = []


# Encode Faces
def get_encodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img)
        if encodes:
            encodeList.append(encodes[0])
    return encodeList


def markAttendance(student_id):
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    date_str = now.strftime('%Y-%m-%d')

    try:
        cursor.execute(
            "SELECT * FROM attendance WHERE student_id = %s AND date_attended = %s",
            (student_id, date_str)
        )
        result = cursor.fetchone()

        cursor.execute(
            "SELECT name FROM student WHERE id = %s",
            (student_id)
        )
        name = cursor.fetchone()

        if not result and name is not None:
            print(f"Test {name}")
            name = name[0]
            cursor.execute(
                "INSERT INTO attendance (student_id, time_attended, date_attended) VALUES (%s, %s, %s)",
                (student_id, time_str, date_str)
            )
            connection.commit()
            print(f"Marked attendance for {name} at {time_str} on {date_str}")
        else:
            # print(f"Attendance already marked for {name} on {date_str}.")
            pass

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
        encodeListKnown, classNames = pickle.load(f)
    print("Encodings loaded successfully.")
else:
    print("Encodings not found. Generating...")
    encodeListKnown = get_encodings(images)
    with open(encoding_file, 'wb') as f:
        pickle.dump((encodeListKnown, classNames), f)
    print("Encodings saved to file.")


# Face Recognition from Webcam
WIDTH = 1280
HEIGHT = 720
SCALE = 4
dimension = (WIDTH * SCALE, HEIGHT * SCALE)
registered_this_session = set()
webcam = cv2.VideoCapture(2)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


print("TEST")
print(cv2.CAP_PROP_FRAME_WIDTH)
print(cv2.CAP_PROP_FRAME_HEIGHT)
cv2.namedWindow("Webcam", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Webcam",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

# Get midpoints of width and height
xm = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)
ym = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)

# 2 points to define the center region
offset = 150
x0 = xm - offset
y0 = ym + offset
x1 = xm + offset
y1 = ym - offset

# Open connection to mysql
connection = pymysql.connect(
    host='127.0.0.1',  
    user=os.environ.get('SQL_USER'),  
    password=os.environ.get('SQL_PASS'),   
    database='attendance_db'
)
cursor = connection.cursor()

threshold = 150.00 # higher means more clearer
not_blur = 0

name = ""
student_id = ""

while True:
    gate_opened = False
    success, img = webcam.read()

    if not success:
        print("No webcam detected")
        break
    
    # Defining detection region with drawn rectangle
    center_img = img[y1:y0, x0:x1]
    center_img = cv2.cvtColor(center_img, cv2.COLOR_BGR2RGB) 
    cv2.rectangle(img, (x0, y0), (x1, y1), (255, 255, 255), 2)
    
    # Blur detection
    center_img_gray = cv2.cvtColor(center_img, cv2.COLOR_BGR2GRAY) 
    variance = cv2.Laplacian(center_img_gray, cv2.CV_64F).var()

    # Get face location
    facesCurFrame = face_recognition.face_locations(center_img)
    encodesCurFrame = face_recognition.face_encodings(center_img, facesCurFrame)

    # Show last log
    cv2.putText(img, "Last log", (50, 540),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Name: " + name), (50, 580),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, ("Student Number: " + student_id), (50, 620),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        print(not_blur, variance)
        if not facesCurFrame:
            not_blur = 0
            continue

        if len(facesCurFrame) > 1:
            cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 255), 2)
            cv2.putText(img, "Multiple face detected..", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            continue
            
        if variance < threshold:
            cv2.rectangle(img, (x0, y0), (x1, y1), (0, 165, 255), 2)
            cv2.putText(img, "Please stay still..", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            not_blur = 0
            continue

        cv2.putText(img, "Detecting face...", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        cv2.rectangle(img, (x0, y0), (x1, y1), (0, 165, 255), 2)

        not_blur += 1

        matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=.4)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if True not in matches and not_blur >= 30:
            not_blur = 0
            cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 255), 2)
            print("Unknown Face Detected")

            continue

        if matches[matchIndex] and not_blur >= 30:
            not_blur = 0
            gate_opened = True
            print("MATCHES: ", matches)
            print("FD:", faceDis)
            print("MI:", matchIndex)
            print("CM:", classNames)

            cursor.execute(
                "SELECT name FROM student WHERE id = %s",
                (classNames[matchIndex]))

            name = cursor.fetchone()
            name = name[0]
            student_id = str(classNames[matchIndex])

            cv2.putText(img, "Access granted!", (x0 + 6, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 0), 2)

            # gate.open()
            markAttendance(name)

    resized_frame = cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)
    cv2.imshow("Webcam", resized_frame)

    if gate_opened:
        cv2.waitKey(2000)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam.release()
cursor.close()
connection.close()
cv2.destroyAllWindows()


