import pyautogui
import time

print("Move your mouse to the top-left corner to stop.")
time.sleep(2)

pyautogui.moveTo(500, 500, duration=1)

print("Mouse moved.")