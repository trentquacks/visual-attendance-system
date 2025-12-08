#include <Servo.h>

Servo myservo; 

int open_pos = 0;    
int close_pos = 90;

void setup() {
  Serial.begin(9600);
  myservo.attach(9);
  myservo.write(close_pos);
}

void loop() {
  if (Serial.available() > 0) {
    String msg = Serial.readString();

    if (msg == "OPEN") {
      myservo.write(open_pos);
      delay(5000);
      myservo.write(close_pos);
    }
  }
}
