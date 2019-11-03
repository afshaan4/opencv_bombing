# opencv_bombing

All units are in centimeters

## Using it:

* **Install dependencies:**
  If you are using a pi just `pip3 install -r requirements.txt`, it'll get:

  * opencv 3+
  * imutils
  * Rpi.GPIO

  If you are not using a pi then get:

  * opencv 3+
  * imutils
  * pyserial


* **Running it**
  execute `controller.py` with these arguments:
  ```sh
  python3 controller.py -v <camera> -s <sensor_mode> <serial port> --headless
  # the third argument is only needed when using sensor mode 1(arduino)
  # with sensor mode 1:
  python3 controller.py -v 2 -s 1 /dev/ttyACM0
  # sensor mode 2, headless:
  python3 controller.py -v 2 -s 2 --headless
  ```

## Documentation:

* **Camera parameters:**
  All distance and speed measurements depend on knowing the focal length 
  and the pixels per centimeter of your camera, make sure you change these
  values to those of your camera, they're in `controller.py`: 

  * `self.focalLen` 
  * `self.pixelsPerCM`

* **The altitude sensor:**
  There are two ways to get altitude readings: an arduino with an ultrasonic
  sensor and an ultrasonic sensor *directly* connected to the raspberry pi.

  - Mode 1 is for when you don't have a raspberry pi.
    Here altitude is read from an arduino that is running `rangefinder.ino`,
    when using this mode you have to specify a serial port to which the 
    arduino is connected.

  - Mode 2 is for use with a raspberry pi, it gets altitude readings 
    directly from a sensor connected to the Pi's GPIO.

  The sensor I am using(HC-SR04) has a max range of 4 meters, for a practical
  setup use a LIDAR with enough range.

* **The target:**
  The "target" to drop the "bomb" on is identified by color, the program just 
  looks for a circle of the color specified in `model.py`: 
  ```
  # limits of target color acceptable
        self.targetClrLower = (29, 86, 6)
        self.targetClrHigher = (64, 255, 255)
  ```

## The maths:

* **Measuring distances:**
  First figure out how big 10 centimeters is on the image plane,
  that calculation is: 

  ```size_in_image = actual_size * focal_length / distance```

  then to convert that to pixels: 
  ```10_cm_in_image = size_in_image * pixels_per_cm```
  where `pixels_per_cm` is the your cameras pixel density.

  Then you can measure distances in the image with `10_cm_in_image`.

* **Calculating where the "bomb" will land:**
  Where the bomb will fall is calculated with this projectile range equation:

  ![range](https://wikimedia.org/api/rest_v1/media/math/render/svg/e74be30b3ea8179e1fa1f8ac9f0315f0b8fae6f4)

  It takes the altitude(`y0`) of the "bomb", the angle the "bomb" is dropped at
  which is zero ,and the velocity(`v`) of the "bomb", the velocity of the 
  "bomb" is just the velocity of the target in the opposite direction.
  This is done for both axes and we get a vector of where the bomb lands.
  
  *the equation is from this wiki: https://en.wikipedia.org/wiki/Range_of_a_projectile#Uneven_ground*