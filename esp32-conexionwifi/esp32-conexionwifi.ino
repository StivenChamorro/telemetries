#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_INA219.h>

// --- CONFIGURACIÓN DE RED WI-FI ---
//const char* ssid = "Redmi Note 14";
//const char* password = "tatis123";

const char* ssid = "Lida Caicedo";
const char* password = "1415LCC-A11";

// --- CONFIGURACIÓN DEL SERVIDOR (Laravel / XAMPP) ---
// Asegúrate de que esta IP sea la misma que probaste en tu celular y navegador
const char* serverName = "http://192.168.101.78:8000/api/telemetry";
//const char* serverName = "http://10.93.154.31:8000/api/telemetry";

// --- INSTANCIA DEL SENSOR INA219 ---
Adafruit_INA219 ina219;

// --- PINES PARA ACS712 Y FZ0430 (Panel Solar) ---
const int pinVoltajeFZ = 35;   // Pin analógico para el divisor de voltaje (FZ0430)
const int pinCorrienteACS = 34; // Pin analógico para el ACS712

// Variables de calibración y conversión
const float factorCalibracionVoltaje = 5.0; // Ajusta según tu divisor de voltaje real
const float sensibilidadACS = 0.185;        // 185 mV/A para el modelo ACS712 de 5A
const float voltajeRef = 3.3;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Inicializar I2C para el INA219 (Pines SDA=21, SCL=22 en ESP32)
  Wire.begin(21, 22);
  
  if (!ina219.begin()) {
    Serial.println("¡Alerta! No se encontró el sensor INA219. Revisa las conexiones I2C.");
  } else {
    Serial.println("Sensor INA219 inicializado correctamente.");
  }

  // Conexión Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a la red Wi-Fi. IP asignada:");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    
    // ==========================================================
    // 1. LECTURA DE SENSORES CON PROMEDIO (Filtro anti-ruido de 10 muestras)
    // ==========================================================
    long sumVoltajeFZ = 0;
    long sumCorrienteACS = 0;
    int muestras = 10;

    for (int i = 0; i < muestras; i++) {
      sumVoltajeFZ += analogRead(pinVoltajeFZ);
      sumCorrienteACS += analogRead(pinCorrienteACS);
      delay(2);
    }
    
    int rawVoltaje = sumVoltajeFZ / muestras;
    int rawCorriente = sumCorrienteACS / muestras;

    // Cálculo Voltaje Solar (Divisor FZ0430)
    float solarVoltage = (rawVoltaje * voltajeRef / 4095.0) * factorCalibracionVoltaje;

    // Cálculo Corriente Solar (ACS712)
    float voltajeSensorACS = (rawCorriente * voltajeRef) / 4095.0;
    
    // IMPORTANTE: El offset teórico es 1.65V (mitad de 3.3V), pero puedes calibrarlo aquí si en reposo marca distinto
    float offsetACS = 1.65; 
    float solarCurrent = abs((voltajeSensorACS - offsetACS) / sensibilidadACS); 
    
    // Si la corriente calculada es muy baja (ruido), la fijamos en 0
    if (solarCurrent < 0.05 && solarCurrent > -0.05) {
      solarCurrent = 0.0;
    }

    // ==========================================================
    // 2. LECTURA DEL SENSOR DE CONSUMO (11 LEDs mediante INA219)
    // ==========================================================
    float loadVoltage = ina219.getBusVoltage_V();
    float loadCurrentmA = ina219.getCurrent_mA();
    float loadCurrent = loadCurrentmA / 1000.0; // Convertir mA a Amperios

    // ==========================================================
    // 3. CONSTRUCCIÓN DEL JSON CRUDO
    // ==========================================================
    String jsonPayload = "{";
    jsonPayload += "\"solar_voltage\":" + String(solarVoltage, 4) + ",";
    jsonPayload += "\"solar_current\":" + String(solarCurrent, 4) + ",";
    jsonPayload += "\"load_voltage\":" + String(loadVoltage, 4) + ",";
    jsonPayload += "\"load_current\":" + String(loadCurrent, 4);
    jsonPayload += "}";

    // ==========================================================
    // 4. ENVÍO HTTP POST A LA API DE LARAVEL
    // ==========================================================
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Accept", "application/json");
    http.useHTTP10(true);
    http.setTimeout(10000); // 10 segundos de timeout para evitar error -1 por red lenta

    int httpResponseCode = http.POST(jsonPayload);
    String responseBody = http.getString();

    Serial.println("--------------------------------------------------");
    Serial.print("JSON Enviado: ");
    Serial.println(jsonPayload);
    Serial.print("Código HTTP Respuesta: ");
    Serial.println(httpResponseCode);
    Serial.print("Respuesta de Laravel: ");
    Serial.println(responseBody);
    Serial.println("--------------------------------------------------");

    http.end();
  } else {
    Serial.println("WiFi desconectado. Intentando reconectar...");
    WiFi.reconnect();
  }

  delay(5000); // Intervalo de 5 segundos
}