import cv2
import curses

class View:
    """UI methods"""
    def __init__(self):
        self.padding = 10
        self.green = (0, 255, 255)
        self.red = (55, 12, 255)
        self.blue = (255, 55, 0)
        self.black = (0, 0, 0)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontColor = (255, 255, 255)
        self.fontLine = cv2.LINE_AA

    #Headless mode##############################################################

    def startCurses(self):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True) # nonblocking user input
        curses.noecho()
        curses.cbreak()

    def closeCurses(self):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    # prints data out
    def printData(self, velocity, distVector,
                  altitude, target, bombRange, hit, bombEnabled):
        center = target[3]
        radius = target[2]
        velocity = (round(velocity[0], 2), round(velocity[1], 2))
        bombRange = (round(bombRange[0], 2), round(bombRange[1], 2))
        if distVector[0]:
            distVector = (int(distVector[0]), int(distVector[1]))

        # display everything
        self.stdscr.erase()
        self.stdscr.addstr(1, 1, "target position: {}".format(center))
        self.stdscr.addstr(2, 1, "target velocity: {}".format(velocity))
        self.stdscr.addstr(3, 1, "bomb range: {}".format(bombRange))
        self.stdscr.addstr(4, 1, "altitude: {}".format(int(altitude)))
        self.stdscr.addstr(5, 1, "bomb hit: {}".format(hit))
        self.stdscr.addstr(6, 1, "target distance: {}".format(distVector))
        self.stdscr.addstr(8, 1, "bomb Enabled: {}".format(bombEnabled))
        self.stdscr.refresh()

    # lol just return keyEvents
    def checkKeys(self):
        return self.stdscr.getch()

    #GUI mode###################################################################

    # draw text with an outline, so you can see it on any background
    def drawText(self, image, location, text):
        x, y = location
        cv2.putText(image, text, (x + 1, y + 1), self.font, 0.4, self.black,
                    thickness = 2, lineType = self.fontLine)
        cv2.putText(image, text, (x, y), self.font, 0.4, self.fontColor,
                    lineType = self.fontLine)

    # outline target and draw "bomb" trajectory
    def showTarget(self, frame, target, imgCenter, bombRange):
        image = frame[0]
        x, y, radius, targetCenter = target

        cv2.circle(image, imgCenter, 2, self.green, -1)
        # only show stuff if there is a target
        if x:
            bombLand = (imgCenter[0] + int(bombRange[0]),
                        imgCenter[1] + int(bombRange[1]))
            # draw a line from the center to where the "bomb" will land
            cv2.line(image, imgCenter, bombLand, self.blue, 2)
            # draw the target tracker
            cv2.circle(image, (int(x), int(y)), int(radius), self.green, 2)
            cv2.circle(image, targetCenter, 5, self.red, -1)

    # show targets velocity distance on the image
    def showTargetData(self, frame, velocity, distVector):
        image = frame[0]
        textPos1 = (self.padding, self.padding * 2)
        textPos2 = (self.padding, self.padding * 4)
        velocity = (round(velocity[0], 1), round(velocity[1], 1))
        if type(distVector[0]) == float:
            distVector = (int(distVector[0]), int(distVector[1]))

        self.drawText(image, textPos1, "target distance " + str(distVector) + "cm")
        self.drawText(image, textPos2, "target velocity " + str(velocity) + "cm/s")

    def showFrame(self, frame, scaleRuleLen):
        image, imageWidth, imageHeight = frame
        textPos = (self.padding - 5, imageHeight - self.padding)
        # draw scale rule
        self.drawText(image, textPos, "10cm:")
        cv2.line(image, (self.padding * 6, imageHeight - self.padding),
                (self.padding * 6 + int(scaleRuleLen), imageHeight
                - self.padding), self.red, 2)
        cv2.imshow("camera feed", image)
