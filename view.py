import cv2

class View:
    """docstring for View"""
    def __init__(self):
        # all these are in pixels
        self.frameHeight = 480
        self.padding = 10
        # le colors
        self.green = (0, 255, 255)
        self.red = (55, 12, 255)


    def showFrame(self, frame, scaleRuleUnit, target):
        x, y, radius, center, mask = target
        # draw the target tracker
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), self.green, 2)
            cv2.circle(frame, center, 5, self.red, -1)

        # draw scale rule
        cv2.line(frame, (self.padding, self.frameHeight - self.padding), 
            (self.padding + int(scaleRuleUnit), 470), self.red, 2) 
        # show the mask frame
        cv2.imshow("target mask", mask)
        cv2.imshow("camera feed", frame)