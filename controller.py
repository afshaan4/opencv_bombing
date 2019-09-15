from model import Model
from view import View
import cv2
import sys

class Controller:
    """docstring for Controller"""
    def __init__(self, model, view, videoSrc, serialPort):
        self.model = model(videoSrc, serialPort)
        self.view = view()
        # camera parameters, change these for your camera
        self.scaleUnit = 10 # size of unit for scale rule in cm
        self.focalLen = 0.6
        self.pixelsPerCM = 1950


    def run(self):
        oldDistance = 0
        running = True
        while running:
            # get all the data
            frame = self.model.getFrame()
            distance = self.model.getDistance()

            # coz distance is not being sent in sync and is sometimes corrupted
            if distance == -1:
                distance = oldDistance
            else:
                oldDistance = distance

            # calculate the size of 10cm in the image
            scaleRuleUnit = self.model.calcScaleRuleUnit(self.scaleUnit,
                self.focalLen, distance)
            scaleRuleUnit *= self.pixelsPerCM

            # find target
            target = self.model.trackTarget(frame)

            # calculate distance to target
            distVector, imgCenter = self.model.calcTargetDistance(target[3],
                frame[1], frame[2])

            # display all that stuff
            self.view.showDistance(frame, target[3], imgCenter)
            self.view.showTarget(frame, target)
            self.view.showFrame(frame, scaleRuleUnit, target[4])

            # yeet outta here
            keyEvent = cv2.waitKey(30)
            if keyEvent == 27:
                running = False


def main():
    try:
        vidSrc = sys.argv[1]
        serPort = sys.argv[2]
    except:
        vidSrc = 0
        print('WARNING: serial port not specified')

    Controller(Model, View, vidSrc, serPort).run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()