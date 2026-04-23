import psutil
import pyautogui
import asyncio
import cv2, time
import numpy as np
import mediapipe as mp
from datetime import datetime
from collections import Counter
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#import myfunctionsfile as mff

#####################Functions!!#####################

def coordTranslate(coord):
    if 'x' == coord: coord = 1 
    elif 'y' == coord: coord = 2
    elif 'z' == coord: coord = 3
    elif not isinstance(coord, int):
        return TypeError(f"Expected int, got {type(coord).__name__}")
    return coord

def typeIsInt(x):
    if not isinstance(x,int) :
        raise TypeError(f"Expected int, got {type(x).__name__}")
    return True

def checkType(x, y, expected_type):
    if not isinstance(x, expected_type) or not isinstance(y, expected_type):
        raise TypeError(f"Expected both {expected_type.__name__}, got {type(x).__name__} and {type(y).__name__}")
    return True

def isFurther (id1,id2): #takes the **ID** of 2 fingers check if fing1 is further than fing2 according to the x-axis 
    if checkType(id1,id2,int):
        if ( lary[id2][1] - lary[id1][1] < 0 ):
            return True
        else: 
            return False

# I can use it nested for more than 2 fingers checking note: as max function max(1,max(2,3))
def isHigher (id1,id2):  #takes the **ID** of 2 fingers check if id1 is higher than id2 according to the y-axis 
    if(typeIsInt(id1) and typeIsInt(id2)): 
        if ( lary[id1][2] - lary[id2][2] > 0 ):
            return True
        else: 
            return False

def sameHand (id1, id2): #takes the fingers then return true if same(same hand)/false if different or Error for wrong input type
    if(typeIsInt(id1) and typeIsInt(id2)): 
        if ( lary[id1][0] - lary[id2][0] == 0 ): #my genius solution to check if it's the same hand
            return True

def sameCoord2(id1,id2,coord,maxDif):
    coord = coordTranslate(coord)
    if ((lary[id1][coord]- lary[id2][coord]) in range(-int(maxDif/2),int(maxDif/2))):
        return True
    else: return False

def sameCoord(ids, coord, maxDif): #ids can contain 1 or more id as a list
    coord = coordTranslate(coord)
    # Check all pairs
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if abs(lary[ids[i]][coord] - lary[ids[j]][coord]) > maxDif / 2:
                return False
    return True

def pointCoordRange(id,coord,min,max):
    coord = coordTranslate(coord)
    if ( lary[id][coord] >= min and lary[id][coord] <= max ):
        return True
    else: False

########(|Upcoming functions|)##########
#// def sameX (id1,id2,range or allowed difference)
#// def sameY() ^^ 
#// def range(id,{x/y/z},min,max) 
# create a window for warning?
# close when 90% of screen is black
# show battery percentage

def showKeyboard(w,h):

    #cv2
    return "mao"


#############<(_The-Code_)>############# 


    ### <(_Important-Variables_)> ### 
fbs = 30
h = 720 # 720
w = 720 # 1280
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.9, min_tracking_confidence=0.9)
mp_drawing = mp.solutions.drawing_utils
webcam = cv2.VideoCapture(0) # 0 for laptop cam # 1 for phone 
#webcam.set(cv2.CAP_PROP_FRAME_HEIGHT,h) #height
#webcam.set(cv2.CAP_PROP_FRAME_WIDTH,w) #width
#webcam.set(cv2.CAP_PROP_FPS,fbs) #FPS
finalMSG = None
savedFrame = None
screenShot = None
io = 0
key= cv2.waitKey(1)
battery = psutil.sensors_battery()
fileObject = open("outputFile.txt", "r") #read the file
if (fileObject.readline().strip() == str(datetime.now().date())): #if file is from the same date don't overwrite
    fileObject = open("outputFile.txt", "a") # Open for writing, **WON'T** overwrite (append)
else:
    fileObject = open("outputFile.txt", "w") # Open for writing, **WILL** overwrite (write)
    fileObject.write(str(datetime.now().date())+'\n')
startTime = time.time()
endTime = None

try:

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    fool = True
    is_black = False
    prev_frame_time = 0

    while not is_black and fool and webcam.isOpened():
        success, frame = webcam.read()
        if not success:
            continue
            
        # Flip frame
        frame = cv2.flip(frame, 1)
        thumbsUp = "No thumbs |:"
        #cv2.waitKey(1) if we want a delay

        # Process frame
        h, w, _ = frame.shape
        cv2.putText(frame, f", h= {h}, w= {w} " , (130, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2, cv2.LINE_AA)

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
                    mp_drawing.DrawingSpec(color=(0,0,190), thickness=2),
                    mp_drawing.DrawingSpec(color=(225,225,225), thickness=1),
                )
                
                label = handedness.classification[0].label
                dir = 1 if label == "Right" else 0
                # Store landmarks with direction
                lary = np.zeros((21, 4))  #def lary [dir, x, y, z] for each landmark
                for id, landmark in enumerate(hand_landmarks.landmark):
                    lary[id] = [
                        dir,  # direction ( 0=left | 1=right ) 
                        int(landmark.x * w), # x coordinate #note: it used to be w- etc (idk y)
                        int(landmark.y * h),  # y coordinate
                        float(landmark.z * w), # z coordinate
                    ]
                    
                    # Display fingertip coordinates
                    if id % 4 == 0:
                        cv2.putText(
                            frame,
                            f"P<{dir}>{id}({lary[id][1]},{lary[id][2]},{round(lary[id][3],3)})", 
                            (int(lary[id][1]), int(lary[id][2])),  # Position at landmark
                            cv2.FONT_HERSHEY_DUPLEX, 
                            0.4, 
                            (211, 51, 51),
                            1
                        )
                    if dir == 0: #the shut down process
                        NumOfStraightFingers = 0
                        for i in range (8,21,4):
                            if sameCoord2(i,i-2,'x',15) and pointCoordRange(i,3,-30,30) : #if all fingers but the thumb are almost straight
                                cv2.circle(frame,(int(lary[i][1]),int(lary[i][2])),2,(25,25,20),3,0,0)
                                NumOfStraightFingers  += 1
                                continue
                            else:
                                NumOfStraightFingers=0
                        if NumOfStraightFingers == 4 and sameCoord2(4,3,2,6) and isFurther(3,4):   #if thumb is front and horizontal
                                    cv2.putText(
                                        frame,
                                        f"STOPPING THE PROGRAM ", 
                                        (int(lary[0][1]), int(lary[2][2])),  
                                        cv2.FONT_HERSHEY_DUPLEX, 
                                        1, 
                                        (0, 0,225), 
                                        0
                                    )
                                    savedFrame = frame
                                    fool = False
                                    break
                    # if ( 0 == dir and isHigher(4,3) and isFurther(8,7) and sameCoord(4,2,)) :
                    #    break

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
                # 
                #

                
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
                            if (dist_yP<= .06):
                                dist_yP = 0 
                            elif (dist_yP>= .99): # needed it to manage the abnormal values (negative or over the limit 170)
                                dist_yP = 1
                            sbc.set_brightness(dist_yP*100)
                else: # fingers of different hands, nothing to do
                    hand =-1

                # Thumb state detection
                avg_x = int((lary[4][1] + lary[3][1] )/2)
                if ((lary[8][1]-lary[8+1][1] in range(-60,60))):
                    if (avg_x in range(int(lary[4][1]-15), int(lary[4][1]+15)) and lary[4][2] < lary[3][2]):
                        thumbsUp = "Thumbs UP :D"
                        
                    elif ((avg_x in range(int(lary[4][1]-15), int(lary[4][1]+15)) and lary[4][2] > lary[3][2])):
                        thumbsUp = "Thumbs down D:"
                        
            # Display thumb status
                
                if dir == 1 and thumbsUp =="Thumbs UP :D":
                    pyautogui.press('k')
                    
                    '''
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"like_screenshot_{timestamp}.jpg"
                    cv2.putText(
                        frame,
                        f"say cheeeese! x{io}", 
                        (15, 300),
                        cv2.FONT_HERSHEY_DUPLEX, 
                        2, 
                        (211, 0, 0), 
                    )
                    #screenShot = frame
                    #cv2.imwrite(f'shots\cheeeese{filename}.jpg', screenShot)
                    #io+=1
                    '''
                    #time.perf_counter
                    #time.sleep(10)
                    
                    
                    
                ''' if dir == 0:
                        cv2.putText(
                        frame,
                        f"{thumbsUp} in the Left hand", 
                        (15, 110),
                        cv2.FONT_HERSHEY_DUPLEX, 
                        0.8,
                        (211, 0, 0),
                        1
                    )'''
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps) # Convert to integer for display
        cv2.putText(frame, f"{str(fps)}FPS" , (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2, cv2.LINE_AA)
        cv2.putText(
            frame,
            "Click 'Q' to Exit", 
            (430, 450),
            cv2.FONT_HERSHEY_DUPLEX, 
            0.65,
            (225,225,225),
            1
        )
        if battery is not None:
            percentage = battery.percent
            cv2.putText(
            frame,
            f"Battery Percentage: {percentage}%", 
            (15, 180),
            cv2.FONT_HERSHEY_PLAIN, 
            1.5, 
            (171, 0, 0), 
            1
        )
        else:
            cv2.putText(
            frame,
            "No battery found or battery information unavailable.", 
            (15, 180),
            cv2.FONT_HERSHEY_PLAIN, 
            1, 
            (171, 0, 0), 
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
        cv2.imshow("Hand Landmarks", frame)
        #if (cv2.waitKey(1) and 0xFF == ord('q')) or ( cv2.waitKey(1) and 0xFF == ord('Q')) :
        if key==ord("q"):
            cv2.waitKey(500)
            finalMSG = "The program was shut down by the user's input"
            break
        if is_black:
            finalMSG = "The program was shut down by a black frame"
            break
    cv2.waitKey(500) #changed it from time.sleep(0.9) to waitKey
    finalMSG = "The program was shut down by the user's gesture"
    
except:
    finalMSG = "The program was shut down by an exception"
finally:
    endTime = time.time()
    fileObject.write(
    "---------------"
    f"\nThis file was:\n"
    f"open at {time.ctime(startTime)}\n"
    f"close at {time.ctime(endTime)}\n"
    f"total usage in minutes = {round((endTime-startTime)/60,2)}\n"
    f"the frame h = {h}, w = {w}\n"
    f"with {fps} FPS\n"
    f"the final msg was '{finalMSG}'\n---------------\n")
    cv2.imwrite('theLastFrame.jpg', savedFrame)
    webcam.release()
    cv2.destroyAllWindows()
    hands.close()
    fileObject.close() # Important to close the file



