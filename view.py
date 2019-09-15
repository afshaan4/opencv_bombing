import cv2

class View:
    """docstring for View"""
    def __init__(self):
        # in pixels
        self.padding = 10
        # le colors
        self.green = (0, 255, 255)
        self.red = (55, 12, 255)
        self.blue = (255, 55, 0)

    def showDistance(self, frame, targetCenter, imgCenter):
        image = frame[0]
        cv2.line(image, imgCenter, targetCenter, self.blue, 2)
        cv2.circle(image, imgCenter, 2, self.green, -1)


    def showTarget(self, frame, target):
        image = frame[0]
        x, y, radius, center, mask = target
        # draw the target tracker
        if radius > 10:
            cv2.circle(image, (int(x), int(y)), int(radius), self.green, 2)
            cv2.circle(image, center, 5, self.red, -1)


    def showFrame(self, image, scaleRuleUnit, mask):
        frame, imageHeight, imageWidth = image
        # draw scale rule
        cv2.line(frame, (self.padding, imageHeight - self.padding), 
            (self.padding + int(scaleRuleUnit), imageHeight - self.padding), self.red, 2) 

        # show the mask and frame
        cv2.imshow("target mask", mask)
        cv2.imshow("camera feed", frame)