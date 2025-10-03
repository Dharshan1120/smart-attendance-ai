import cv2
import face_recognition
import pickle
import csv
import datetime
import os
import numpy as np
import time
import platform

# For sound notification
if platform.system() == "Windows":
    import winsound

ENCODINGS_FILE = "encodings.pkl"
ATTENDANCE_DIR = "attendance"  # folder to store daily files
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

# Load encodings
with open(ENCODINGS_FILE, "rb") as f:
    data = pickle.load(f)

# Flatten (average the 5 encodings for each user)
known_encodings = []
known_names = []
for name, encodings in data.items():
    avg_encoding = np.mean(encodings, axis=0)
    known_encodings.append(avg_encoding)
    known_names.append(name)

print("[INFO] Smart Attendance system running... Press 'q' to quit.")

cap = cv2.VideoCapture(0)

marked_today = set()  # To avoid duplicate attendance
popup_message = ""    # For showing confirmation
popup_time = 0        # Time when popup appeared

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(rgb_frame, boxes)

    for encoding, (top, right, bottom, left) in zip(encodings, boxes):
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
        name = "Unknown"

        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]

            # Attendance
            today = datetime.date.today().strftime("%Y-%m-%d")
            now = datetime.datetime.now().strftime("%H:%M:%S")
            unique_key = f"{name}_{today}"

            if unique_key not in marked_today:
                # Save into today's CSV file
                attendance_file = os.path.join(ATTENDANCE_DIR, f"{today}.csv")
                file_exists = os.path.isfile(attendance_file)

                with open(attendance_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["Name", "Date", "Time"])
                    writer.writerow([name, today, now])

                marked_today.add(unique_key)

                # Set popup message
                popup_message = f"✅ {name} marked present!"
                popup_time = time.time()
                print(f"[ATTENDANCE] {name} marked present at {now}")

                # Play sound notification
                if platform.system() == "Windows":
                    winsound.Beep(1000, 500)  # frequency=1000Hz, duration=0.5s
                else:
                    os.system('play -nq -t alsa synth 0.5 sine 1000')

            else:
                # ⚠️ Already marked present
                popup_message = f"⚠️ {name} already marked present today"
                popup_time = time.time()
                print(f"[INFO] {name} already marked present today")

        # Draw box + label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    # Show popup for 3 seconds after marking
    if popup_message and (time.time() - popup_time < 3):
        cv2.putText(frame, popup_message, (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

    cv2.imshow("Smart Attendance System", frame)

    # Exit only when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Exiting attendance system.")
        break

cap.release()
cv2.destroyAllWindows()
