# opencv_bombing

All units are in centimeters

## Running it:

* execute `controller.py` with these arguments:
  ```bash
  python3 controller.py -v camera -s sensor_mode <serial port> --headless
  # the third argument is only needed when using sensor mode 1(arduino)
  # with sensor mode 1:
  python3 controller.py -v 2 -s 1 /dev/ttyACM0
  # sensor mode 2:
  python3 controller.py -v 2 -s 2
  ```

## Documentation:

* **Camera parameters:**
  all distance and speed measurements depend on knowing the focal length and the
  pixels per centimeter of your camera, make sure you change these values:
  `self.focalLen` and `self.pixelsPerCM`

* **The altitude sensor:**
  There are two ways to get altitude readings, an arduino with an ultrasonic
  sensor and an ultrasonic sensor *directly* connected to the raspberry pi.

  - The first mode(arduino) is just for testing with a laptop when using it you
    have to specify a serial port to which the arduino is connected, don't use 
    it for a "deployed" setup its too slow.

  - The second mode is for when the thing is being used, its fast.
