import os
import math
import time
import cv2
import serial
import imutils

if os.uname()[4].startswith("arm"):
    import RPi.GPIO as gpio


class Model:
    """All the calculations and sensor reading happens here."""
    def __init__(self, videoSrc, altitudeSensor, serialPort):
        self.altitudeSensor = altitudeSensor
        self.cam = cv2.VideoCapture(videoSrc)
        self.serialPort = serialPort
        # limits of target color acceptable
        self.targetClrLower = (29, 86, 6)
        self.targetClrHigher = (64, 255, 255)
        self.minTargetRadius = 10 # filter out smol targets

        # set up the altitude sensor
        if altitudeSensor == 1:
            # arduino
            self.sensor = serial.Serial(str(self.serialPort), 9600, timeout=.1)
        elif altitudeSensor == 2:
            # pi
            gpio.setmode(gpio.BCM)
            # trigger and echo pins of the ultrasonic rangefinder
            self.trigger = 23
            self.echo = 24
            gpio.setup(self.trigger, gpio.OUT)
            gpio.setup(self.echo, gpio.IN)
             # set up the servo used to drop the "bomb"
            dropServo = 18
            gpio.setup(dropServo, gpio.OUT)
            self.bombRelease = gpio.PWM(dropServo, 50) # set pwm clock to 50Hz
            # set the servo to 90 degrees, lock "bomb" in the "bomb bay"
            self.bombRelease.start(7.5)

    # return image and image dimensions
    def getFrame(self):
        ret, frame = self.cam.read()
        frame = imutils.resize(frame, width=600)
        height, width = frame.shape[:2]
        return frame, width, height

    def getAltitude(self):
        if self.altitudeSensor == 1:
            self.sensor.write(b'S') # ask for an altitude reading
            altitude = self.sensor.readline()[:-2]
            if altitude:
                # it has a bunch of garbage attached to it, get rid of that
                altitude = str(altitude)
                altitude = altitude.split('\'')
                altitude = int(altitude[1])
            else:
                altitude = -1
        elif self.altitudeSensor == 2:
            pulseStart = 0
            pulseEnd = 0
            # send pulse
            gpio.output(self.trigger, False)
            time.sleep(0.000002) # 2 microseconds
            gpio.output(self.trigger, True)
            time.sleep(0.000005) # 5 microseconds
            gpio.output(self.trigger, False)

            # count how long echo is HIGH
            while gpio.input(self.echo) == 0:
                pulseStart = time.time()

            while gpio.input(self.echo) == 1:
                pulseEnd = time.time()

            pulse = pulseEnd - pulseStart
            # sound goes 340 m/s or 29 microseconds per centimeter.
            # The ping travels out and back, so altitude is half the time
            altitude = pulse / 0.000029 / 2
        return altitude

    def trackTarget(self, image):
        target = 0
        frame = image[0]
        # blur and convert to HSV colorspace
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # make a mask for green and remove small blobs that are noise
        mask = cv2.inRange(hsv, self.targetClrLower, self.targetClrHigher)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and try to find the ball
        cntrs = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, 
                                 cv2.CHAIN_APPROX_SIMPLE)
        cntrs = imutils.grab_contours(cntrs)
        center = None

        if len(cntrs) > 0:
            # find the largest contour in the mask, then use it to compute
            # the minimum enclosing circle and centroid
            c = max(cntrs, key = cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius >= self.minTargetRadius:
                target = (int(x), int(y), int(radius), center)
            else:
                target = (None, None, 0, (None, None))
        else:
            target = (None, None, 0, (None, None))
        return target

    # USE ONE UNIT FOR ALL ARGS, cm in this case
    # calculates the size of the *image* of an object of known size
    def calcObjImageSize(self, size, focalLen, distance):
        if distance < 1:
            return 0
        else:
            return(size * focalLen / distance)

    # returns:
    #   - distanceVector: the distance to the tracked object from the center
    #       of the image in centimeters in the form (i^, j^)
    #       i^ is horizontal, j^ is vertical
    def calcTargetDistance(self, targetCenter, imageCenter,
                           scaleRuleLen, scaleLen):
        # make sure we don't divide by zero or use None in calculations
        if targetCenter[0] and scaleRuleLen >= 1:
            # distance in pixels
            distanceVector = (targetCenter[0] - imageCenter[0],
                              targetCenter[1] - imageCenter[1])
            # distance in centimeters
            distanceVector = (int(distanceVector[0]) / int(scaleRuleLen),
                              int(distanceVector[1]) / int(scaleRuleLen))
            distanceVector = (distanceVector[0] * scaleLen,
                              distanceVector[1] * scaleLen)
            return distanceVector
        else:
            return (None, None)

    # returns targets velocity vector relative to the center of the image
    # velocity is in cm/second
    def calcTargetVelocity(self, deltaDistance, deltaTime):
        xSpeed = (deltaDistance[0]) / deltaTime
        ySpeed = (deltaDistance[1]) / deltaTime
        return (xSpeed, ySpeed)

    # calculate the range of the bomb, given its velocity and altitude
    # we assume the launch angle is 0
    # equation: https://en.wikipedia.org/wiki/Range_of_a_projectile#Uneven_ground
    def calcBombRange(self, altitude, vel, angle = 0, g = 9.8):
        x = (vel[0] * math.cos(angle)/g * (vel[0]*math.sin(angle)
            + math.sqrt(vel[0]**2 * math.sin(angle)**2 + 2 * g * altitude)))

        y = (vel[1] * math.cos(angle)/g * (vel[1] * math.sin(angle)
            + math.sqrt(vel[1]**2 * math.sin(angle)**2 + 2 * g * altitude)))
        return(x, y)

    # checks if the bombs trajectory will lead it to hit the target
    # release "bomb" if it does
    def hit(self, bombRange, target, imgCenter):
        x, y, radius, targetCenter = target
        if targetCenter[0]:
            bombLand = (imgCenter[0] + int(bombRange[0]),
                        imgCenter[1] + int(bombRange[1]))
            # if the point where the bomb will land is inside the target
            # circle(https://math.stackexchange.com/a/198769)
            if math.sqrt((bombLand[0] - x)**2 + (bombLand[1] - y)**2) < radius:
                # drop the bomb and reset
                if self.altitudeSensor == 2:
                    self.bombRelease.ChangeDutyCycle(12.5)
                return True
            else:
                return False

    def cleanGpio(self):
        if self.altitudeSensor == 2:
            gpio.cleanup()
