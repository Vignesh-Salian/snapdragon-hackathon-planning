/*
 * Smart Cold Box — MCU sketch (STM32U585, Zephyr via Arduino Core).
 *
 * In this design the Modulinos are driven from Python on the MPU over QWIIC/I2C
 * (see python/main.py), so the MCU sketch only keeps the board alive and blinks
 * the on-board LED as a heartbeat. If you prefer MCU-side sensing instead, move
 * the Modulino reads here using the C++ Modulino library and expose them over
 * Bridge RPC — but do NOT do both, or two masters will fight on the I2C bus.
 *
 * Do not touch Serial1 — it is reserved for the arduino-router Bridge link.
 */
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);
}
