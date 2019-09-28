import cv2
import imutils
import re
import serial
import time
import os

if os.uname()[4].startswith("arm"):
    import RPi.GPIO as gpio


class Model:
    """
    Model reads from sensors and does all the calculations
    """
    def __init__(self, videoSrc, altitudeSensor, serialPort):
        # limits of green acceptable
        self.greenLower = (29, 86, 6)
        self.greenUpper = (64, 255, 255)
        self.serialPort = serialPort
        self.altitudeSensor = altitudeSensor
        # have to do this only once
        if altitudeSensor == 1:
            # we read from the arduino
            self.sensor = serial.Serial(str(self.serialPort), 9600, timeout=.1)
        elif altitudeSensor == 2:
            gpio.setmode(gpio.BCM)
            # trigger and echo pins of the ultrasonic rangefinder
            self.trigger = 23
            self.echo = 24
            gpio.setup(self.trigger, gpio.OUT)
            gpio.setup(self.echo, gpio.IN)

        '''
         handle getting the camera
         done like this because we need the size of the frame
        '''
        src = str(videoSrc).strip()
        # Win32: handle drive lett-er ('c:', ...)
        src = re.sub(r'(^|=)([a-zA-Z]):([/\\a-zA-Z0-9])', r'\1?disk\2?\3', src)
        chunks = src.split(':')
        chunks = [re.sub(r'\?disk([a-zA-Z])\?', r'\1:', s) for s in chunks]

        src = chunks[0]
        try: src = int(src)
        except ValueError: pass
        params = dict( s.split('=') for s in chunks[1:] )

        self.cam = cv2.VideoCapture(src)
        # add size to capture
        if 'size' in params:
            w, h = map(int, params['size'].split('x'))
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)


    # return image and image dimensions
    def getFrame(self):
        ret, frame = self.cam.read()
        frame = imutils.resize(frame, width=600)
        height, width = frame.shape[:2]
        return frame, width, height


    def getAltitude(self):
        # selecting the altitude sensor
        if self.altitudeSensor == 1:
            # we read from the arduino
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
        frame = image[0]
        # blur and convert to HSV colorspace
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # make a mask for green and remove small blobs that are noise
        mask = cv2.inRange(hsv, self.greenLower, self.greenUpper)
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
            # x and y are the coords for the center of the min enclosing circle
            return int(x), int(y), int(radius), center, mask
        else:
            return (None, None, 0, (None, None), mask)


    # USE ONE UNIT FOR ALL ARGS, cm in this case
    # calculates the size of the *image* of an object of known size
    def calcObjImageSize(self, size, focalLen, distance):
        if distance < 1:
            return 0
        else:
            return(size * focalLen / distance)


    # returns:
    #   - imageCenter: the coordinates for the center of the image
    #   - distanceVector: the distance to the tracked object from the center
    #       of the image in centimeters in the form (i^, j^)
    #       i^ is horizontal, j^ is vertical
    def calcTargetDistance(self, targetCenter, imgWidth, imgHeight,
        scaleRuleLen, scaleLen):
        imageCenter = (int(imgWidth / 2), int(imgHeight / 2))

        # make sure we don't divide by zero or use None in calculations
        if targetCenter[0] and scaleRuleLen > 0:
            # distance in pixels
            distanceVector = (targetCenter[0] - imageCenter[0],
                targetCenter[1] - imageCenter[1])
            # distance in centimeters
            distanceVector = (int(distanceVector[0]) / int(scaleRuleLen),
                int(distanceVector[1]) / int(scaleRuleLen))
            distanceVector = (distanceVector[0] * scaleLen, distanceVector[1] * scaleLen)
            return distanceVector, imageCenter
        else:
            return ((None, None), imageCenter)


    # returns targets velocity vector relative to the center of the image
    # velocity is in cm/second
    def calcTargetVelocity(self, deltaDistance, deltaTime):
        # 1 second / deltaTime = multiplier
        # so to get speed in centimeter/second just:
        # (deltaDistance * multiplier) / (deltaTime * multiplier)
        second = 1
        multiplier = second / deltaTime
        deltaTime *= multiplier

        xSpeed = (deltaDistance[0] * multiplier) / deltaTime
        ySpeed = (deltaDistance[1] * multiplier) / deltaTime
        return (xSpeed, ySpeed)
