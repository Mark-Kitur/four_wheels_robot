#include <Arduino.h>
// 
float left_position = 0.0;
float left_velocity = 0.0;
float right_position = 0.0;
float right_velocity = 0.0;

void setup() {
  Serial.begin(115200);
// Example values (replace with your encoder readings)
  
  // Wait for the serial port (useful on boards with native USB)
  while (!Serial) {
  }
}

void loop() {
  float left;
    float right;


if (Serial.available())
{
    String line = Serial.readStringUntil('\n');

        if (sscanf(line.c_str(), "%f,%f",
               &left, &right) == 2)
    {
        // Drive motors
    }
}
  Serial.print(left);
  Serial.print(",");

  // Serial.print(left_velocity);
  // Serial.print(",");

  // Serial.print(right_position);
  // Serial.print(",");

  Serial.println(right);

  delay(20);   // 50 Hz
}