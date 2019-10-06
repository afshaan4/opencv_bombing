// rangefinder using the HC-SR04 ultrasonic sensor
// MIT

const int trigger = 12;
const int echo = 11;
char input;


void setup() {
  pinMode(trigger, OUTPUT);
  pinMode(echo, INPUT);
  Serial.begin(9600);
}

void loop() {
  // yeet
}

// only send an altitude reading when asked to
void serialEvent() {
  while(Serial.available()) {
    input = (char)Serial.read();
    if (input == 'S') {
      long duration, cm; // used to calculate distance

      // send a ping
      digitalWrite(trigger, LOW); // pull it low for a clean ping
      delayMicroseconds(2);
      digitalWrite(trigger, HIGH); // send the ping
      delayMicroseconds(5);
      digitalWrite(trigger, LOW); // pull it low again

      duration = pulseIn(echo, HIGH);
      cm = microsecondsToCentimeters(duration);

      Serial.println(cm);
    }
  }
}

long microsecondsToCentimeters(long microseconds) {
  // The speed of sound is 340 m/s or 29 microseconds per centimeter.
  // The ping travels out and back, so to find the distance of the
  // object we take half of the distance traveled.
  return microseconds /29 / 2;
}
