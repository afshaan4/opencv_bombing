from model import Model
from view import View
import cv2
import sys
import time

class Controller:
    """docstring for Controller"""
    def __init__(self, model, view, videoSrc, sensor, serialPort):
        self.model = model(videoSrc, int(sensor), serialPort)
        self.view = view()
        # size of unit for scale rule in cm
        # this is what we will measure everything in the image with
        self.scaleLength = 10
        # camera parameters, change these for your camera
        self.focalLen = 0.6
        self.pixelsPerCM = 1950


    def run(self):
        oldAltitude = 0
        oldTime = 0
        oldDistVector = (0, 0)
        running = True
        while running:
            # get all the data
            frame = self.model.getFrame()
            altitude = self.model.getAltitude()

            # coz altitude is not being sent in sync and is sometimes corrupted
            if altitude == -1:
                altitude = oldAltitude

            # calculate the size of 10cm in the image
            scaleRuleLen = self.model.calcObjImageSize(self.scaleLength,
                self.focalLen, altitude)
            scaleRuleLen *= self.pixelsPerCM

            # find target
            target = self.model.trackTarget(frame)

            # calculate distance to target
            distVector, imgCenter = self.model.calcTargetDistance(target[3],
                frame[1], frame[2], scaleRuleLen, self.scaleLength)

            # calculate target velocity
            if (distVector[0] and oldDistVector[0]):
                deltaDistance = (oldDistVector[0] - distVector[0],
                    oldDistVector[1] - distVector[1])
            else:
                deltaDistance = (0, 0)
            curTime = time.time()

            targetVelocity = self.model.calcTargetVelocity(deltaDistance,
                curTime - oldTime)

            # display all that stuff
            self.view.showTarget(frame, target, imgCenter, distVector)
            self.view.showTargetVelocity(frame, targetVelocity)
            self.view.showFrame(frame, scaleRuleLen, target[4])

            # update old vals 
            oldAltitude = altitude
            oldTime = curTime
            oldDistVector = distVector

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
            print('WARNING: no sensor specified, defaulting to arduino')
        elif not serPort:
            print('WARNING: serial port not specified')

    Controller(Model, View, vidSrc, sensor, serPort).run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    