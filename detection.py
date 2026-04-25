import cv2
import mediapipe as mp
import time
import math
import requests
import smtplib
from email.message import EmailMessage
import datetime
import os
import numpy as np
import face_recognition

# ================= CONFIG ================= #

NTFY_TOPIC = "help"
NTFY_BASE_URL = "https://ntfy.sh"
POLICE_CONTACT = "9876990060"

SENDER_EMAIL = 'ananyanov22@gmail.com'
SENDER_PASSWORD = 'ouckiduxyghfohor' 
RECIPIENT_EMAIL = 'ananyaaloo22@gmail.com'

ALERT_COOLDOWN_SECONDS = 300
CONSECUTIVE_DETECTION_FRAMES = 45

KNOWN_FACES_DIR = "known_faces"
UNKNOWN_PERSON_NAME = "Unknown Person"

# ================= LOAD FACES ================= #

known_face_encodings = []
known_face_names = []

def load_known_faces():
    print("Loading known faces...")

    if os.path.exists(KNOWN_FACES_DIR):
        for filename in os.listdir(KNOWN_FACES_DIR):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                try:
                    name = os.path.splitext(filename)[0]
                    image = face_recognition.load_image_file(os.path.join(KNOWN_FACES_DIR, filename))
                    encodings = face_recognition.face_encodings(image)

                    if encodings:
                        known_face_encodings.append(encodings[0])
                        known_face_names.append(name)
                        print(f"Loaded: {name}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

# ================= MEDIAPIPE ================= #

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ================= HELPERS ================= #

def get_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def is_signal_for_help_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

    dist_tip_to_index = get_distance(thumb_tip, index_mcp)
    hand_size = get_distance(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST], thumb_mcp)

    if dist_tip_to_index / hand_size >= 0.35:
        return False

    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]

    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    folded = 0

    for tip_lm in finger_tips:
        tip = hand_landmarks.landmark[tip_lm]
        if get_distance(tip, wrist) < 0.8:
            folded += 1

    return folded == 4

# ================= ALERT ================= #

def send_email_alert(subject, body, image_path=None):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg.set_content(body)

        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename=os.path.basename(image_path))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        print("✅ Email sent!")

    except Exception as e:
        print("❌ Email failed:", e)

# ================= MAIN FUNCTION ================= #

def start_detection():
    load_known_faces()

    cap = cv2.VideoCapture(0)
    gesture_frames = 0
    last_alert_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hand_results = hands.process(rgb)
        gesture_detected = False

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                if is_signal_for_help_gesture(hand_landmarks):
                    gesture_detected = True
                    cv2.putText(frame, "HELP SIGN DETECTED!", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if gesture_detected:
            gesture_frames += 1
        else:
            gesture_frames = 0

        if gesture_frames >= CONSECUTIVE_DETECTION_FRAMES:
            now = time.time()

            if now - last_alert_time > ALERT_COOLDOWN_SECONDS:
                filename = f"alert_{int(now)}.jpg"
                cv2.imwrite(filename, frame)

                send_email_alert(
                    "🚨 HELP ALERT",
                    "Help gesture detected!",
                    filename
                )

                print("🚨 ALERT SENT")
                last_alert_time = now

        cv2.imshow("Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()