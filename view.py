import cv2

class View:
    """docstring for View"""
    def __init__(self):
        pass


    def showFrame(self, frame, scaleRuleUnit):
        # image ,start, end, color, width
        cv2.line(frame, (10, 470), (10 + int(scaleRuleUnit), 470), (55, 12, 255), 2) 
        cv2.imshow("camera feed", frame)