# opencv_bombing

All units are in centimeters

## Running it:

* execute `controller.py` with these arguments:
  ```bash
  python3 controller.py <camera> <sensor mode> <serial port>
  # like:
  python3 controller.py 2 1 /dev/ttyACM0
  ```

## Documentation:

* Camera parameters:
  all distance and speed measurements depend on knowing the focal length and the
  pixels per centimeter of you camera make sure you change these values:
  `self.focalLen` and `self.pixelsPerCM`

* **The altitude sensor:**
  There are two ways to get altitude readings, an arduino with an ultrasonic sensor
  and an ultrasonic sensor *directly* connected to the raspberry pi.

  - The first mode(arduino) is just for testing with a laptop when using it you
    have to specify a serial port to which the arduino is connected, don't use 
    it for a "deployed" setup its too slow.

  - The second mode is for when the thing is being used, its fast.
