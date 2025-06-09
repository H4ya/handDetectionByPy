import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(0)

try:
    while webcam.isOpened():
        success, frame = webcam.read()
        if not success:
            continue
            
        # قلب الإطار أولاً (لتصحيح المرآة)
        frame = cv2.flip(frame, 1)
        
        # معالجة الإطار
        frame.flags.writeable = False
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame.flags.writeable = True
        
        # رسم المعالم والوصلات
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # رسم الوصلات والمعالم
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,0,180), thickness=2),  # لون النقاط
                    mp_drawing.DrawingSpec(color=(225,225,225), thickness=1),  # لون الخطوط

                )
                
                # كتابة الأرقام على النقاط
                #h, w = frame.shape[:2]
                #for id, landmark in enumerate(hand_landmarks.landmark):
                #    # حساب الإحداثيات بعد قلب الصورة
                #    x, y = int(landmark.x * w), int(landmark.y * h)
                #    
                #    # تعديل موقع النص ليكون أعلى النقطة قليلاً
                #    text_y = y - 10 if y > 20 else y + 20
                #    
                #    cv2.putText(frame, str(id), (x, text_y), 
                #                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
        
        # عرض معدل الإطارات
        cv2.putText(frame, f"FPS: {int(webcam.get(cv2.CAP_PROP_FPS))}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        
        cv2.imshow("Hand Landmarks", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    webcam.release()
    cv2.destroyAllWindows()
    hands.close()