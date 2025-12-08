import cv2
import numpy as np

cap = cv2.VideoCapture(0)

lower_color = np.array([0, 130, 150], np.uint8)
upper_color = np.array([5, 255, 255], np.uint8)




def detect_wand():
    """Returns x, y, frame."""
    ret, frame = cap.read()
    if not ret:
        return None, None, None

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_color, upper_color)

    mask = cv2.erode(mask, None, 1)
    mask = cv2.dilate(mask, None, 2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    wand_x = wand_y = None

    if contours:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        if radius > 5:
            wand_x, wand_y = int(x), int(y)
            cv2.circle(frame, (wand_x, wand_y), int(radius), (255, 50, 255), 2)

    return wand_x, wand_y, frame
