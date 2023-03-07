import cv2
import numpy as np

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False
current_color = ''
old_color = ''
#This sections will do stuff while your camera is on
while rval:
    #show camera
    cv2.imshow("preview", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    # exit on ESC
    if key == 27:
        break
    colors = {
    "red" : (0, 0, 255),
    "blue" : (255, 0, 0),
    "green" : (0, 255, 0),
    "yellow" : (0, 255, 255),
    "white" : (255, 255, 255),
    "orange" : (0, 165, 255)
    }
    #get a list of colors on the screen
    b = frame[:, :, :1]
    g = frame[:, :, 1:2]
    r = frame[:, :, 2:]
    #get a mean of those colors
    b_mean = np.mean(b)
    g_mean = np.mean(g)
    r_mean = np.mean(r)
    #check to see which mean is higher, the highest is the color it sees
    if (b_mean > g_mean and b_mean > r_mean and current_color != "Blue"):
        current_color ="Blue"
    elif (g_mean > r_mean and g_mean > b_mean and current_color != "Green"):
        current_color ="Green"
    elif (r_mean > b_mean and r_mean > g_mean and current_color != "Red"):
        current_color ="Red"
    if old_color != current_color:
        print(current_color)
    old_color = current_color

vc.release()
cv2.destroyWindow("preview")