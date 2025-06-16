import cv2
import mediapipe as mp
import numpy as np

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
        thumbsUp = "No thumbs |:"

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
                h, w , _ = frame.shape
                lary = np.zeros((21, 3))  # array of 21 rows and 3 cols for hand landmarks
                for id, landmark in enumerate(hand_landmarks.landmark):
                    
                    lary[id] = [int(landmark.x * w), int(landmark.y * h), float(landmark.z * w)]
                    
                    #thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    
                    okZ = lary[4][2] - lary[8][2]
                    if(id%4==0): #يطبع لي اطراف الاصابع والرقم 0
                        cv2.putText(frame, f"P{id}({lary[id][0]},{lary[id][1]},{round(lary[id][2],2)})", (int(lary[id][0]+10),int(lary[id][1]-10)),
                        cv2.FONT_HERSHEY_DUPLEX, .4, (211,51,51), 1)
                    #    print("\nYour Celsius value is {:0.2f}ºC.\n".format(answer))
                    okX = lary[8][0] - lary[4][0]
                    okY = lary[4][1] - lary[8][1] #functions to see if the ok symbol apply according to x, y & z
                    if lary[4][1] != 0 and lary[8][1] != 0:#todo: re-write it
                        if (okY <= 23) and (okY >= 0) and(okX in range(-1,8)) and (okZ >= -3) and (okZ <= 35):
                            cv2.putText(frame, f"Hello Genius!", (20, 40),
                                        cv2.FONT_HERSHEY_DUPLEX, 1.3, (211,51,51), 1)
                if (int((lary[4][0] + lary[3][0] + lary[2][0])/3) in range (int(lary[4][0]-15),int(lary[4][0]+15)) and lary[4][1]<lary[3][1] and (lary[4][2] in range(-35,11))):
                    thumbsUp = "Thumbs UP :D"
                    
                elif(int((lary[4][0] + lary[3][0] + lary[2][0])/3) in range (int(lary[4][0]-15),int(lary[4][0]+15)) and lary[4][1]>lary[2][1]):
                    thumbsUp = "Thumbs down D:"
                else:
                    thumbsUp = "No thumbs |:"

                    

                        
                            #the rest of points will disappear if thumb tip almost/meets the index tip

                    #if 4 - 8 >=30 

#            for id, landmark in enumerate(hand_landmarks.landmark):
#                    cv2.putText(frame, f"({hand_landmarks.x},{hand_landmarks.y})", (x, y),
#                cv2.FONT_HERSHEY_DUPLEX, 1.3, (211,51,51), 1)

#todo: create a sign to stop the program

        
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
        cv2.putText(frame, f"{thumbsUp}", (15,70),
            cv2.FONT_HERSHEY_DUPLEX, .8, (211,0,0), 1)
        

        cv2.imshow("Hand Landmarks", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit()

finally:
    webcam.release()
    cv2.destroyAllWindows()
    hands.close()