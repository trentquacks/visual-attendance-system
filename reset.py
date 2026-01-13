from visual_attendance import VisualAttendance
import os

va = VisualAttendance()

connection = va.start_sql(os.environ.get('SQL_USER'),
                          os.environ.get('SQL_PASS'),
                          'attendance_db')

va.reset(connection)
