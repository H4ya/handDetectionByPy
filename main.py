import cv2
import mediapipe as mp

try:
    # Initialize once (not in loop)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5)
    
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    webcam = cv2.VideoCapture(0)
    
    while webcam.isOpened():
        success, frame = webcam.read()
        if not success:
            print("Ignoring empty camera frame")
            continue
        
        # Performance optimization
        frame.flags.writeable = False
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Prepare for drawing
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Better drawing with styles
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks)
                
                # Example: Access individual landmarks
                h, w, _ = frame.shape
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                cv2.circle(frame, (wrist_x, wrist_y), 10, (255, 0, 0), -1)
        
        # Mirror effect
        frame = cv2.flip(frame, 1)
        
        # Show FPS
        fps = webcam.get(cv2.CAP_PROP_FPS)
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), #message, point
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2) #font, size, color, thickness
        
        cv2.imshow("Hand Landmark Detection", frame)
        
        if ((cv2.waitKey(1) & 0xFF == ord("q")) |( cv2.waitKey(1) & 0xFF == ord("Q"))):
            break

except Exception as e:
    print(f"Error occurred: {str(e)}")

finally:
    webcam.release()
    cv2.destroyAllWindows()
    hands.close()  # Don't forget to close MediaPipe resources