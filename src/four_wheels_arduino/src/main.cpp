#include <Arduino.h>
// 
float left_vel = 0.0f;
float right_vel = 0.0f;
float left_position_vel = 0.0f;
float right_position_vel = 0.0f;
unsigned long last_time = 0;

int IN1 = 3;
int IN2 = 4;
int IN3 = 5;
int IN4 = 6;
int ENA = 9;
int ENB = 10;

void setup() {
  Serial.begin(115200);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  while (!Serial) {
  }

  last_time = millis();
}

void loop() {
  // Read latest command if available
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');

    int comma = line.indexOf(',');

    if (comma != -1) {
      left_vel = line.substring(0, comma).toFloat();
      right_vel = line.substring(comma + 1).toFloat();
    }
  }
	analogWrite(ENA, left_vel*10);
	digitalWrite(IN1, HIGH);
	digitalWrite(IN2, LOW);

  analogWrite(ENB, right_vel*10);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);


  float left_position = 0.0f;
  float right_position = 0.0f;
  right_position_vel += 1;
  left_position_vel += 1;
  // Send feedback
  Serial.print(left_position, 3);
  Serial.print(",");
  Serial.print(left_vel, 3);
  Serial.print(",");
  Serial.print(right_position, 3);
  Serial.print(",");
  Serial.println(right_vel, 3);

  delay(20);
}
