/**
 * @file smart_cold_box.ino
 * @brief HemaGrid AI - Smart Cold Box Firmware
 * 
 * Production-quality, non-blocking firmware for monitoring blood shipments.
 * Polling uses timer intervals rather than blocking delays. State logic 
 * evaluates environmental conditions and serializes status as JSON over UART.
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <DHT.h>

// --- Configuration & Constants ---
#define SERIAL_BAUD         115200
#define DEVICE_ID           "cold_box_001"

// Pin Configurations
#define PIN_DHT             2
#define PIN_LED_GREEN       8
#define PIN_LED_YELLOW      9
#define PIN_LED_RED         10
#define PIN_BUZZER          11

// Sensor Type
#define DHTTYPE             DHT22

// Timing Intervals (milliseconds)
#define POLLING_INTERVAL    1000  // Read sensors every 1 second
#define ALERT_TONE_INTERVAL  500  // Buzzer oscillation rate in alarm

// Environmental Thresholds
const float TEMP_SAFE_MIN   = 2.0;   // Clinical blood refrigeration bottom limit
const float TEMP_SAFE_MAX   = 6.0;   // Clinical blood refrigeration top limit
const float TEMP_WARN_MAX   = 8.0;   // Upper warning limit before compromise

const float ACCEL_WARN_MAX  = 1.5;   // Warning vibration threshold (g)
const float ACCEL_COMP_MAX  = 3.0;   // Compromising impact threshold (g)

// --- Types & Enums ---
enum DeviceState {
  STATE_SAFE,
  STATE_WARNING,
  STATE_COMPROMISED
};

struct TelemetryData {
  float temperature_c;
  float humidity_pct;
  float acceleration_g;
  float max_impact_g;
};

struct StatusFlags {
  bool temp_breached;
  bool impact_breached;
};

// --- Global Variables ---
DHT dht(PIN_DHT, DHTTYPE);
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

TelemetryData currentTelemetry = {0.0, 0.0, 0.0, 0.0};
StatusFlags currentFlags = {false, false};
DeviceState currentState = STATE_SAFE;

unsigned long lastPollTime = 0;
unsigned long lastBuzzerToggle = 0;
bool buzzerActive = false;

// --- Function Prototypes ---
void initPins();
void initSensors();
void pollSensors();
void evaluateState();
void updateIndicators();
void serializeTelemetry();

// --- Initialization ---
void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    ; // Wait for serial port to connect (required for native USB boards)
  }

  initPins();
  initSensors();
}

// --- Main Loop ---
void loop() {
  unsigned long currentTime = millis();

  // Non-blocking timer for polling sensors
  if (currentTime - lastPollTime >= POLLING_INTERVAL) {
    lastPollTime = currentTime;
    pollSensors();
    evaluateState();
    serializeTelemetry();
  }

  // Active indicators and buzzer alert management
  updateIndicators();
}

// --- Helper Functions ---

void initPins() {
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  // Initial indicator state (All off)
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_BUZZER, LOW);
}

void initSensors() {
  dht.begin();

  // Initialize ADXL345 Accelerometer
  if (!accel.begin()) {
    // If the accelerometer fails to mount, write a critical error packet
    Serial.println(F("{\"error\": \"ADXL345 connection failed. Check wiring.\"}"));
    while (1) {
      // Lock up and blink Red LED to indicate hardware failure
      digitalWrite(PIN_LED_RED, HIGH);
      delay(200);
      digitalWrite(PIN_LED_RED, LOW);
      delay(200);
    }
  }

  // Set sensor scale
  accel.setRange(ADXL345_RANGE_16_G);
}

void pollSensors() {
  // 1. Read DHT22 Temperature & Humidity
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (!isnan(temp)) {
    currentTelemetry.temperature_c = temp;
  }
  if (!isnan(hum)) {
    currentTelemetry.humidity_pct = hum;
  }

  // 2. Read ADXL345 Accelerometer
  sensors_event_t event;
  accel.getEvent(&event);

  // Calculate overall magnitude: G = sqrt(x^2 + y^2 + z^2) / 9.80665
  float x_g = event.acceleration.x / 9.80665;
  float y_g = event.acceleration.y / 9.80665;
  float z_g = event.acceleration.z / 9.80665;
  
  float magnitude = sqrt((x_g * x_g) + (y_g * y_g) + (z_g * z_g));

  // Filter out normal gravity constant (~1g) to isolate dynamic shock forces
  float shock = abs(magnitude - 1.0);
  currentTelemetry.acceleration_g = shock;

  // Track the absolute maximum shock encountered
  if (shock > currentTelemetry.max_impact_g) {
    currentTelemetry.max_impact_g = shock;
  }
}

void evaluateState() {
  // Evaluate Temperature Bounds
  if (currentTelemetry.temperature_c > TEMP_WARN_MAX || currentTelemetry.temperature_c < TEMP_SAFE_MIN) {
    currentFlags.temp_breached = true;
  } else if (currentTelemetry.temperature_c > TEMP_SAFE_MAX) {
    // Falls between 6.0 and 8.0 -> Trigger local warning, but not a full compromise
    currentFlags.temp_breached = false; 
  } else {
    currentFlags.temp_breached = false;
  }

  // Evaluate Impact Bounds
  if (currentTelemetry.max_impact_g >= ACCEL_COMP_MAX) {
    currentFlags.impact_breached = true;
  }

  // Determine Overall State
  // COMPROMISED state is sticky: once breached, it requires a physical reset
  if (currentFlags.temp_breached || currentFlags.impact_breached) {
    currentState = STATE_COMPROMISED;
  } 
  else if (currentTelemetry.temperature_c > TEMP_SAFE_MAX || currentTelemetry.acceleration_g >= ACCEL_WARN_MAX) {
    if (currentState != STATE_COMPROMISED) {
      currentState = STATE_WARNING;
    }
  } 
  else {
    if (currentState != STATE_COMPROMISED) {
      currentState = STATE_SAFE;
    }
  }
}

void updateIndicators() {
  unsigned long currentTime = millis();

  switch (currentState) {
    case STATE_SAFE:
      digitalWrite(PIN_LED_GREEN, HIGH);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, LOW);
      digitalWrite(PIN_BUZZER, LOW);
      break;

    case STATE_WARNING:
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, HIGH);
      digitalWrite(PIN_LED_RED, LOW);
      digitalWrite(PIN_BUZZER, LOW);
      break;

    case STATE_COMPROMISED:
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, HIGH);

      // Pulse buzzer during alarm state without blocking the main CPU execution loop
      if (currentTime - lastBuzzerToggle >= ALERT_TONE_INTERVAL) {
        lastBuzzerToggle = currentTime;
        buzzerActive = !buzzerActive;
        digitalWrite(PIN_BUZZER, buzzerActive ? HIGH : LOW);
      }
      break;
  }
}

void serializeTelemetry() {
  // Generate and transmit structured JSON string over the serial line
  Serial.print(F("{\"device_id\":\""));
  Serial.print(DEVICE_ID);
  Serial.print(F("\",\"uptime_ms\":"));
  Serial.print(millis());
  Serial.print(F(",\"telemetry\":{\"temperature_c\":"));
  Serial.print(currentTelemetry.temperature_c, 2);
  Serial.print(F(",\"humidity_pct\":"));
  Serial.print(currentTelemetry.humidity_pct, 2);
  Serial.print(F(",\"acceleration_g\":"));
  Serial.print(currentTelemetry.acceleration_g, 2);
  Serial.print(F(",\"max_impact_g\":"));
  Serial.print(currentTelemetry.max_impact_g, 2);
  Serial.print(F("},\"status\":{\"state\":\""));

  switch (currentState) {
    case STATE_SAFE:
      Serial.print(F("SAFE"));
      break;
    case STATE_WARNING:
      Serial.print(F("WARNING"));
      break;
    case STATE_COMPROMISED:
      Serial.print(F("COMPROMISED"));
      break;
  }

  Serial.print(F("\",\"flags\":{\"temp_breached\":"));
  Serial.print(currentFlags.temp_breached ? F("true") : F("false"));
  Serial.print(F(",\"impact_breached\":"));
  Serial.print(currentFlags.impact_breached ? F("true") : F("false"));
  Serial.println(F("}}}"));
}
