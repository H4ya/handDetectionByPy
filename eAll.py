import cv2
import time
import numpy as np
from scipy.spatial import distance
import mediapipe as mp

# ==================== Validation Settings ====================
max_duration = 5.0      # Maximum allowed time for gesture (seconds)
min_duration = 2.0      # Minimum required time
min_speed = 0.1         # Minimum acceptable speed
max_speed = 0.5         # Maximum acceptable speed
sync_threshold = 0.2    # Allowed time difference between hands (200ms)

# ==================== Timing Variables ====================
gesture_start_time = None
is_gesture_active = False

# ==================== Motion Analysis Variables ====================
previous_left_landmarks = None
previous_right_landmarks = None
previous_time = None

# ==================== Synchronization Variables ====================
left_hand_times = []
right_hand_times = []

# ==================== Timer Functions ====================
def start_timer():
    global gesture_start_time, is_gesture_active
    gesture_start_time = time.time()
    is_gesture_active = True
    print("Timer started")

def check_timeout():
    global gesture_start_time, is_gesture_active
    if not is_gesture_active:
        return False
    elapsed = time.time() - gesture_start_time
    return elapsed > max_duration

def check_minimum_time():
    global gesture_start_time
    if gesture_start_time is None:
        return False
    elapsed = time.time() - gesture_start_time
    return elapsed >= min_duration

def reset_timer():
    global gesture_start_time, is_gesture_active
    gesture_start_time = None
    is_gesture_active = False
    print("Timer reset")

# ==================== Speed Analysis Functions ====================
def calculate_velocity(current_landmarks, previous_landmarks, time_delta):
    if previous_landmarks is None or time_delta == 0:
        return 0.0
    
    # Calculate total movement distance
    total_distance = 0.0
    for prev, curr in zip(previous_landmarks, current_landmarks):
        total_distance += distance.euclidean(prev[:2], curr[:2])  # Use only x,y coordinates
    
    velocity = total_distance / time_delta
    return velocity

def is_valid_speed(velocity):
    return min_speed <= velocity <= max_speed

# ==================== Synchronization Functions ====================
def record_hand_movement(hand_type, timestamp):
    global left_hand_times, right_hand_times
    
    if hand_type == "Left":
        left_hand_times.append(timestamp)
    else:
        right_hand_times.append(timestamp)

def check_synchronization():
    global left_hand_times, right_hand_times
    
    if len(left_hand_times) < 2 or len(right_hand_times) < 2:
        return False
    
    # Calculate time differences between movements
    left_diffs = np.diff(left_hand_times)
    right_diffs = np.diff(right_hand_times)
    
    # Check synchronization
    sync_errors = []
    for left_diff, right_diff in zip(left_diffs, right_diffs):
        time_error = abs(left_diff - right_diff)
        sync_errors.append(time_error)
    
    if len(sync_errors) == 0:
        return False
        
    avg_error = np.mean(sync_errors)
    return avg_error <= sync_threshold

def reset_sync_data():
    global left_hand_times, right_hand_times
    left_hand_times = []
    right_hand_times = []
    print("Synchronization data reset")

# ==================== Main Validation Function ====================
def validate_gesture(left_hand_landmarks, right_hand_landmarks):
    global is_gesture_active, gesture_start_time, previous_left_landmarks, previous_right_landmarks, previous_time
    
    current_time = time.time()
    
    # Check if both hands are present
    if left_hand_landmarks is None or right_hand_landmarks is None:
        reset_timer()
        reset_sync_data()
        return False, "Please use both hands"
    
    # Start timer if not already started
    if not is_gesture_active:
        start_timer()
        reset_sync_data()
        previous_time = current_time
        previous_left_landmarks = left_hand_landmarks
        previous_right_landmarks = right_hand_landmarks
        return False, "Start moving..."

    # Check for timeout
    if check_timeout():
        reset_timer()
        reset_sync_data()
        return False, "Time limit exceeded"
    
    # Calculate velocity
    time_delta = current_time - previous_time
    left_velocity = calculate_velocity(left_hand_landmarks, previous_left_landmarks, time_delta)
    right_velocity = calculate_velocity(right_hand_landmarks, previous_right_landmarks, time_delta)
    
    # Update previous data
    previous_left_landmarks = left_hand_landmarks
    previous_right_landmarks = right_hand_landmarks
    previous_time = current_time
    
    # Check speed validity
    if not is_valid_speed(left_velocity):
        return False, "Left hand speed not suitable"
    
    if not is_valid_speed(right_velocity):
        return False, "Right hand speed not suitable"
    
    # Record hand movements for synchronization check
    record_hand_movement("Left", current_time)
    record_hand_movement("Right", current_time)
    
    # Check synchronization
    if not check_synchronization():
        return False, "Movements not synchronized"
    
    # Check if minimum time is met
    if check_minimum_time():
        reset_timer()
        reset_sync_data()
        return True, "Gesture successful! ✓"
    
    return False, "Continue moving..."

# ==================== Visual Feedback Function ====================
def add_visual_feedback(frame, is_valid, message):
    global gesture_start_time, is_gesture_active
    
    # Time indicator
    if is_gesture_active and gesture_start_time:
        elapsed = time.time() - gesture_start_time
        progress = min(elapsed / max_duration, 1.0)
        cv2.rectangle(frame, (10, 50), (210, 70), (100, 100, 100), -1)
        cv2.rectangle(frame, (10, 50), (10 + int(200 * progress), 70), 
                    (0, 255, 0), -1)
        cv2.putText(frame, f"Time: {elapsed:.1f}s/{max_duration}s", (220, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Status indicator
    status_color = (0, 255, 0) if is_valid else (0, 0, 255)
    cv2.putText(frame, f"Status: {message}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    # User instructions
    cv2.putText(frame, "Move both hands together for 2-5 seconds", (10, 400), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Speed guidelines
    cv2.putText(frame, "Keep speed moderate - not too fast or slow", (10, 430), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

# ==================== Main Function ====================
def main():
    # Setup MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    print("System starting...")
    print("Instructions: Move both hands together at moderate speed for 2-5 seconds")
    print("Press ESC to exit")
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Error reading frame")
            continue
        
        # Flip frame horizontally (mirror effect)
        frame = cv2.flip(frame, 1)
        
        # Process image
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        
        left_hand = None
        right_hand = None
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if results.multi_handedness:
                    handness = results.multi_handedness[idx].classification[0].label
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                    
                    if handness == "Left":
                        left_hand = landmarks
                        # Draw left hand landmarks in blue
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=3),
                            mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2))
                    else:
                        right_hand = landmarks
                        # Draw right hand landmarks in red
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3),
                            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2))
        
        # Validate gesture
        is_valid, message = validate_gesture(left_hand, right_hand)
        
        # Add visual feedback
        add_visual_feedback(frame, is_valid, message)
        
        # Display frame
        cv2.imshow('Gesture Validation System - Press ESC to exit', frame)
        
        # Exit on ESC key
        if cv2.waitKey(5) & 0xFF == 27:
            break
    
    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()
    print("System stopped")

# ==================== Run Program ====================
if __name__ == "__main__":
    main()