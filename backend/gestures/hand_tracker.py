import cv2
import mediapipe as mp
import pyautogui
import math
import time
import os
import tkinter as tk
import threading

# Screen size
screen_width, screen_height = pyautogui.size()

# PyAutoGUI settings
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Smoothing (Exponential Moving Average)
smoothed_x, smoothed_y = screen_width / 2, screen_height / 2
SMOOTHING_ALPHA = 0.35  # Adjusted for better responsiveness

# Click cooldown
last_click_time = 0
CLICK_COOLDOWN = 0.8

# Scroll tracking
prev_scroll_y = None
SCROLL_THRESHOLD = 5

# Volume tracking
last_volume_action = 0
VOLUME_COOLDOWN = 0.2

# Swipe tracking
prev_wrist_x = None
last_swipe_time = 0
SWIPE_THRESHOLD = 0.15 
SWIPE_COOLDOWN = 1.0

# Lens/Selection Mode
in_lens_mode = False
lens_start_pos = None
lens_end_pos = None

# Shared state for thread-safe Tkinter updates
overlay_state = {
    'visible': False,
    'rect': (0, 0, 0, 0)
}

# Tkinter Overlay for Screen Selection (runs completely in its own thread)
def run_overlay():
    root = tk.Tk()
    root.attributes('-alpha', 0.3)
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    root.config(bg='green')
    root.geometry("0x0+-1000+-1000") # Start hidden off-screen
    
    def poll_update():
        if overlay_state['visible']:
            x, y, w, h = overlay_state['rect']
            root.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")
        else:
            root.geometry("0x0+-1000+-1000")
            
        root.after(16, poll_update) # ~60 FPS polling

    poll_update()
    root.mainloop()

threading.Thread(target=run_overlay, daemon=True).start()


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def is_finger_up(tip, pip):
    return tip.y < pip.y

def start_gesture_control():
    global smoothed_x, smoothed_y, last_click_time, prev_scroll_y, last_volume_action
    global prev_wrist_x, last_swipe_time
    global in_lens_mode, lens_start_pos, lens_end_pos

    cap = cv2.VideoCapture(0)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    mp_draw = mp.solutions.drawing_utils

    print("Gesture Control Started ✋ (Upgraded Stability & Overlay)")

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark

                wrist = landmarks[0]
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                index_pip = landmarks[6]
                middle_tip = landmarks[12]
                middle_pip = landmarks[10]
                ring_tip = landmarks[16]
                ring_pip = landmarks[14]
                pinky_tip = landmarks[20]
                pinky_pip = landmarks[18]

                ix, iy = int(index_tip.x * frame_width), int(index_tip.y * frame_height)
                tx, ty = int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height)

                index_up = is_finger_up(index_tip, index_pip)
                middle_up = is_finger_up(middle_tip, middle_pip)
                ring_up = is_finger_up(ring_tip, ring_pip)
                pinky_up = is_finger_up(pinky_tip, pinky_pip)

                pinch_dist = distance(ix, iy, tx, ty)
                current_time = time.time()

                # 👋 SWIPE MODE
                if prev_wrist_x is not None and (current_time - last_swipe_time) > SWIPE_COOLDOWN:
                    delta_x = wrist.x - prev_wrist_x
                    if delta_x > SWIPE_THRESHOLD:
                        pyautogui.hotkey('ctrl', 'tab')
                        last_swipe_time = current_time
                    elif delta_x < -SWIPE_THRESHOLD:
                        pyautogui.hotkey('ctrl', 'shift', 'tab')
                        last_swipe_time = current_time
                prev_wrist_x = wrist.x


                # 🔍 LENS MODE (Shaka sign)
                is_shaka = pinky_up and not index_up and not middle_up and not ring_up
                if is_shaka:
                    if not in_lens_mode:
                        in_lens_mode = True
                        lens_start_pos = None
                        lens_end_pos = None
                    
                    cv2.putText(frame, "LENS MODE", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                    px, py = int(pinky_tip.x * frame_width), int(pinky_tip.y * frame_height)
                    select_pinch_dist = distance(tx, ty, px, py)

                    # Map to screen using active area to reach edges easily
                    active_w, active_h = frame_width * 0.5, frame_height * 0.5
                    active_x, active_y = frame_width * 0.25, frame_height * 0.25
                    cx, cy = (tx + px) / 2, (ty + py) / 2
                    norm_x = max(0, min(1, (cx - active_x) / active_w))
                    norm_y = max(0, min(1, (cy - active_y) / active_h))
                    screen_x = screen_width * norm_x
                    screen_y = screen_height * norm_y
                    
                    smoothed_x = SMOOTHING_ALPHA * screen_x + (1 - SMOOTHING_ALPHA) * smoothed_x
                    smoothed_y = SMOOTHING_ALPHA * screen_y + (1 - SMOOTHING_ALPHA) * smoothed_y
                    
                    if select_pinch_dist < 60: # Pinching
                        if lens_start_pos is None:
                            lens_start_pos = (int(smoothed_x), int(smoothed_y))
                        lens_end_pos = (int(smoothed_x), int(smoothed_y))
                        
                        # Show overlay on main screen
                        x1, y1 = lens_start_pos
                        x2, y2 = lens_end_pos
                        rx, ry = min(x1, x2), min(y1, y2)
                        rw, rh = abs(x2 - x1), abs(y2 - y1)
                        if rw > 10 and rh > 10:
                            overlay_state['rect'] = (rx, ry, rw, rh)
                            overlay_state['visible'] = True
                    else:
                        overlay_state['visible'] = False
                        if lens_start_pos is not None and lens_end_pos is not None:
                            x1, y1 = lens_start_pos
                            x2, y2 = lens_end_pos
                            x, y = min(x1, x2), min(y1, y2)
                            w, h = abs(x2 - x1), abs(y2 - y1)
                            
                            if w > 50 and h > 50:
                                try:
                                    screenshot = pyautogui.screenshot(region=(x, y, w, h))
                                    img_path = os.path.join(os.path.dirname(__file__), '..', 'vision', 'lens_capture.png')
                                    os.makedirs(os.path.dirname(img_path), exist_ok=True)
                                    screenshot.save(img_path)
                                    with open(os.path.join(os.path.dirname(__file__), '..', 'vision', 'trigger_analysis.txt'), 'w') as f:
                                        f.write(img_path)
                                except Exception as e:
                                    print("Error:", e)
                                
                            lens_start_pos = None
                            lens_end_pos = None

                    continue
                else:
                    if in_lens_mode:
                        overlay_state['visible'] = False
                        in_lens_mode = False

                # 🔊 VOLUME MODE
                if index_up and middle_up and not ring_up and not pinky_up and pinch_dist > 60:
                    if (current_time - last_volume_action) > VOLUME_COOLDOWN:
                        if pinch_dist > 150:
                            pyautogui.press("volumeup")
                            last_volume_action = current_time
                        elif pinch_dist < 90:
                            pyautogui.press("volumedown")
                            last_volume_action = current_time
                    cv2.putText(frame, "VOLUME", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)

                # ✌️ SCROLL MODE
                elif index_up and middle_up and not ring_up and not pinky_up:
                    scroll_y = int((index_tip.y + middle_tip.y) / 2 * frame_height)
                    if prev_scroll_y is not None:
                        delta = prev_scroll_y - scroll_y
                        if abs(delta) > SCROLL_THRESHOLD:
                            # Multiplied by 30 for much faster Windows scrolling
                            pyautogui.scroll(int(delta * 30))
                    prev_scroll_y = scroll_y
                    cv2.putText(frame, "SCROLL", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

                # 🖱️ MOUSE MOVE & CLICK
                elif index_up and not middle_up and not ring_up and not pinky_up:
                    prev_scroll_y = None
                    
                    # Active area mapping to reach screen edges easily
                    active_w, active_h = frame_width * 0.5, frame_height * 0.5
                    active_x, active_y = frame_width * 0.25, frame_height * 0.25
                    
                    norm_x = max(0, min(1, (ix - active_x) / active_w))
                    norm_y = max(0, min(1, (iy - active_y) / active_h))
                    
                    screen_x = screen_width * norm_x
                    screen_y = screen_height * norm_y
                    
                    smoothed_x = SMOOTHING_ALPHA * screen_x + (1 - SMOOTHING_ALPHA) * smoothed_x
                    smoothed_y = SMOOTHING_ALPHA * screen_y + (1 - SMOOTHING_ALPHA) * smoothed_y
                    
                    safe_x = max(0, min(screen_width - 1, smoothed_x))
                    safe_y = max(0, min(screen_height - 1, smoothed_y))
                    
                    pyautogui.moveTo(safe_x, safe_y)

                    if pinch_dist < 40 and (current_time - last_click_time) > CLICK_COOLDOWN:
                        pyautogui.click()
                        last_click_time = current_time
                        cv2.putText(frame, "CLICK!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("Touch AI Gesture Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    overlay_state['visible'] = False
    cap.release()
    cv2.destroyAllWindows()