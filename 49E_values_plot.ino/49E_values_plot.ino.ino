const int hallPin = A0;
const int coilPin = 5;     // MOSFET Gate Control (PWM)
int hallSignal = 0;
int pwmValue = 0;

void setup() {
  Serial.begin(115200);
  pinMode(coilPin, OUTPUT);
  digitalWrite(coilPin,HIGH);
  analogWrite(coilPin, 0);  // Start with coil off
}

void loop() {
  // Read Hall sensor
  hallSignal = analogRead(hallPin);
  
  // Check for incoming PWM commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command.startsWith("PWM:")) {
      pwmValue = command.substring(4).toInt();
      pwmValue = constrain(pwmValue, 0, 255);
      analogWrite(coilPin, pwmValue);
    }
  }
  
  // Send data in format: HALL,PWM
  Serial.print(hallSignal);
  Serial.print(",");
  Serial.println(pwmValue);

  delay(50); // 20Hz update rate
}