import os
import time

def clear_console():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

while True:
    clear_console()
    print()
    print("⋆｡°✩  Visual Attendance System ⋆｡°✩")
    print("             By Group 5 ")
    print()
    print("1. Enroll")
    print("2. Attendance")
    print("3. View Database (Unavailable ;-;)")
    print("4. Reset")
    print("5. Test Gate")
    print("6. Exit")
    print()

    try:
        user_input = int(input("Enter input: "))
    except ValueError:
        continue

    if user_input == 1:
        exec(open("enrollment2.py").read())
    if user_input == 2:
        exec(open("attendance2.py").read())
    if user_input == 3:
        pass
    if user_input == 4:
        exec(open("reset.py").read())
        message = "RESETTING"
        for _ in range(3):
            clear_console()
            message += '.'
            print(message)
            time.sleep(2)

    if user_input == 5:
        exec(open("gate_test.py").read())
        message = "TESTING GATE"
        for _ in range(3):
            clear_console()
            message += '.'
            print(message)
            time.sleep(2)
    if user_input == 6:
        clear_console()
        print("GOODBYE")
        break
