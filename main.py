import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(1)

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
                thumb_y, index_y = 0, 0                
                
                h, w , _ = frame.shape
                for id, landmark in enumerate(hand_landmarks.landmark):
            
                    if id == 4 or id == 8 or id == 12 or id == 16 or id == 20:
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)

                        cv2.putText(frame, f"P{id}({x},{y})", (x+10,y-10),
                    cv2.FONT_HERSHEY_DUPLEX, .4, (211,51,51), 1)
                        if id == 4:
                            thumb_y = y
                            thumb_x = x
                        if id == 8:
                            index_y =  y
                            index_x = x
                            okY = thumb_y - index_y
                            okX = thumb_x - index_x
                            if thumb_y != 0 and index_y != 0:#todo: re-write it

                                if ((okY <= 23)and (okY >= 0))and(okX <= 17):
                                    cv2.putText(frame, f"Hello Genius!", (20, 40),
                                                cv2.FONT_HERSHEY_DUPLEX, 1.3, (211,51,51), 1)

                            #the rest of points will disappear if thumb tip almost/meets the index tip

                    #if 4 - 8 >=30 

#            for id, landmark in enumerate(hand_landmarks.landmark):
#                    cv2.putText(frame, f"({hand_landmarks.x},{hand_landmarks.y})", (x, y),
#                cv2.FONT_HERSHEY_DUPLEX, 1.3, (211,51,51), 1)


                
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
                # cv2.putText(frame, f"FPS: {int(webcam.get(cv2.CAP_PROP_FPS))}", (10, 30),
                #             cv2.FONT_HERSHEY_SIMPLEX, 1, (211,51,51), 2)

            #cv2.putText(frame, f"Hello Genius!", (20, 40),
            #cv2.FONT_HERSHEY_DUPLEX, 1.3, (211,51,51), 1)
            
        cv2.imshow("Hand Landmarks", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit()

finally:
    webcam.release()
    cv2.destroyAllWindows()
    hands.close()