import cv2
import pyautogui
import time
from cvzone.HandTrackingModule import HandDetector
import webbrowser
import subprocess

def open_spotify_app():
    try:
        subprocess.Popen("spotify")
    except FileNotFoundError:
        print("Spotify is not installed or not found in PATH.")

cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)
detector = HandDetector(maxHands=1)

prevGesture = None
gesture_choice = None
awaiting_confirmation = False
awaiting_next_app = False
message = ""
app_state = {'app': None, 'playing': False}

apps = {
    'youtube': 'https://www.youtube.com',
    'spotify': 'https://open.spotify.com',
    'gmail': 'https://mail.google.com/mail/u/0/#inbox'
}

def show_instructions(img, app):
    instructions = {
        'youtube': [
            "5 fingers: Play/Pause",
            "2 fingers: 2x Speed",
            "4 fingers: -0.25x Speed",
            "1 finger: Move pointer",
            "Thumb + Index: Click",
            "Move hand up/down to scroll",
            "Fist: Close App",
        ],
        'spotify': [
            "5 fingers: Play/Pause",
            "2 fingers: Next Song",
            "1 finger: Previous Song",
            "Fist: Close App",
        ],
        'gmail': [
            "1 finger: Go to Inbox",
            "2 fingers: Go to Outbox",
            "3 fingers: Go to Spam",
            "5 fingers: Reply Mode",
            "Thumb + Index: Click",
            "Move hand up/down to scroll",
            "Fist: Close App",
        ]
    }

    if app in instructions:
        y_offset = 40
        cv2.putText(img, f" {app.upper()} GESTURES", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        for i, line in enumerate(instructions[app]):
            cv2.putText(img, f"{line}", (10, y_offset + (i+1)*30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def open_app(name):
    if name == 'spotify':
        open_spotify_app()
    else:
        webbrowser.open(apps[name])
    app_state['app'] = name
    time.sleep(5)


def toggle_play_pause():
    pyautogui.press('k')
    app_state['playing'] = not app_state['playing']

def close_app():
    pyautogui.hotkey('ctrl', 'w')
    app_state['app'] = None

def scroll_page(direction):
    pyautogui.scroll(300 if direction == "up" else -300)

def reply_mode():
    pyautogui.click()
    time.sleep(1)
    pyautogui.write("Hi, this is a gesture-based response.", interval=0.1)

def display_message(img, text, pos=(10, 30), color=(0, 255, 0)):
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        x, y = lmList[8][:2]

        if not awaiting_confirmation and not awaiting_next_app and not app_state['app']:
            if fingers == [0, 1, 0, 0, 0] and prevGesture != '1':
                gesture_choice = "Open YouTube"
                message = "Detected: YouTube — Show to Thumbs up confirm"
                prevGesture = '1'
                awaiting_confirmation = True

            elif fingers == [0, 1, 1, 0, 0] and prevGesture != '2':
                gesture_choice = "Open Spotify"
                message = "Detected: Spotify — Show Thumbs up to confirm"
                prevGesture = '2'
                awaiting_confirmation = True

            elif fingers == [0, 1, 1, 1, 0] and prevGesture != '3':
                gesture_choice = "Gmail Inbox"
                message = "Detected: Gmail — Show Thumbs up to confirm"
                prevGesture = '3'
                awaiting_confirmation = True

            elif fingers == [1, 1, 1, 1, 1] and prevGesture != '5_reply':
                gesture_choice = "Reply Mode"
                message = "Detected: Reply Mode — Show Thumbs up to confirm"
                prevGesture = '5_reply'
                awaiting_confirmation = True

        elif awaiting_confirmation:
            if fingers == [1, 0, 0, 0, 0] and prevGesture != 'thumbs_up':
                message = f"Confirmed: {gesture_choice}"
                if gesture_choice == "Open YouTube":
                    open_app('youtube')
                elif gesture_choice == "Open Spotify":
                    open_app('spotify')
                elif gesture_choice == "Gmail Inbox":
                    open_app('gmail')
                    time.sleep(3)
                    pyautogui.hotkey('g', 'i')
                elif gesture_choice == "Reply Mode":
                    reply_mode()
                awaiting_confirmation = False
                prevGesture = 'thumbs_up'
                gesture_choice = None

            elif fingers == [0, 0, 0, 0, 0] and prevGesture != 'fist_cancel':
                message = "Cancelled. Show a new gesture."
                awaiting_confirmation = False
                prevGesture = 'fist_cancel'
                gesture_choice = None

        if app_state['app'] and fingers == [0, 0, 0, 0, 0] and not awaiting_next_app:
            close_app()
            message = "Closed current app. Show 1/2/3 to switch."
            awaiting_next_app = True
            app_state['app'] = None
            prevGesture = 'fist'

        elif awaiting_next_app:
            if fingers == [0, 1, 0, 0, 0] and prevGesture != '1':
                message = "Switch to YouTube? Show Thumbs up to confirm"
                gesture_choice = "Open YouTube"
                prevGesture = '1'
                awaiting_confirmation = True
                awaiting_next_app = False

            elif fingers == [0, 1, 1, 0, 0] and prevGesture != '2':
                message = "Switch to Spotify? Show Thumbs up to confirm"
                gesture_choice = "Open Spotify"
                prevGesture = '2'
                awaiting_confirmation = True
                awaiting_next_app = False

            elif fingers == [0, 1, 1, 1, 0] and prevGesture != '3':
                message = "Switch to Gmail? Show Thumbs up to confirm"
                gesture_choice = "Gmail Inbox"
                prevGesture = '3'
                awaiting_confirmation = True
                awaiting_next_app = False

        # YouTube specific gestures
        if app_state['app'] == 'youtube':
            if fingers == [1, 1, 1, 1, 1] and prevGesture != 'play_pause':
                toggle_play_pause()
                message = "Play/Pause toggled"
                prevGesture = 'play_pause'
            elif fingers == [0, 1, 1, 0, 0] and prevGesture != 'yt_2x':
                pyautogui.hotkey('shift', '.')
                pyautogui.hotkey('shift', '.')
                message = " YouTube Speed: 2x"
                prevGesture = 'yt_2x'
            elif fingers == [0, 1, 1, 1, 1] and prevGesture != 'yt_minus':
                pyautogui.hotkey('shift', ',')
                message = "YouTube Speed -0.25x"
                prevGesture = 'yt_minus'

        # Gmail specific navigation
        if app_state['app'] == 'gmail':
            if fingers == [0, 1, 0, 0, 0] and prevGesture != 'gmail_inbox':
                pyautogui.hotkey('g', 'i')
                message = " Gmail: Inbox"
                prevGesture = 'gmail_inbox'
            elif fingers == [0, 1, 1, 0, 0] and prevGesture != 'gmail_outbox':
                pyautogui.hotkey('g', 't')
                message = "Gmail: Sent"
                prevGesture = 'gmail_outbox'
            elif fingers == [0, 1, 1, 1, 0] and prevGesture != 'gmail_spam':
                pyautogui.hotkey('g', 's')
                message = "Gmail: Spam"
                prevGesture = 'gmail_spam'
        if app_state['app'] == 'spotify':
    # 5 finger → Play/Pause
            if fingers == [1, 1, 1, 1, 1] and prevGesture != 'spotify_play_pause':
                toggle_play_pause()
                message = "Play/Pause toggled"
                prevGesture = 'play_pause'

    # 2 fingers → Next Song
            elif fingers == [0, 1, 1, 0, 0] and prevGesture != 'spotify_next':
                pyautogui.hotkey('ctrl', 'right')
                message = "Next Song"
                prevGesture = 'spotify_next'

    # 3 fingers → Previous Song
            elif fingers == [0, 1, 1, 1, 0] and prevGesture != 'spotify_prev':
                pyautogui.hotkey('ctrl', 'left')
                message = "Previous Song"
                prevGesture = 'spotify_prev'

        if app_state['app'] in ['youtube', 'gmail'] and fingers == [0, 1, 0, 0, 0]:
            pyautogui.moveTo(x * 2, y * 2)

        if fingers[0] == 1 and fingers[1] == 1 and sum(fingers) == 2:
            if app_state['app'] in ['youtube', 'gmail']:
                pyautogui.click()

        if app_state['app'] == 'spotify':
            if fingers == [0, 1, 0, 0, 0] and prevGesture != 'spotify_prev':
                pyautogui.hotkey('shift', 'p')
                message = "Previous Song"
                prevGesture = 'spotify_prev'
            elif fingers == [0, 1, 1, 0, 0] and prevGesture != 'spotify_next':
                pyautogui.hotkey('shift', 'n')
                message = "Next Song"
                prevGesture = 'spotify_next'

        if app_state['app'] in ['youtube', 'gmail']:
            if y < 150:
                scroll_page("up")
            elif y > 350:
                scroll_page("down")

    else:
        prevGesture = None

    if message:
        display_message(img, message)

    mini_img = cv2.resize(img, (200, 150))
    frame = img.copy()
    frame[10:160, -210:-10] = mini_img
    cv2.rectangle(frame, (img.shape[1] - 210, 10), (img.shape[1] - 10, 160), (0, 255, 255), 2)

    if app_state['app']:
        show_instructions(frame, app_state['app'])

    cv2.imshow("Gesture Control", frame)
    cv2.setWindowProperty("Gesture Control", cv2.WND_PROP_TOPMOST, 1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()