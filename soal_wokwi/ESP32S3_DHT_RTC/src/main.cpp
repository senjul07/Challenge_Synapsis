#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <RTClib.h>

// === KONFIGURASI WIFI & MQTT ===
const char *ssid = "Wokwi-GUEST";
const char *password = "";
const char *mqtt_server = "test.mosquitto.org";
const int mqtt_port = 1883;
const char *nama = "sendy";
String topic_data = "mqtt/" + String(nama) + "/data";

// === KONFIGURASI PIN LED ===
#define LED_WIFI 2
#define LED_MQTT 4

// === KONFIGURASI PIN DHT22 ===
#define DHTPIN 10
#define DHTTYPE DHT22
DHT sensor_dht(DHTPIN, DHTTYPE);

// === KONFIGURASI RTC DS1307 ===
RTC_DS1307 rtc;

// === OBJEK WIFI & MQTT ===
WiFiClient esp_client;
PubSubClient client(esp_client);

// === TASK HANDLES ===
TaskHandle_t TaskSensorHandle = NULL;


// === FUNGSI setup WIFI ===
void setupWifi()
{
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password); // inisialisasi koneksi wifi
  while (WiFi.status() != WL_CONNECTED)
  {
    vTaskDelay(500 / portTICK_PERIOD_MS);
  }
  Serial.print("WiFi connected - IP: ");
  Serial.println(WiFi.localIP());
  Serial.println("");
  digitalWrite(LED_WIFI, HIGH);
}


// === FUNGSI CHECK KONEKSI WIFI ===
void checkWiFi()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    digitalWrite(LED_WIFI, LOW);
    while (WiFi.status() != WL_CONNECTED)
    {
      WiFi.reconnect();
      vTaskDelay(500 / portTICK_PERIOD_MS);
    }
    digitalWrite(LED_WIFI, HIGH);
  }
}


// === TASK SENSOR ===
void taskSensor(void *pvParameters)
{
    const TickType_t xDelay = 5000 / portTICK_PERIOD_MS; // 5 detik
    const TickType_t xKedip = 200 / portTICK_PERIOD_MS; // 200 ms

    for (;;)
    {
      // cek koneksi WiFi
      if (WiFi.status() == WL_CONNECTED)
      {
        // baca sensor
        float data_hum = sensor_dht.readHumidity();
        float data_temp = sensor_dht.readTemperature();

        if (isnan(data_hum) || isnan(data_temp))
        {
            Serial.println("Failed to read from sensor_dht sensor!");
        }
        else
        {
            // ambil waktu dari RTC
            DateTime now_gmt7 = rtc.now(); // get waktu dari RTC (karena simulator wokwi pake waktu lokal browser jadinya default GMT+7)
            DateTime now_utc = now_gmt7 - TimeSpan(0, 7, 0, 0); // konversi ke UTC

            // format UTC
            char timestamp_utc[20];
            sprintf(timestamp_utc, "%04d-%02d-%02d %02d:%02d:%02d",
                    now_utc.year(), now_utc.month(), now_utc.day(),
                    now_utc.hour(), now_utc.minute(), now_utc.second());

            // format GMT+7
            char timestamp_gmt7[20];
            sprintf(timestamp_gmt7, "%04d-%02d-%02d %02d:%02d:%02d",
                    now_gmt7.year(), now_gmt7.month(), now_gmt7.day(),
                    now_gmt7.hour(), now_gmt7.minute(), now_gmt7.second());

            // buat data JSON
            String payload = "{";
            payload += "\"nama\":\"" + String(nama) + "\",";
            payload += "\"data\":{";
            payload += "\"temperature\":" + String(data_temp, 1) + ",";
            payload += "\"humidity\":" + String(data_hum, 1);
            payload += "},";
            payload += "\"timestamp\":\"" + String(timestamp_utc) + "\"";
            payload += "}";

            // koneksi ke MQTT
            client.connect("ESP32Client");

            // publish ke MQTT
            boolean result = client.publish(topic_data.c_str(), payload.c_str());

            // handle client MQTT
            client.loop();

            Serial.print("Datetime : ");
            Serial.println(timestamp_gmt7);
            Serial.print("Temperature : ");
            Serial.println(data_temp);
            Serial.print("Humidity : ");
            Serial.println(data_hum);
            Serial.print("Data Pack : ");
            Serial.println(payload);
            Serial.print("Result Publish : ");
            Serial.println(result ? "Success" : "Failed");
            Serial.println("=================================");

            if(result)
            {
              digitalWrite(LED_MQTT, HIGH);
              vTaskDelay(xKedip);
              digitalWrite(LED_MQTT, LOW);
            }
            else
            {
              digitalWrite(LED_MQTT, LOW);
              vTaskDelay(xKedip);
            }
          }
        }
        else
        {
          Serial.println("WiFi not connected!");
          checkWiFi();
        }

        vTaskDelay(xDelay - xKedip);
    }
}


// === SETUP ===
void setup()
{
  Serial.begin(115200); // inisialisasi serial monitor
  sensor_dht.begin();   // inisialisasi sensor DHT22

  // Inisialisasi LED
  pinMode(LED_WIFI, OUTPUT);
  pinMode(LED_MQTT, OUTPUT);
  digitalWrite(LED_WIFI, LOW);
  digitalWrite(LED_MQTT, LOW);

  if (!rtc.begin()) // inisialisasi RTC
  {
    while (1);
  }

  if (!rtc.isrunning()) // inisialisasi RTC
  {
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__))); // set waktu sesuai waktu kompilasi
  }

  setupWifi();                              // setup wifi
  client.setServer(mqtt_server, mqtt_port); // set server MQTT

  // Task Sensor
  xTaskCreate(
      taskSensor,         // fungsi task
      "taskSensor",       // nama task
      4096,               // stack size
      NULL,               // parameter
      1,                  // priority
      &TaskSensorHandle); // handle task
}


// === LOOP ===
void loop()
{
  // loop
}