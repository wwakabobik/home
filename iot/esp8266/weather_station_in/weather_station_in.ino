/* ***************************************************************************
 * This sketch contains weather station logic                                *
 *                                                                           *
 * Sketch uses ESP8288 controller, and it contains limited amount of         *
 * RAM. Due to that - to achieve stability - at least 20% of RAM should be   *
 * free and debug serial output is commented-out in this sketch.             *
 *                                                                           *
 * Flight controller contains:                                               *
 *    - ESP8266 (CH340g with WiFI), AC-DC supply unit,                       *
 *      BME280 barometer/thermometer/hydrometer.                             *
 *                                                                           *
 * Note: this sketch is designed for indoor use                              *
 *                                                                           *
 * Logic:                                                                    *
 *    1) Init BME280 sensor                                                  *
 *    2) Wait for WiFi connection established                                *
 *    3) Start looping:                                                      *
 *       a) Check WiFi status, reconnect if needed                           *
 *       b) Get data from sensor                                             *
 *       c) Connect to server via REST JSON API                              *
 *       d) Send packet                                                      *
 *       e) Wait cooldown, go to "a"                                         *
 *                                                                           *
 * Sketch written by Iliya Vereshchagin 2021.                                *
 *****************************************************************************/

#define DEBUG

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BME280.h>
#include <Arduino_JSON.h>


// Sensor globals
Adafruit_BME280 bme; // use I2C interface
Adafruit_Sensor *bme_temp = bme.getTemperatureSensor();
Adafruit_Sensor *bme_pressure = bme.getPressureSensor();
Adafruit_Sensor *bme_humidity = bme.getHumiditySensor();
float correction_temperature = -1.5;  // calibration addition for temperature
float correction_pressure = 14;       // calibration addition for pressure
float correction_humidity = 0;        // calibration addition for humidity


// Format consts
String delimiter = ",";


// Device ID
const String DEVICE_ID = "0";  // 0 is internal, 1 is external sensor

// Wifi
const char* wifi_ssid = "YOUR_SSID";
const char* wifi_password = "YOUR_PASSWORD";

// API
const String ip_address = "YOUR_IP_OF_SERVER";
const String port = "YOUR_PORT";
const String api_endpoint = "/api/v1/add_weather_data";
const String api_url = "http://" + ip_address + ":" + port + api_endpoint;
const int max_retries = 5;  // number of retries to send packet

// Packet send cooldown
const long cooldown = 300000;


void setup()
{
     Serial.begin(115200);
     Serial.println("Started init");
     init_BME();
     init_WiFi();
}

void loop()
{
    #ifdef DEBUG
    get_serial_data();
    #endif
    post_data();
    delay(cooldown);
}

/* Init functions */
void init_WiFi()
{
    connect_to_WiFi();
    #ifdef DEBUG
    Serial.println("Init WiFi OK");
    #endif
}

void init_BME()
{
    if (!bme.begin())
    {
        Serial.println(F("Could not find a valid BME280 sensor, check wiring!"));
        while (1) delay(10);
    }

    #ifdef DEBUG
    Serial.println("Init BME280 OK");
    bme_temp->printSensorDetails();
    bme_pressure->printSensorDetails();
    bme_humidity->printSensorDetails();
    #endif
}


#ifdef ODISPLAY
void init_oled()
{
    myOLED.begin();
    myOLED.setFont(SmallFont);
    Serial.println("OLED initialized");
}
#endif


/* WiFi functions */

void connect_to_WiFi()
{
   #ifdef DEBUG
   Serial.println("Connecting to " + String(wifi_ssid));
   #endif
   WiFi.mode(WIFI_STA);
   WiFi.begin(wifi_ssid, wifi_password);
   while (WiFi.status() != WL_CONNECTED)
   {
      delay(500);
   }
   #ifdef DEBUG
   Serial.println("WiFi connected");
   Serial.print("IP address: ");
   Serial.println(WiFi.localIP());
   #endif
}

void check_connection()
{
    if (WiFi.status() != WL_CONNECTED)
    {
        #ifdef DEBUG
        Serial.println("Network disconnected");
        #endif
        connect_to_WiFi();
    }
    else
    {
        #ifdef DEBUG
        Serial.println("Network stable");
        #endif
    }
}


void post_data()
{
    check_connection();

    #ifdef DEBUG
    Serial.println("Sending POST data to server");
    #endif
    HTTPClient http;    //Declare object of class HTTPClient

    String content = get_csv_data();
    int http_code = 404;
    int retries = 0;
    while (http_code != 201)
    {
        http.begin(api_url); // connect to request destination
        http.addHeader("Content-Type", "application/json");        // set content-type header
        http_code = http.POST("{\"data\": \"" + content +"\"}");   // send the request
        #ifdef DEBUG
        String payload = http.getString();                         // get response payload
        #endif DEBUG
        http.end();                                                // close connection

        #ifdef DEBUG
        Serial.println(http_code);  //Print HTTP return code
        Serial.println(payload);    //Print request response payload
        #endif

        retries++;
        if (retries > max_retries)
        {
            break;
            #ifdef DEBUG
            Serial.println("Package lost!");
            #endif
        }
    }
}

/* BME functions */

float get_temperature()
{
    sensors_event_t temp_event, pressure_event, humidity_event;
    bme_temp->getEvent(&temp_event);
    return temp_event.temperature + correction_temperature;
}

float get_pressure()
{
    sensors_event_t pressure_event;
    bme_pressure->getEvent(&pressure_event);
    return (pressure_event.pressure/1.3333 + correction_pressure);
}

float get_humidity()
{
    sensors_event_t humidity_event;
    bme_humidity->getEvent(&humidity_event);
    return humidity_event.relative_humidity + correction_humidity;
}

float get_dew_point()
{
    float dp;
    float t = get_temperature();
    float h = get_humidity();
    dp = (t-(14.55+0.114*t)*(1-(0.01*h))-pow(((2.5+0.007*t)*(1-(0.01*h))),3)-(15.9+0.117*t)*pow((1-(0.01*h)), 14));

    return dp;
}

/* Format functions */

String get_csv_data()
{
    String ret_string = DEVICE_ID;
    ret_string += delimiter + String(get_temperature());
    ret_string += delimiter + String(get_humidity());
    ret_string += delimiter + String(get_pressure());
    ret_string += delimiter + String(get_dew_point());
    ret_string += ',0.0,0.0';  // fill with zeros UV and rain sensor values
    return ret_string;
}

#ifdef DEBUG
void get_serial_data()
{
    String ret_string = "Temperature: " + String(get_temperature()) + " *C\nHumidity: " + String(get_humidity());
    ret_string += " %\nPressure: " + String(get_pressure()) + " mmhg\nDew point: " + get_dew_point() + " *C\n";
    Serial.println(ret_string);
}
#endif
