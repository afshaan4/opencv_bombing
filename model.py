import cv2
import imutils
import re
import serial

class Model:
    """
    Model reads from sensors and does all the calculations
    Args:
    - videoSrc: camera that opencv will use
    - serialPort: the serial port that the arduino is connected to
    - baudRate: baud rate for serial communication with the arduino
    """
    def __init__(self, videoSrc, serialPort, baudRate = 9600):
        # limits of green acceptable
        self.greenLower = (29, 86, 6)
        self.greenUpper = (64, 255, 255)
        self.arduino = serial.Serial(str(serialPort), int(baudRate), timeout=.1)
        
        '''
         handle getting the camera
         done like this because we need the size of the frame
        '''
        source = str(videoSrc).strip()
        # Win32: handle drive letter ('c:', ...)
        source = re.sub(r'(^|=)([a-zA-Z]):([/\\a-zA-Z0-9])', r'\1?disk\2?\3', source)
        chunks = source.split(':')
        chunks = [re.sub(r'\?disk([a-zA-Z])\?', r'\1:', s) for s in chunks]

        source = chunks[0]
        try: source = int(source)
        except ValueError: pass
        params = dict( s.split('=') for s in chunks[1:] )

        self.cam = cv2.VideoCapture(source)
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
        return frame, height, width


    def getDistance(self):
        # read and trim the distance reading
        distance = self.arduino.readline()[:-2]
        if distance:
            # it has a bunch of garbage attached to it, get rid of that
            distance = str(distance)
            distance = distance.split('\'')
            distance = int(distance[1])
        else:
            # if we get something that is NOT a number
            distance = -1

        return distance


    def trackTarget(self, image):
        frame = image[0]
        # resize, blur, convert to HSV colorspace
        # frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

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
            return (0, 0, 0, (0, 0), mask)


    # USE ONE UNIT FOR ALL ARGS, cm in this case
    def calcScaleRuleUnit(self, size, f, dist):
        if dist < 1:
            return 0
        else:
            return(size * f / dist)


    # returns the center of the image and the distance to target
    # as a vector originating at the center of the image
    # the vector is of form (i^, j^)
    def calcTargetDistance(self, targetCenter, imgWidth, imgHeight):
        # x: width, y: height
        imageCenter = (int(imgWidth / 2), int(imgHeight / 2))
        distanceVector = (targetCenter[0] - imageCenter[0],
            targetCenter[1] - imageCenter[1])
        return distanceVector, imageCenter