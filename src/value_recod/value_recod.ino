// =============================================================
//  Magnetic Levitator – Hall Sensor Recorder
//  6-sweep sequence: Up1, Down1, Up2, Down2, Up3, Down3
//
//  Each reading is streamed live as:  <label>,<pwm>,<hall>
//  No storage arrays on the Arduino – all CSV work done by
//  the companion Python script (hall_recorder.py) on the PC.
//
//  Trigger : runcheck"<voltage>"   e.g.  runcheck"12.5"
//  Stream  : Up1,0,512  /  Down1,255,498  / …
// =============================================================

const int hallPin  = A0;
const int coilPin  = 5;   // MOSFET Gate Control (PWM)

// ---------- Tuning parameters ----------
const int  SETTLE_MS  = 100; // ms to wait after setting each PWM value
const int  SAMPLES    = 5;   // Hall readings averaged per step
const int  STEP_SIZE  = 1;   // PWM increment (1 = full resolution)
// ---------------------------------------

float testVoltage = 0.0;

// ---- Forward declarations ----
void runTest();
void sweepUp(const char* label);
void sweepDown(const char* label);
int  readHall();

// ==============================
void setup() {
  Serial.begin(115200);
  pinMode(coilPin, OUTPUT);
  analogWrite(coilPin, 0);  // Coil off at start

  Serial.println(F("Magnetic Levitator – Hall Recorder ready."));
  Serial.println(F("Send:  runcheck\"<voltage>\"  e.g.  runcheck\"12.5\""));
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // Parse:  runcheck"12.5"
    if (cmd.startsWith("runcheck\"")) {
      int qStart = cmd.indexOf('"') + 1;
      int qEnd   = cmd.lastIndexOf('"');

      if (qStart > 0 && qEnd > qStart) {
        testVoltage = cmd.substring(qStart, qEnd).toFloat();
        runTest();
      } else {
        Serial.println(F("ERROR: Bad format. Expected runcheck\"12.5\""));
      }
    }
  }
}

// ---- Average several Hall readings to reduce noise ----
int readHall() {
  long sum = 0;
  for (int i = 0; i < SAMPLES; i++) {
    sum += analogRead(hallPin);
    delay(10);
  }
  return (int)(sum / SAMPLES);
}

// ---- Sweep PWM 0 → 255, stream label,pwm,hall each step ----
void sweepUp(const char* label) {
  for (int pwm = 0; pwm <= 255; pwm += STEP_SIZE) {
    analogWrite(coilPin, pwm);
    delay(SETTLE_MS);
    Serial.print(label);    Serial.print(F(","));
    Serial.print(pwm);      Serial.print(F(","));
    Serial.println(readHall());
  }
}

// ---- Sweep PWM 255 → 0, stream label,pwm,hall each step ----
void sweepDown(const char* label) {
  for (int pwm = 255; pwm >= 0; pwm -= STEP_SIZE) {
    analogWrite(coilPin, pwm);
    delay(SETTLE_MS);
    Serial.print(label);    Serial.print(F(","));
    Serial.print(pwm);      Serial.print(F(","));
    Serial.println(readHall());
  }
}

// ---- Run all 6 sweeps, streaming readings live ----
void runTest() {
  Serial.print(F("TEST START | Voltage = "));
  Serial.print(testVoltage, 2);
  Serial.println(F(" V"));
  Serial.println(F("##DATA_START##"));

  Serial.println(F("#Sweep 1/6 Up1"));   sweepUp("Up1");
  Serial.println(F("#Sweep 2/6 Down1")); sweepDown("Down1");
  Serial.println(F("#Sweep 3/6 Up2"));   sweepUp("Up2");
  Serial.println(F("#Sweep 4/6 Down2")); sweepDown("Down2");
  Serial.println(F("#Sweep 5/6 Up3"));   sweepUp("Up3");
  Serial.println(F("#Sweep 6/6 Down3")); sweepDown("Down3");

  analogWrite(coilPin, 0);  // Safety: coil off
  Serial.println(F("##DATA_END##"));
  Serial.println(F("Ready. Send runcheck\"<voltage>\" for another test."));
}