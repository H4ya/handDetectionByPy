import cv2
import mediapipe as mp

sol = mp.solutions
handi = sol.hands
drawing = sol.drawing_utils

mp_hands =0 

webcam = cv2.VideoCapture(1)
# 0 = computer device
# 1 = 2nd cam
while webcam.isOpened():
        success, frame = webcam.read()
        
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results = handi.Hands(max_num_hands=3, min_detection_confidence =0.7).process(frame)
        frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        #if not success:
        #    break  
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                drawing.draw_landmarks(frame,hand_landmarks ,connections = handi.HAND_CONNECTIONS)

        cv2.imshow("my Cam Frame", frame)

        # Check if window is closed or 'q' is pressed

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

webcam.release()
cv2.destroyAllWindows()
