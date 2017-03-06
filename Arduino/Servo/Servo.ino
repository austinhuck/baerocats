// Servo Library
#include <Servo.h>

// Creating Object
Servo servoObject;

// Pin (Switch)
int switchPin=4;
int val; // determines whether the switch is on or off
int switchState; // variable that determines the last state of the switch

// Setup
void setup()
{
  servoObject.attach(7);
  switchState=digitalRead(switchPin);
  pinMode(switchPin,INPUT);
  Serial.begin(9600);
}

// Loop (Changes Positions)
void loop()
{
  // Read the input value
  val=digitalRead(switchPin);
  
  if (val == switchState) {
    if (val == LOW) {
    // Right Position
    //servoObject.write (40);
    servoObject.writeMicroseconds (600);
    Serial.println("Low");
    delay(100);
    } 
    else {
    // Left Position
    //servoObject.write (80);
    Serial.println("High");
    servoObject.writeMicroseconds (1000);
   delay(100);
  }
  }
  delay(10);
    // New switch state
  switchState = val;
}
