from model import Model
from view import View
import cv2
import sys

class Controller:
    """docstring for Controller"""
    def __init__(self, model, view, videoSrc, sensor, serialPort):
        self.model = model(videoSrc, int(sensor), serialPort)
        self.view = view()
        # camera parameters, change these for your camera
        self.scaleLength = 10 # size of unit for scale rule in cm
        self.focalLen = 0.6
        self.pixelsPerCM = 1950


    def run(self):
        oldAltitude = 0
        running = True
        while running:
            # get all the data
            frame = self.model.getFrame()
            altitude = self.model.getAltitude()

            # coz altitude is not being sent in sync and is sometimes corrupted
            if altitude == -1:
                altitude = oldAltitude
            else:
                oldAltitude = altitude

            # calculate the size of 10cm in the image
            scaleRuleLen = self.model.calcObjImageSize(self.scaleLength,
                self.focalLen, altitude)
            scaleRuleLen *= self.pixelsPerCM

            # find target
            target = self.model.trackTarget(frame)

            # calculate distance to target
            distVector, imgCenter = self.model.calcTargetDistance(target[3],
                frame[1], frame[2], scaleRuleLen, self.scaleLength)

            # display all that stuff
            self.view.showDistance(frame, target[3], imgCenter, distVector)
            self.view.showTarget(frame, target)
            self.view.showFrame(frame, scaleRuleLen, target[4])

            # yeet outta here
            keyEvent = cv2.waitKey(30)
            if keyEvent == 27:
                running = False


def main():
    try:
        vidSrc = sys.argv[1]
        sensor = sys.argv[2]
        serPort = sys.argv[3]
    except:
        vidSrc = 0
        if not sensor:
            sensor = 1
            print('WARNING: no sensor specified, defaulting to sensor 1(arduino)')
        elif not serPort:
            print('WARNING: serial port not specified')

    Controller(Model, View, vidSrc, sensor, serPort).run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    