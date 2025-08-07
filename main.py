import cv2
import mediapipe as mp
import numpy as np
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc


#####################Functions!!#####################

def isFurther (fing1ID,fing2ID): #takes the **ID** of 2 fingers check if fing1 is further than fing2 according to the x-axis 
    if(type(fing1ID) == int and type(fing2ID) == int ): #optimize check type
        if ( lary[fing2ID][1] - lary[fing1ID][1] < 0 ):
            return True
        else: 
            return False
    else:
        return 'Error'

#I think I could use it nested for more than 2 fingers checking note: as max function max(1,max(2,3))
def isHigher (fing1ID,fing2ID):  #takes the **ID** of 2 fingers check if fing1ID is higher than fing2ID according to the y-axis 
    if(type(fing1ID) == int and type(fing2ID) == int ): #optimize check type
        if ( lary[fing1ID][2] - lary[fing2ID][2] > 0 ):
            return True
        else: 
            return False
    else:
        return 'Error'

def sameHand (fing1ID, fing2ID): #takes the fingers then return true if same(same hand)/false if different or Error for wrong input type
## gly: change it so the function takes the id 
    if(type(fing1ID)==int and type(fing2ID)== int ):#optimize check type 
        if ( lary[fing1ID][0] - lary[fing2ID][0] == 0 ): #my genius solution to check if it's the same hand
            return True
        else: return False
    else: return 'Error'

def sameCoord(point1ID,point2ID,coord,maxDif):
    if ((lary[point1ID][coord]- lary[point2ID][coord]) in range(-int(maxDif/2),int(maxDif/2))):
        return True
    else: return False


def pointRange(id,coord,min,max):
    if ( lary[id][coord] >= min and lary[id][coord] <= max ):
        return True
    else: False

########(|Upcoming functions|)##########
#// def sameX (id1,id2,range or allowed difference)
#// def sameY() ^^ 
#// def range(id,{x/y/z},min,max) 
#
#
#

#############<(_The-Code_)>############# 

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(0)

try:
    
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

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
                lary = np.zeros((21, 4))  #def lary [dir, x, y, z] for each landmark
                for id, landmark in enumerate(hand_landmarks.landmark):
                    lary[id] = [
                        dir,  # direction (0=left | 1=right) 
                        int(landmark.x * w), # x coordinate #note: it used to be w- etc (idk y)
                        int(landmark.y * h),  # y coordinate
                        float(landmark.z * w), # z coordinate
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
                    if id > 4 and id % 4 == 0 :
                        #if((lary[id][1]-lary[id-2][1]) in range(-10,10))and (lary[id][3]<=0 and lary[id][3]>= -30) :
                        if sameCoord(id,id-2,1,20) and pointRange(id,3,-30,0) :
                            cv2.circle(frame,(int(lary[id][1]),int(lary[id][2])),2,(25,25,20),3,0,0)
                            #if ((lary[4][1] - lary[4-1][1]) in range (-3,3)) and lary[4][3] 
                    ''' 
                    # the "OK" gesture detection
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
                            '''
                    #if id != 0 and id %4 ==0:

                #if ((lary[12][1]-lary[0][1] in range (-5,5)) and (lary[12][0]-lary[9][0]==0) and (lary[6][2]< lary[9][2] )): fool = True
                if sameHand(4,8): 
                    hand = lary[8][0]
                    dist_y = lary[4][2]-lary[8][2] #should be positive
                    dist_yP = float(dist_y/170) #the percentage from 0 to 1
                    if hand == 0: # left for vol ctrl
                        if(isFurther(4,8)):
                            if (dist_yP<= .08):
                                dist_yP = 0 
                            elif (dist_yP >= .99):
                                dist_yP = 1
                            # needed it to manage the abnormal values (negative or over the limit 170)
                            volume.SetMasterVolumeLevelScalar(dist_yP, None)
                    if hand == 1: # right for brightness ctrl
                        if(isFurther(8,4)):
                            if (dist_yP<= .08):
                                dist_yP = 0 
                            elif (dist_yP>= .99): # needed it to manage the abnormal values (negative or over the limit 170)
                                dist_yP = 1
                            sbc.set_brightness(dist_yP*100)
                else: # fingers of different hands, nothing to do
                    hand =-1

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
        
        cv2.putText(
            frame,
            f"volume lvl is : {int(volume.GetMasterVolumeLevelScalar()*100)}%", 
            (15, 80),
            cv2.FONT_HERSHEY_DUPLEX, 
            0.8, 
            (211, 0, 0), 
            1
        )
        cv2.putText(frame,f"brightness lvl is : {(sbc.get_brightness())}%", 
            (15, 130),
            cv2.FONT_HERSHEY_DUPLEX, 
            0.8, 
            (211, 0, 0), 
            1
        )
        #if fool :
        #    break
        cv2.imshow("Hand Landmarks", frame)
        if (cv2.waitKey(1) and 0xFF == ord('q')) or ( cv2.waitKey(1) and 0xFF == ord('Q')):
            break

finally:
    webcam.release()
    cv2.destroyAllWindows()
    hands.close()




