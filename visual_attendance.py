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
    name = ""
    student_id = ""


    def __init__(self):
        self.load_encodings()

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
        return encode_list


    def load_encodings(self):
        my_list = os.listdir(self.path)
        self.encode_list_known = self.get_encodings()

        for cl in my_list:
            current_img = cv2.imread(f'{self.path}/{cl}')
            self.images.append(current_img)
            self.class_names.append(os.path.splitext(cl)[0])

        try:
            print("Loading encodings from file...")
            with open(self.encoding_file, 'rb') as f:
                self.encode_list_known, self.class_names = pickle.load(f)
            # with open(self.encoding_file, 'wb') as f:
            #     pickle.dump((self.encode_list_known, self.class_names), f)
            print("Encodings loaded successfully.")
        except FileNotFoundError:
            print("NO ENCODINGS")

    def save_encodings(self):
        self.encode_list_known = self.get_encodings()
        print("Encodings not found. Generating...")
        with open(self.encoding_file, 'wb') as f:
            pickle.dump((self.encode_list_known, self.class_names), f)
        print("Encodings saved to file.")


    def start_sql(self, user, password, database):
        connection = pymysql.connect(
            host='localhost',  
            user=user,  
            password=password,   
            database=database
        )
        # cursor = self.connection.cursor()
        return connection


    def enroll_student(self, id, name, img, connection):
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%Y-%m-%d')

        try:
            with connection.cursor() as cursor:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO student (id, name, time_enrolled, date_enrolled) VALUES (%s, %s, %s, %s);",
                    (id, name, time_str, date_str)
                )
                connection.commit()

                save_path = os.path.join(self.path, f'{id}.jpg')
                cv2.imwrite(save_path, cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                print(f"Saved cropped face to {save_path}")

                self.class_names.append(id)
                self.images.append(img)
                self.name = name
                self.student_id = str(id)
        except pymysql.MySQLError as err:
                print(f"Database error: {err}")

    
    def mark_attendance(self, student_id, connection):
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%Y-%m-%d')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM student WHERE id = %s",
                    (student_id)
                )
                name = cursor.fetchone()

                if name is not None:
                    self.student_id = student_id
                    self.name = name[0]
                    cursor.execute(
                        "INSERT INTO attendance (student_id, time_attended, date_attended) VALUES (%s, %s, %s)",
                        (student_id, time_str, date_str)
                    )
                    connection.commit()
                    print(f"Marked attendance for {name} at {time_str} on {date_str}")

        except pymysql.MySQLError as err:
            print(f"Database error: {err}")


    def open_webcam(self, name="Webcam", width=1280, height=720, webcam=0):
        stream = cv2.VideoCapture(webcam)

        if not stream.isOpened():
            print(f'Webcam {webcam} is not available')
            return exit()

        cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(name,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # camera will default to nearest available res even if specified
        width = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        scale = 3
        offset = 150

        # mid points
        self.xm = int(width/2)
        self.ym = int(height/2)

        # 2 points to define the center region
        self.x0 = self.xm - offset
        self.y0 = self.ym + offset
        self.x1 = self.xm + offset
        self.y1 = self.ym - offset
        self.dimension = (width * scale, height * scale)
        print("DIMESNION", self.dimension)
        return stream


    def show_webcam(self, img, name="Webcam"):
        resized_img = cv2.resize(img, self.dimension, interpolation=cv2.INTER_AREA)
        cv2.imshow(name, resized_img)


    def crop_center(self, img):
        center_img = img[self.y1:self.y0, self.x0:self.x1]
        center_img = cv2.cvtColor(center_img, cv2.COLOR_BGR2RGB) 
        return center_img

    
    def detect_blur(self, img, threshold=150):
        variance = cv2.Laplacian(img, cv2.CV_64F).var()
        print("VARIANCE", variance)
        return variance < threshold


    def reset(self, connection):
        for item in os.listdir(self.path):
            os.remove(f"{self.path}/{item}")
            print(item)

        try:
            os.remove(self.encoding_file)
        except FileNotFoundError:
            pass

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM attendance")
            cursor.execute("DELETE FROM student")
            connection.commit()


