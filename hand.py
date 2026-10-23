import cv2
import mediapipe as mp
import track
import random
from pynput.mouse import Button, Controller
import pyautogui
from time import sleep

mouse = Controller()
screen_width, screen_height = pyautogui.size()

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', ',']
]

FRAME_W, FRAME_H = 1280, 720


def is_move_mouse(index_angle, middle_angle, thumb_index_dist):
    return thumb_index_dist < 50 and index_angle > 90


def is_left_click(index_angle, middle_angle, thumb_index_dist):
    return index_angle < 50 and middle_angle > 90 and thumb_index_dist > 50


def is_right_click(index_angle, middle_angle, thumb_index_dist):
    return middle_angle < 50 and index_angle > 90 and thumb_index_dist > 50


def is_double_click(index_angle, middle_angle, thumb_index_dist):
    return middle_angle < 50 and index_angle < 50 and thumb_index_dist > 50


def is_screenshot(index_angle, middle_angle, thumb_index_dist):
    return middle_angle < 50 and index_angle < 50 and thumb_index_dist < 50


def detect_gestures(frame, landmarks_list, index_finger_tip, thumb_index_dist):
    if len(landmarks_list) < 21:
        return

    index_angle = track.getangle(landmarks_list[5], landmarks_list[6], landmarks_list[8])
    middle_angle = track.getangle(landmarks_list[9], landmarks_list[10], landmarks_list[12])

    if is_move_mouse(index_angle, middle_angle, thumb_index_dist):
        if index_finger_tip is not None:
            x = int(index_finger_tip.x * screen_width)
            y = int(index_finger_tip.y * screen_height)
            pyautogui.moveTo(x, y)

    elif is_left_click(index_angle, middle_angle, thumb_index_dist):
        mouse.press(Button.left)
        mouse.release(Button.left)
        cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    elif is_right_click(index_angle, middle_angle, thumb_index_dist):
        mouse.press(Button.right)
        mouse.release(Button.right)
        cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    elif is_double_click(index_angle, middle_angle, thumb_index_dist):
        pyautogui.doubleClick()
        cv2.putText(frame, "Double Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    elif is_screenshot(index_angle, middle_angle, thumb_index_dist):
        im1 = pyautogui.screenshot()
        label = random.randint(1, 1000)
        im1.save(f'my_screenshot_{label}.png')
        cv2.putText(frame, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)


class VirtualButton:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


def draw(img, buttonlist):
    for btn in buttonlist:
        x, y = btn.pos
        w, h = btn.size
        cv2.rectangle(img, btn.pos, (x + w, y + h), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, btn.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    return img


buttonlist = []
button_size = [75, 75]
x_offset, y_offset = 50, 50
x_spacing, y_spacing = 75, 75

for i, row in enumerate(keys):
    for j, key in enumerate(row):
        x = x_offset + j * x_spacing
        y = y_offset + i * y_spacing
        buttonlist.append(VirtualButton([x, y], key, button_size))


def handle_keyboard(frame, landmarks_list, thumb_index_dist):
    tip_x = int(landmarks_list[8][0] * FRAME_W)
    tip_y = int(landmarks_list[8][1] * FRAME_H)

    index_middle_dist = track.get_distance((landmarks_list[8], landmarks_list[12]))
    key_pressed = index_middle_dist < 50 and thumb_index_dist > 50

    for btn in buttonlist:
        x, y = btn.pos
        w, h = btn.size
        if x < tip_x < x + w and y < tip_y < y + h:
            cv2.rectangle(frame, btn.pos, (x + w, y + h), (255, 178, 0), cv2.FILLED)
            cv2.putText(frame, btn.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 2, (255, 128, 255), 2)
            if key_pressed:
                pyautogui.press(btn.text.lower())
                cv2.rectangle(frame, btn.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, btn.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 2, (255, 120, 120), 2)
                sleep(0.2)


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    draw_utils = mp.solutions.drawing_utils

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed = hands.process(frameRGB)

        landmarks_list = []
        index_finger_tip = None  # mediapipe landmark object (normalised)

        if processed.multi_hand_landmarks:
            hand_landmarks = processed.multi_hand_landmarks[0]
            draw_utils.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)

            for lm in hand_landmarks.landmark:
                landmarks_list.append((lm.x, lm.y))

            # Single source of truth for the fingertip landmark
            index_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]

        frame = draw(frame, buttonlist)

        if landmarks_list:
            # Compute shared values ONCE per frame
            thumb_index_dist = track.get_distance((landmarks_list[4], landmarks_list[5]))

            detect_gestures(frame, landmarks_list, index_finger_tip, thumb_index_dist)
            handle_keyboard(frame, landmarks_list, thumb_index_dist)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
