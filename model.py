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
         done like this coz we need the size of the frame
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


    def getFrame(self):
        ret, frame = self.cam.read()
        return ret, frame


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


    def trackItem(self):
        pass


    # USE ONE UNIT FOR ALL ARGS, cm in this case
    def calcScaleRuleUnit(self, size, f, dist):
        if dist < 1:
            return 0
        else:
            return(size * f / dist)


    def calcDistance(self):
        pass