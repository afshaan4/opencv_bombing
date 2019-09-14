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
            ################################
            # get all the data
            ################################
            ret, frame = self.model.getFrame()
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

            target = self.model.trackTarget(frame)
            
            self.view.showFrame(frame, scaleRuleUnit, target)

            # yeet outta here
            keyEvent = cv2.waitKey(30)
            if keyEvent == 27:
                # TODO: destroy windows
                running = False


def main():
    try:
        vidSrc = sys.argv[1]
        serPort = sys.argv[2]
    except:
        vidSrc = 0
        print('WARNING: serial port not specified')

    Controller(Model, View, vidSrc, serPort).run()

if __name__ == '__main__':
    main()