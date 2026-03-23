// Real-Time Magnetic Interference Cancellation for Magnetic Levitator
// MOSFET gate (coilPin) kept LOW during setup for safety.
// Outputs to Serial: Raw_Hall,Calculated_Offset,Clean_Signal

const int hallPin = A0;    // SS49E Hall sensor
const int coilPin = 5;     // MOSFET Gate Control (PWM)
int pwmValue = 0;          // current PWM (0-255)

// Full baseline lookup table derived from measured data (no ball present)
// Index == PWM value, entry == average raw ADC from CSV measurements
const int offsetTable[256] = {
  526,526,526,526,526,526,526,526,526,526, // 0-9
  526,526,525,525,525,525,525,525,524,524, // 10-19
  523,523,523,522,521,521,520,520,519,519, // 20-29
  518,517,516,516,515,514,514,513,512,511, // 30-39
  511,510,509,508,507,507,506,505,504,504, // 40-49
  503,502,501,500,499,499,498,497,496,496, // 50-59
  495,494,493,492,491,490,489,489,488,487, // 60-69
  486,485,484,484,483,482,481,480,480,478, // 70-79
  478,477,476,475,474,473,473,471,471,470, // 80-89
  469,468,467,466,465,465,464,463,462,461, // 90-99
  460,460,459,458,457,456,455,454,453,452, // 100-109
  451,451,450,449,448,447,446,445,444,444, // 110-119
  442,442,441,440,439,438,437,436,436,434, // 120-129
  434,433,432,431,430,429,428,427,426,425, // 130-139
  425,424,423,422,421,420,419,418,417,416, // 140-149
  416,415,414,413,412,411,410,409,408,407, // 150-159
  407,406,405,404,403,402,401,400,399,398, // 160-169
  398,397,396,395,394,393,392,391,390,389, // 170-179
  388,388,386,386,385,384,383,382,381,380, // 180-189
  379,378,377,376,376,374,374,373,372,371, // 190-199
  370,369,368,367,366,365,364,364,363,362, // 200-209
  361,360,359,358,357,356,355,354,354,353, // 210-219
  352,351,350,349,348,347,346,345,344,343, // 220-229
  342,342,341,340,339,338,337,336,335,335, // 230-239
  334,333,332,331,330,329,328,327,326,325, // 240-249
  325,324,323,322,321,320                                   // 250-255
};

// Return expected offset from lookup table, smoothed with a 5-sample moving average and returned as integer
int calcOffset(int pwm) {
  if (pwm < 0) pwm = 0;
  if (pwm > 255) pwm = 255;
  const int radius = 2; // window radius for smoothing (2 on each side => 5 samples)
  int start = pwm - radius;
  int end = pwm + radius;
  if (start < 0) start = 0;
  if (end > 255) end = 255;
  long sum = 0;
  int count = 0;
  for (int i = start; i <= end; i++) {
    sum += offsetTable[i];
    count++;
  }
  // round to nearest integer
  int avg = (int)(sum / (float)count + 0.5);
  return avg;
}

void setup() {
  // Safety: ensure MOSFET gate is LOW while initializing
  pinMode(coilPin, OUTPUT);
  digitalWrite(coilPin, LOW);    // keep gate low
  analogWrite(coilPin, 0);

  pinMode(hallPin, INPUT);
  Serial.begin(115200);
  while (!Serial) { ; } // wait for serial

  // Provide header for serial output
  Serial.println("Raw_Hall,Calculated_Offset,Clean_Signal");
}

void loop() {
  // Optional: allow setting PWM over serial by sending an integer (0-255)
  if (Serial.available() > 0) {
    String s = Serial.readStringUntil('\n');
    s.trim();
    if (s.length() > 0) {
      int v = s.toInt();
      if (v >= 0 && v <= 255) {
        pwmValue = v;
      }
    }
  }

  // Apply PWM to coil
  analogWrite(coilPin, pwmValue);

  // Read raw hall sensor (ADC 0-1023)
  int rawHall = analogRead(hallPin);

  // Calculate expected offset for current PWM
  float expectedOffset = calcOffset(pwmValue);

  // Produce clean signal by subtracting offset; should be ~0 when no ball present
  float cleanSignal = (float)rawHall - expectedOffset;

  // Print values to Serial monitor
  Serial.print(rawHall);
  Serial.print(",");
  Serial.print(expectedOffset, 2);
  Serial.print(",");
  Serial.println(cleanSignal, 2);

  delay(50); // 20 Hz update rate
}
