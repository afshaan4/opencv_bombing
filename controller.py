from model import Model
from view import View
import cv2
import sys
import time
import argparse

class Controller:
    """docstring for Controller"""
    def __init__(self, model, view, videoSrc, sensor, serialPort, headless):
        self.model = model(videoSrc, int(sensor), serialPort)
        self.view = view()
        # size of unit for scale rule in cm
        # this is what we will measure everything in the image with
        self.scaleLength = 10
        # camera parameters, change these for your camera
        self.focalLen = 0.6
        self.pixelsPerCM = 1950
        self.headless = headless


    def run(self):
        oldAltitude = 0
        oldTime = 0
        oldDistVector = (0, 0)
        running = True
        while running:
            # get all the data
            frame = self.model.getFrame()
            altitude = self.model.getAltitude()
            # altitude is sometimes corrupted
            if altitude == -1:
                altitude = oldAltitude

            # calculate the size of 10cm in the image
            scaleRuleLen = self.model.calcObjImageSize(self.scaleLength,
                self.focalLen, altitude)
            scaleRuleLen *= self.pixelsPerCM

            # find target and calculate distance to it
            target = self.model.trackTarget(frame)
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

            # calculate the range of the bomb
            bombRange = self.model.calcBombRange(altitude, (-targetVelocity[0],
                -targetVelocity[1]))

            # display all that stuff
            if self.headless:
                self.view.printData(targetVelocity, distVector, altitude, 
                    target, bombRange)
            else:
                self.view.showTarget(frame, target, imgCenter)
                self.view.showTargetData(frame, targetVelocity, distVector)
                self.view.showFrame(frame, scaleRuleLen)

            # update old values
            oldAltitude = altitude
            oldTime = curTime
            oldDistVector = distVector

            # yeet outta here
            keyEvent = cv2.waitKey(30)
            if keyEvent == 27:
                running = False


def main():
    parser = argparse.ArgumentParser(description = 'drop bombs on the haters')
    parser.add_argument(
        '-v', '--video-src', type = int, default = 0, help = 'video source')
    parser.add_argument(
        '-s', '--sensor', type = int, default = 2, help = 'altitude sensor mode')
    parser.add_argument(
        'serPort', nargs = '?', metavar = 'serial port', default = None,
        help = 'serial port that the arduino is connected to')
    parser.add_argument(
        '--headless', action = 'store_true', help = 'disable GUI')
    args = parser.parse_args()


    Controller(Model, View, args.video_src, args.sensor, args.serPort,
        args.headless).run()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
