import cv2
import mediapipe as mp
import numpy as np
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
def set_volume(level):  # level: float between 0.0 and 1.0
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level, None)
    cv2.putText(
        frame,
        f"volume is : {int(dist_yP*100)}%", 
        (15, 80),
        cv2.FONT_HERSHEY_DUPLEX, 
        0.8, 
        (211, 0, 0), 
        1
    )

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(0)

try:

    while webcam.isOpened():
        success, frame = webcam.read()
        if not success:
            continue
            
        # Flip frame
        frame = cv2.flip(frame, 1)
        thumbsUp = "No thumbs |:"

        # Process frame
        frame.flags.writeable = False
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame.flags.writeable = True
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_idx, (hand_landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,0,180), thickness=2),
                    mp_drawing.DrawingSpec(color=(225,225,225), thickness=1),
                )
                
                h, w, _ = frame.shape
                label = handedness.classification[0].label
                dir = 1 if label == "Right" else 0
                
                # Store landmarks with direction
                lary = np.zeros((21, 4))  # [dir, x, y, z] for each landmark
                for id, landmark in enumerate(hand_landmarks.landmark):
                    lary[id] = [
                        dir,  # direction (0=left, 1=right)
                        int(landmark.x * w),  # x coordinate
                        int(landmark.y * h),  # y coordinate
                        float(landmark.z * w),# z coordinate
                    ]
                    
                    # Display fingertip coordinates
                    if id % 4 == 0:
                        cv2.putText(
                            frame, 
                            f"P{id}({lary[id][1]},{lary[id][2]},{round(lary[id][3],3)})", 
                            (int(lary[id][1]), int(lary[id][2])),  # Position at landmark
                            cv2.FONT_HERSHEY_DUPLEX, 
                            0.4, 
                            (211, 51, 51), 
                            1
                        )
                    
                    # OK gesture detection
                    if id == 8:  # Only check once per frame
                        okZ = lary[4][3] - lary[8][3]
                        okX = lary[8][1] - lary[4][1]
                        okY = lary[4][2] - lary[8][2]
                        
                        if (okY <= 23) and (okY >= 0) and (okX in range(-7,8)) and (okZ >= -3) and (okZ <= 35):
                            cv2.putText(
                                frame,
                                "Hello Genius!",
                                (20, 40),
                                cv2.FONT_HERSHEY_DUPLEX, 
                                1.3,
                                (211, 51, 51),
                                1
                            )
                #distances
                dist_x = lary[8][1]-lary[4][1] #should be positive
                dist_y = lary[4][2]-lary[8][2] #should be positive too 
                dist_yP = float(dist_y/170) #the percentage from 0 to 1
                if (dist_yP<=0.11):
                    dist_yP =0 
                elif (dist_yP>=1):
                    dist_yP = 1
                    # needed it to manage the abnormal values (negative or over the limit 170)

                if(dist_x <=0):
                    set_volume(dist_yP)

                # Thumb state detection
                '''avg_x = int((lary[4][1] + lary[3][1] )/2)
                if ((lary[8][1]-lary[8+1][1] in range(-60,60))):
                    if (avg_x in range(int(lary[4][1]-15), int(lary[4][1]+15)) and lary[4][2] < lary[3][2]):
                        thumbsUp = "Thumbs UP :D"
                        
                    elif ((avg_x in range(int(lary[4][1]-15), int(lary[4][1]+15)) and lary[4][2] > lary[3][2])):
                        thumbsUp = "Thumbs down D:"
                        
            # Display thumb status
                if dir == 1:
                    cv2.putText(
                        frame,
                        f"{thumbsUp} in the Right hand", 
                        (15, 70),
                        cv2.FONT_HERSHEY_DUPLEX, 
                        0.8, 
                        (211, 0, 0), 
                        1
                    )
                if dir == 0:
                    cv2.putText(
                    frame,
                    f"{thumbsUp} in the Left hand", 
                    (15, 110),
                    cv2.FONT_HERSHEY_DUPLEX, 
                    0.8,
                    (211, 0, 0),
                    1
                )'''
            
        cv2.putText(
            frame,
            "Click 'Q' to Exit", 
            (430, 450),
            cv2.FONT_HERSHEY_DUPLEX, 
            0.65,
            (225,225,225),
            1
        )
    
        cv2.imshow("Hand Landmarks", frame)
        if ((cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.waitKey(1) & 0xFF == ord('Q'))):
            break

finally:
    webcam.release()
    cv2.destroyAllWindows()
    hands.close()