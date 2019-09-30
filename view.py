import cv2

class View:
    """stuff that displays things"""
    def __init__(self):
        self.padding = 10
        self.green = (0, 255, 255)
        self.red = (55, 12, 255)
        self.blue = (255, 55, 0)
        self.black = (0, 0, 0)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontColor = (255, 255, 255)
        self.fontLine = cv2.LINE_AA


    # draw text with an outline, so you can see it on any background
    def drawText(self, image, location, text):
        x, y = location
        cv2.putText(image, text, (x + 1, y + 1), self.font, 0.4, self.black,
            thickness = 2, lineType = self.fontLine)
        cv2.putText(image, text, (x, y), self.font, 0.4, self.fontColor,
            lineType = self.fontLine)


    # prints data out for headless mode
    def printData(self, velocity, distVector, altitude, target):
        center = target[3]
        radius = target[2]
        velocity = (round(velocity[0], 1), round(velocity[1], 1))
        if distVector[0]:
            distVector = (int(distVector[0]), int(distVector[1]))

        if radius > 10:
            print("pos:{}    alt:{}    vel:{}    dist:{}".format(center,
                altitude, velocity, distVector))
        else:
            print("pos:{}    alt:{}    vel:{}    dist:{}".format(None, altitude,
                None, None))


    # draws a line from the center of the image to the target, draws a circle
    # around the target
    def showTarget(self, frame, target, imgCenter):
        image = frame[0]
        x, y, radius, center = target

        if radius > 10:
            # draw the line to the target
            cv2.line(image, imgCenter, center, self.blue, 2)
            cv2.circle(image, imgCenter, 2, self.green, -1)  
            # draw the target tracker
            cv2.circle(image, (int(x), int(y)), int(radius), self.green, 2)
            cv2.circle(image, center, 5, self.red, -1)


    def showTargetData(self, frame, velocity, distVector):
        image = frame[0]
        textPos1 = (self.padding, self.padding * 2)
        textPos2 = (self.padding, self.padding * 4)
        if distVector[0]:
            distVector = (int(distVector[0]), int(distVector[1]))
        velocity = (round(velocity[0], 1), round(velocity[1], 1))
        self.drawText(image, textPos1, "target distance " + str(distVector) + "cm")
        self.drawText(image, textPos2, "target velocity " + str(velocity) + "cm/s")


    def showFrame(self, frame, scaleRuleLen):
        image, imageWidth, imageHeight = frame
        textPos = (self.padding - 5, imageHeight - self.padding)
        # draw scale rule
        self.drawText(image, textPos, "10cm:")
        cv2.line(image, (self.padding * 6, imageHeight - self.padding),
            (self.padding * 6 + int(scaleRuleLen), imageHeight - self.padding), self.red, 2) 
        cv2.imshow("camera feed", image)
        