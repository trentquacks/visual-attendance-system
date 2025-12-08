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


class VisualAttendance:
    path = 'Images'
    encoding_file = 'encodings.pkl'
    images = []
    class_names = []
    encode_list_known = []


    def __init__(self):

        pass

    def get_encodings(self):
        encode_list = []
        try:
            for img in self.images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encodes = face_recognition.face_encodings(img)
                if encodes:
                    encode_list.append(encodes[0])
        except FileNotFoundError:
            print("No 'Images' detected. Created.")
            os.mkdir("Images")
        print(encode_list)
        return encode_list

    def load_encodings(self):
        my_list = os.listdir(self.path)
        for cl in my_list:
            current_img = cv2.imread(f'{self.path}/{cl}')
            self.images.append(current_img)
            self.class_names.append(os.path.splitext(cl)[0])

        if os.path.exists(self.encoding_file):
            print("Loading encodings from file...")
            with open(self.encoding_file, 'rb') as f:
                encode_list_known, self.class_names = pickle.load(f)
            print("Encodings loaded successfully.")
        else:
            print("Encodings not found. Generating...")
            encode_list_known = get_encodings()
            with open(self.encoding_file, 'wb') as f:
                pickle.dump((encode_list_known, self.class_names), f)
            print("Encodings saved to file.")


    def start_sql(self, user, password, database):
        self.connection = pymysql.connect(
        host='localhost',  
        user=user,  
        password=password,   
        database=database
        )
        # cursor = self.connection.cursor()
        return self.connection

    
    def mark_attendance(self, student_id, connection):
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%Y-%m-%d')

        try:
            with connection.cursor() as cursor:
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

        except pymysql.MySQLError as err:
            print(f"Database error: {err}")


    def open_webcam(self, width=1280, height=720, webcam=0):
        stream = cv2.VideoCapture(webcam)

        if not stream.isOpened():
            print(f'Webcam {webcam} is not available')
            return exit()

        stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        return stream


    def crop_center(self):
        center_img = img[y1:y0, x0:x1]
        center_img = cv2.cvtColor(center_img, cv2.COLOR_BGR2RGB) 
        return center_img

va = VisualAttendance()
connection = va.start_sql('root', 'root', 'attendance_db')
va.mark_attendance(1, connection)

