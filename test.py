import math
import threading
import time
from collections import deque
import cv2
import mediapipe as mp
import numpy as np
import pyautogui
try:
    import screen_brightness_control as sbc
except ImportError:  # pragma: no cover - optional dependency
    sbc = None

try:
    from pycaw.pycaw import AudioUtilities
except ImportError:  # pragma: no cover - optional dependency
    AudioUtilities = None

class ThreadedCamera:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.ret = False
        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.ret = ret
                    self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is None:
                return self.ret, None
            return self.ret, self.frame.copy()

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        self.running = False
        self.thread.join(timeout=1)
        self.cap.release()


class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.85,
            min_tracking_confidence=0.85,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.frame_history = deque(maxlen=6)
        self.calibrated = False
        self.calibration_samples = []
        self.reference_span = 120.0
        self.reference_distance = 220.0
        self.last_action_time = 0.0
        self.last_gesture = None
        self.stop_requested = False
        self.volume = None
        self._init_audio()

    def _init_audio(self):
        if AudioUtilities is None:
            return
        try:
            device = AudioUtilities.GetSpeakers()
            self.volume = device.EndpointVolume
        except Exception:
            self.volume = None

    def clamp(self, value, low, high):
        return max(low, min(high, value))

    def smooth_landmarks(self, landmarks, width, height):
        if not landmarks:
            return []

        point_list = []
        for landmark in landmarks:
            if hasattr(landmark, "x") and hasattr(landmark, "y"):
                point_list.append((int(landmark.x * width), int(landmark.y * height)))
            elif isinstance(landmark, (tuple, list)) and len(landmark) >= 2:
                point_list.append((int(landmark[0]), int(landmark[1])))
            else:
                point_list.append((0, 0))

        self.frame_history.append(point_list)
        if len(self.frame_history) < 2:
            return point_list

        smoothed = []
        for idx in range(len(point_list)):
            xs = [frame[idx][0] for frame in self.frame_history]
            ys = [frame[idx][1] for frame in self.frame_history]
            smoothed.append((int(sum(xs) / len(xs)), int(sum(ys) / len(ys))))
        return smoothed

    def update_calibration(self, landmarks, width, height):
        if not self.calibrated and landmarks:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
            self.calibration_samples.append(distance)
            if len(self.calibration_samples) >= 20:
                self.reference_span = float(sum(self.calibration_samples) / len(self.calibration_samples))
                self.reference_distance = max(self.reference_span * 1.75, 140.0)
                self.calibrated = True

    def _hand_label(self, handedness):
        return handedness.classification[0].label

    def _is_stop_sign(self, landmarks):
        if len(landmarks) < 21:
            return False
        # Straight fingers: index, middle, ring, pinky roughly aligned
        finger_ids = [8, 12, 16, 20]
        straight = True
        for finger_id in finger_ids:
            if abs(landmarks[finger_id][1] - landmarks[8][1]) > 25:
                straight = False
                break
        thumb = landmarks[4]
        wrist = landmarks[0]
        thumb_is_forward = abs(thumb[0] - wrist[0]) < 30 and thumb[1] < wrist[1]
        return straight and thumb_is_forward

    def _is_thumbs_up(self, landmarks):
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        thumb_index_gap = abs(thumb_tip[0] - index_tip[0])
        thumb_y_gap = thumb_tip[1] - index_tip[1]
        return thumb_index_gap < 35 and thumb_y_gap < -20

    def _normalize_value(self, sample, reference):
        if reference <= 0:
            return 0.0
        value = self.clamp(sample / reference, 0.0, 1.0)
        return round(value, 3)

    def process_frame(self, frame):
        height, width, _ = frame.shape
        working = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(working)

        annotated = frame.copy()
        cv2.putText(annotated, "Open both hands to calibrate", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 200, 0), 2)

        if not self.calibrated:
            cv2.putText(annotated, "Calibrating...", (10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (0, 200, 0), 2)

        if results.multi_hand_landmarks and results.multi_handedness:
            hand_maps = []
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                landmark_points = []
                for landmark in hand_landmarks.landmark:
                    landmark_points.append((int(landmark.x * width), int(landmark.y * height)))
                hand_maps.append((self._hand_label(handedness), landmark_points, hand_landmarks))

            for label, landmarks, hand_landmarks in hand_maps:
                smoothed = self.smooth_landmarks(landmarks, width, height)
                self.mp_drawing.draw_landmarks(
                    annotated,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 0, 190), thickness=2),
                    self.mp_drawing.DrawingSpec(color=(225, 225, 225), thickness=1),
                )

                if not self.calibrated:
                    self.update_calibration(smoothed, width, height)
                    if self.calibrated:
                        cv2.putText(annotated, "Calibration complete", (10, 90), cv2.FONT_HERSHEY_PLAIN, 1, (0, 200, 0), 2)

                if self.calibrated:
                    thumb_tip = smoothed[4]
                    index_tip = smoothed[8]
                    wrist = smoothed[0]
                    distance = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
                    normalized_distance = self._normalize_value(distance, self.reference_span)

                    if label.lower() == "left" and self._is_stop_sign(smoothed):
                        cv2.putText(annotated, "Stopping program", (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                        self.stop_requested = True
                    else:
                        if label.lower() == "left":
                            if time.time() - self.last_action_time > 0.15:
                                if self.volume is not None:
                                    self.volume.SetMasterVolumeLevelScalar(self.clamp(1.0 - normalized_distance, 0.0, 1.0), None)
                                self.last_action_time = time.time()
                            cv2.putText(annotated, f"Volume: {int(self.clamp(1.0 - normalized_distance, 0.0, 1.0) * 100)}%", (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                        elif label.lower() == "right":
                            if time.time() - self.last_action_time > 0.15:
                                if sbc is not None:
                                    sbc.set_brightness(self.clamp(normalized_distance * 100, 0.0, 100.0))
                                self.last_action_time = time.time()
                            cv2.putText(annotated, f"Brightness: {int(self.clamp(normalized_distance * 100, 0.0, 100.0))}%", (10, 150), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

                    if self._is_thumbs_up(smoothed) and label.lower() == "right":
                        if time.time() - self.last_action_time > 0.35:
                            pyautogui.press("k")
                            self.last_action_time = time.time()
                            self.last_gesture = "thumbs_up"
                        cv2.putText(annotated, "Thumbs up detected", (10, 180), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1)

                    # Draw simple landmarks and helper lines
                    cv2.circle(annotated, thumb_tip, 6, (255, 0, 0), -1)
                    cv2.circle(annotated, index_tip, 6, (0, 255, 0), -1)
                    cv2.line(annotated, thumb_tip, index_tip, (255, 255, 255), 1)
                    cv2.putText(annotated, f"Hand: {label}", (thumb_tip[0], thumb_tip[1] - 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

        return annotated


def main():
    camera = ThreadedCamera(0)
    controller = GestureController()

    if not camera.isOpened():
        print("Unable to open camera")
        return

    print("Starting improved hand-control demo")
    print("Hold your hands in view to calibrate the gesture thresholds")

    try:
        while not controller.stop_requested:
            success, frame = camera.read()
            if not success or frame is None:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            annotated = controller.process_frame(frame)
            cv2.imshow("Improved Hand Controls", annotated)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as exc:
        print(f"Runtime error: {exc}")
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
