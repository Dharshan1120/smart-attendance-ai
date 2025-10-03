import cv2
import face_recognition
import pickle
import os
import numpy as np
import time

ENCODINGS_FILE = "encodings.pkl"

def register_user(name):
    # Load existing encodings
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
    else:
        data = {}

    # Check if name is already in DB
    if name in data:
        print(f"[ERROR] The name '{name}' is already registered!")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open camera.")
        return

    print(f"[INFO] Capturing 5 photos for {name}... Look at the camera!")

    user_encodings = []
    count = 0
    popup_message = ""
    popup_time = 0
    POPUP_DURATION = 3.0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, boxes)

        for encoding, (top, right, bottom, left) in zip(encodings, boxes):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            label = "New Face"

            # ---- Check if this face already exists ----
            for existing_name, enc_list in data.items():
                avg_encoding = np.mean(enc_list, axis=0)
                match = face_recognition.compare_faces([avg_encoding], encoding, tolerance=0.5)
                if match[0]:
                    label = existing_name
                    popup_message = f"⚠️ Face already registered as {existing_name}"
                    popup_time = time.time()
                    print(f"[ERROR] Face already registered as {existing_name}")
                    cap.release()
                    cv2.destroyAllWindows()
                    return

            # Capture 5 photos for new user
            if count < 5:
                user_encodings.append(encoding)
                count += 1
                label = f"Captured {count}/5"
                print(f"[INFO] Captured photo {count}/5")
                cv2.waitKey(1000)

            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Show popup if duplicate face
        if popup_message and (time.time() - popup_time) < POPUP_DURATION:
            cv2.putText(frame, popup_message, (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("Register Face", frame)

        if count >= 5:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Registration aborted.")
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    # Save new user
    if len(user_encodings) == 5:
        data[name] = user_encodings
        with open(ENCODINGS_FILE, "wb") as f:
            pickle.dump(data, f)
        print(f"[INFO] {name} registered successfully with 5 encodings!")
    else:
        print("[ERROR] Registration failed. Try again.")

if __name__ == "__main__":
    user_name = input("Enter the user's name: ")
    register_user(user_name)
