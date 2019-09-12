import cv2
import sys
import re
import imutils
import numpy as np

class App:
    def __init__(self, videoSrc):
        # limits of green acceptable
        self.greenLower = (29, 86, 6)
        self.greenUpper = (64, 255, 255)

        '''
         handle getting the camera
         done like this coz we need the size of the frame
        '''
        source = str(videoSrc).strip()
        # Win32: handle drive letter ('c:', ...)
        source = re.sub(r'(^|=)([a-zA-Z]):([/\\a-zA-Z0-9])', r'\1?disk\2?\3', source)
        chunks = source.split(':')
        chunks = [re.sub(r'\?disk([a-zA-Z])\?', r'\1:', s) for s in chunks]

        source = chunks[0]
        try: source = int(source)
        except ValueError: pass
        params = dict( s.split('=') for s in chunks[1:] )

        self.cam = cv2.VideoCapture(source)
        # add size to capture
        if 'size' in params:
            w, h = map(int, params['size'].split('x'))
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)


    def run(self):
        running = True
        while running:
            ret, frame = self.cam.read()
            # resize, blur, convert to HSV colorspace
            frame = imutils.resize(frame, width=600)
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            # make a mask for green and remove small blobs that are noise
            mask = cv2.inRange(hsv, self.greenLower, self.greenUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            cv2.imshow('BOOOO', mask)

            # find contours in the mask and try to find the ball
            cntrs = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE)
            cntrs = imutils.grab_contours(cntrs)
            center = None

            if len(cntrs) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cntrs, key = cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                print(center) # remove

                # only select if the ball is bigg enough
                if radius > 10:
                    # draw circle and centroid
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)


            cv2.imshow("BRUH", frame)
            k = cv2.waitKey(30)
            if k == 27:
                running = False


def main():
    try:
        videoSrc = sys.argv[1]
    except:
        videoSrc = 0

    App(videoSrc).run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()