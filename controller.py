import sys
import time
import argparse
import cv2
from model import Model
from view import View

class Controller:
    """The main program loop"""
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
        bombEnabled = False
        running = True
        hit = False
        try:
            if self.headless:
                self.view.startCurses()
            while running:
                ################################################################
                # Get data
                ################################################################
                frame = self.model.getFrame()
                imgCenter = (int(frame[1] / 2), int(frame[2] / 2))
                altitude = self.model.getAltitude()
                # altitude is sometimes corrupted
                if altitude == -1:
                    altitude = oldAltitude

                ################################################################
                # Do calculations
                ################################################################
                # calculate the size of 10cm in the image, we use this
                # to do all measurements
                scaleRuleLen = self.model.calcObjImageSize(
                    self.scaleLength, self.focalLen, altitude)
                scaleRuleLen *= self.pixelsPerCM

                # find target and calculate distance to it
                target = self.model.trackTarget(frame)
                distVector = self.model.calcTargetDistance(
                    target[3], imgCenter, scaleRuleLen, self.scaleLength)

                # calculate target velocity
                if (distVector[0] and oldDistVector[0]):
                    deltaDistance = (oldDistVector[0] - distVector[0],
                                     oldDistVector[1] - distVector[1])
                else:
                    deltaDistance = (0, 0)

                curTime = time.time()
                targetVelocity = self.model.calcTargetVelocity(
                    deltaDistance, curTime - oldTime)

                # calculate the range of the "bomb"
                bombRange = self.model.calcBombRange(altitude, targetVelocity)
                # attempt to drop the "bomb"
                if bombEnabled:
                    hit = self.model.hit(bombRange, target, imgCenter)

                ################################################################
                # display calls and "event handlers"
                ################################################################
                if self.headless:
                    self.view.printData(targetVelocity, distVector, altitude,
                                        target, bombRange, hit, bombEnabled)

                    headlessKeyEvent = self.view.checkKeys()
                    if (headlessKeyEvent == ord("q")):
                        # quit headless mode
                        self.view.closeCurses()
                        self.model.cleanGpio()
                        running = False

                    if (headlessKeyEvent == ord("e")):
                        # "bombs" hot
                        bombEnabled = True
                else:
                    self.view.showTarget(frame, target, imgCenter, bombRange)
                    self.view.showTargetData(frame, targetVelocity, distVector)
                    self.view.showFrame(frame, scaleRuleLen)

                    keyEvent = cv2.waitKey(30)
                    if keyEvent == 27:
                        # quit gui mode
                        self.model.cleanGpio()
                        running = False
                    elif keyEvent == ord("e"):
                        # enable "bomb"
                        bombEnabled = True

                # update old values
                oldAltitude = altitude
                oldTime = curTime
                oldDistVector = distVector

        except (KeyboardInterrupt, AttributeError) as e:
            # always clean up before crashing
            if self.headless:
                self.view.closeCurses()
            self.model.cleanGpio()
            raise e


def main():
    parser = argparse.ArgumentParser(description = 'drop bombs on the haters')
    parser.add_argument(
        '-v', '--video-src', type = int, default = 0, help = 'which camera to use')
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
