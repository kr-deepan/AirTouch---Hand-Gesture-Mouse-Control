import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import threading
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_drawing = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
cap = cv2.VideoCapture(0)
cam_width, cam_height = int(cap.get(3)), int(cap.get(4))
ACTIVE_WIDTH, ACTIVE_HEIGHT = cam_width * 0.6, cam_height * 0.6
OFFSET_X, OFFSET_Y = (cam_width - ACTIVE_WIDTH) / 2, (cam_height - ACTIVE_HEIGHT) / 2
ema_x, ema_y = None, None
smoothing_factor = 0.2
base_dead_zone = 12 
max_dead_zone = 20   
last_click_time = 0
click_cooldown = 0.3
click_freeze = False
dragging = False
hold_time = 0.2
frame_lock = threading.Lock()
latest_frame = None
capture_running = True
def capture_frames():
    global latest_frame, capture_running
    while capture_running:
        ret, frame = cap.read()
        if not ret:
            continue
        with frame_lock:
            latest_frame = frame
capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()
while cap.isOpened():
    with frame_lock:
        if latest_frame is None:
            continue
        frame = latest_frame.copy()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            index_finger = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            finger_x, finger_y = index_finger.x * cam_width, index_finger.y * cam_height
            mapped_x = np.interp(finger_x, [OFFSET_X, OFFSET_X + ACTIVE_WIDTH], [0, screen_width])
            mapped_y = np.interp(finger_y, [OFFSET_Y, OFFSET_Y + ACTIVE_HEIGHT], [0, screen_height])
            if ema_x is None or ema_y is None:
                ema_x, ema_y = mapped_x, mapped_y
            else:
                ema_x = smoothing_factor * mapped_x + (1 - smoothing_factor) * ema_x
                ema_y = smoothing_factor * mapped_y + (1 - smoothing_factor) * ema_y
            cursor_x, cursor_y = pyautogui.position()
            move_distance = np.hypot(ema_x - cursor_x, ema_y - cursor_y)
            current_dead_zone = min(base_dead_zone + int(12 / (move_distance + 1)), max_dead_zone)
            if move_distance > current_dead_zone:
                if not click_freeze:
                    pyautogui.moveTo(ema_x, ema_y, _pause=False)
            middle_pinch_distance = np.hypot(middle_tip.x - thumb_tip.x, middle_tip.y - thumb_tip.y)
            ring_pinch_distance = np.hypot(ring_tip.x - thumb_tip.x, ring_tip.y - thumb_tip.y)
            relaxed_distance = np.hypot(index_finger.x - thumb_tip.x, index_finger.y - thumb_tip.y) * 0.6
            current_time = time.time()
            if middle_pinch_distance < relaxed_distance * 0.3:
                if current_time - last_click_time > click_cooldown:
                    last_click_time = current_time
                    click_freeze = True
                    pyautogui.click()
                    time.sleep(0.1)
                    click_freeze = False
            elif ring_pinch_distance < relaxed_distance * 0.3:
                if current_time - last_click_time > click_cooldown:
                    last_click_time = current_time
                    click_freeze = True
                    pyautogui.rightClick()
                    time.sleep(0.1)
                    click_freeze = False
            if middle_pinch_distance < relaxed_distance * 0.3:
                if not dragging:
                    drag_start_time = time.time()
                    while time.time() - drag_start_time < hold_time:
                        if np.hypot(middle_tip.x - thumb_tip.x, middle_tip.y - thumb_tip.y) > relaxed_distance * 0.3:
                            break 
                    else:
                        pyautogui.mouseDown()
                        dragging = True
            elif dragging:
                pyautogui.mouseUp()
                dragging = False
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
capture_running = False
capture_thread.join()
cap.release()
cv2.destroyAllWindows()