import cv2
import mediapipe as mp

handi = mp.solutions.hands
drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(0)
# 0 = computer device
# 1 = 2nd cam
while webcam.isOpened():
    success, frame = webcam.read()
    #if not success:
    #    print("Ignoring empty camera frame.")
    #    continue

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = handi.Hands(max_num_hands=2, min_detection_confidence=0.7).process(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            drawing.draw_landmarks(frame, hand_landmarks, connections=handi.HAND_CONNECTIONS)

    cv2.imshow("my Cam Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

webcam.release()
cv2.destroyAllWindows()
