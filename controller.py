# debut du fichier controller.py
import cv2
import face_recognition
import numpy as np
from models import get_all_users
import time

recent_faces = {}
recent_unknown = {}

def register_user_from_file(name, image_file):
    image = face_recognition.load_image_file(image_file)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        from models import add_user
        add_user(name, encodings[0])
        return True
    return False

def register_user_from_frame(name, frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_frame)
    if encodings:
        from models import add_user
        add_user(name, encodings[0])
        return True
    return False

def recognize_faces(frame, tolerance=0.5, scale=0.5, alert_cooldown=5):
    global recent_faces, recent_unknown
    users = get_all_users()
    known_encodings = [u[1] for u in users]
    known_names = [u[0] for u in users]

    small_frame = cv2.resize(frame, (0,0), fx=scale, fy=scale)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    results = []
    alert = False
    current_time = time.time()

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        top = int(top/scale)
        right = int(right/scale)
        bottom = int(bottom/scale)
        left = int(left/scale)

        name = "Inconnu"
        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_idx = np.argmin(distances)
            if distances[best_idx] <= tolerance:
                name = known_names[best_idx]
                if name not in recent_faces or current_time - recent_faces[name] > 10:
                    recent_faces[name] = current_time
            else:
                alert = True
        else:
            alert = True
        results.append(((top,right,bottom,left), name))

    return results, alert
# fin du fichier controller.py