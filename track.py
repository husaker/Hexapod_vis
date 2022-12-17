import cv2
import numpy as np
import math
import serial
import time

timing1 = time.time()
#timing2 = time.time()


if __name__ == '__main__':
    def nothing(*arg):
        pass

ser = serial.Serial('COM6', 9600) #подключение по ком порту
#time.sleep(2)
ser.reset_input_buffer()

cv2.namedWindow("result")  # создаем главное окно

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
hsv_min = np.array((160, 113, 147), np.uint8)
hsv_max = np.array((182, 215, 255), np.uint8)

color_yellow = (0, 255, 255)

SideFlag = False
noAim = True
movingX = False
movingY = False
movingR = False
stop = False
Fire = False
sideWalk = False
sideR = False
sideDetectionFlag = False
sidewaysMove = False
height = 0
width = 0

def move(command, value):
    ser.write(command)
    ser.write(value)


def sideDetect(widht, height):
    timing3 = time.time()
    sideR = False
    if (abs(width - height) > 50):
        diff = abs(width - height)
        if time.time() - timing1 > 1:
            timing1 = time.time()
            move("Y", "-40")
        if (diff > abs(width - height)):
            sideR = True
    return sideR

def sideHasDifference(widht, height):
    difference = False
    if(abs(heigh-widht) > 10):
        difference = True
    return difference

move(b"S", b"0")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 0)  # переворот кадра
    img = cv2.flip(img, 1)  # отражение кадра вдоль оси Y
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv, hsv_min, hsv_max)

    contours0, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours0
    big_contour = []
    maxop = 0
    for i in cnt:
        areas = cv2.contourArea(i)
        if areas > maxop:
            maxop = areas
            big_contour = i

    try:
        ((centx, centy), (width, height), angle) = cv2.fitEllipse(big_contour)

    except:
        if(noAim == True):
            noAim = False
            move(b"R", b"40")
            move(b"R", b"40")
            print("R")
            print("40")
            print("Исключение--------------------------------------------------")

    moments = cv2.moments(thresh, 1)
    dM01 = moments['m01']
    dM10 = moments['m10']
    S_moment = moments['m00'] #area in pixels
    S_countour = height*height*math.pi/4+0.00000001
    #w = math.sqrt(S*4/3.1415) + 0.0000001 #width in pixels or diameter
    w = height + 0.0000000001
    W = 6
    f = 884 #focal lenght = 844
    d = f*W/w



    if S_moment > 300:
        x = int(dM10 / S_moment)
        y = int(dM01 / S_moment)
        cv2.circle(img, (x, y), 5, color_yellow, 2)
        cv2.putText(img, "%d" % d, (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color_yellow, 2)

        #print(S_countour/S_moment*100 + 0.00000001)


        if((S_countour/S_moment)*100 + 0.0000001 > 140):
            if(x < 640 and SideFlag == False):
                #move(b"Y", b"40")
                print("Y")
                print("40")
                SideFlag = True
            if (x > 641 and SideFlag == False):
                #move(b"Y", b"-40")
                print("Y")
                print("-40")
                SideFlag = True
        else:
            if (x<540 and movingR == False):
                move(b"R", b"30")
                print("R")
                print("40")
                noAim = True
                movingR = True
                movingX = False
                stop = False
                SideFlag = False

            if (x>740 and movingR == False):
                move (b"R", b"-30")
                print("R")
                print("-40")
                noAim = True
                movingR = True
                movingX = False
                stop = False
                SideFlag = False

            if (x<=740 and x>=560 and movingX == False):
                movingX = True
                if (movingR == True):
                    #move(b"S", b"0")
                    print("S")
                    print("0")
                    movingR = False
                move(b"X", b"60")
                print("X")
                print("40")
                stop = False
                SideFlag = False

            if (d < 40 and stop == False):
                stop = True
                move(b"S", b"0")
                print("S")
                print("0")

                time.sleep(1)
                move(b"P", b"1000")
                print("P")
                print("1000")
                print("стрельба------------------------------------")

                time.sleep(1)
                move(b"S", b"0")
                print("S")
                print("0")
                print("остановка после стрельбы------------------------------------------")






    cv2.line(img, (560, 0), (560, 720), (0, 255, 0), 3)
    cv2.line(img, (740, 0), (740, 720), (0, 255, 0), 3)

    cv2.imshow('result', img)
    cv2.imshow('vision', thresh)
    ch = cv2.waitKey(5)
    if ch == 27:
        break

cap.release()
cv2.destroyAllWindows()