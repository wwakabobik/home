/* ***************************************************************************
 * This sketch contains weather station logic                                *
 *                                                                           *
 * Sketch uses ESP8288 controller, and it contains limited amount of         *
 * RAM. Due to that - to achieve stability - at least 20% of RAM should be   *
 * free and debug serial output is commented-out in this sketch.             *
 *                                                                           *
 * Flight controller contains:                                               *
 *    - ESP8266 (CH340g with WiFI), AC-DC supply unit,                       *
 *      OLED 128x64 display (SH1106) via I2C, RTC DS1302.                    *
 *                                                                           *
 *                                                                           *
 * Logic:                                                                    *
 *    1) Init OLED                                                           *
 *    2) Init RTC                                                            *
 *    3) Init Wi-fi                                                          *
 *    3) Start looping:                                                      *
 *       a) Check WiFi status, reconnect if needed                           *
 *       b) Get data from sensor (string)                                    *
 *       c) Display current time                                             *
 *       d) Scroll data string on screen                                     *
 *       e) Wait cooldown, go to "a"                                         *
 *                                                                           *
 * Sketch written by Iliya Vereshchagin 2021.                                *
 *****************************************************************************/


#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <virtuabotixRTC.h>

#define DEBUG


// RTC
virtuabotixRTC myRTC(14, 12, 13);


// OLED
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0);
u8g2_uint_t offset;            // current offset for the scrolling text
u8g2_uint_t width;             // pixel width of the scrolling text (must be lesser than 128 unless U8G2_16BIT is defined
const int string_length = 80;  // maximum count of symbols in marquee
char text[string_length];      // text buffer to scroll

// Wi-Fi
const char* wifi_ssid = "YOUR_SSID";
const char* wifi_password = "YOUR_PASSWORD";

// API
const String ip_address = "YOUR_IP_OF_SERVER";
const String port = "YOUR_PORT";
const String api_endpoint = "/api/v1/add_weather_data";
const String api_url = "http://" + ip_address + ":" + port + api_endpoint;
const int max_retries = 5;  // number of retries to send packet

// Timers and delays
const long data_retrieve_delay = 300000;
const int cycle_delay = 5;
unsigned long last_measurement = 0;

// Reboot timeout
const unsigned long reboot_timeout = 8 * 3600000;  // once per 8 hours


void setup(void) 
{
    Serial.begin(9600);
    init_OLED();
    init_RTC();
    init_WiFi();
}


/* Init functions */
void init_OLED()
{
    u8g2.begin();  
    u8g2.setFont(u8g2_font_inb30_mr); // set the target font to calculate the pixel width
    u8g2.setFontMode(0);    // enable transparent mode, which is faster
}


void init_RTC()
{
    // seconds, minutes, hours, day of the week, day of the month, month, year
    //myRTC.setDS1302Time(30, 03, 22, 5, 19, 2, 2021);
    myRTC.updateTime(); // update of variables for time or accessing the individual elements.
}


void init_WiFi()
{
    connect_to_WiFi();
    #ifdef DEBUG
    Serial.println("Init WiFi OK");
    #endif
}


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


String get_data()
{
    check_connection();

    #ifdef DEBUG
    Serial.println("Obtaining data from server");
    #endif
    HTTPClient http;    //Declare object of class HTTPClient
  
    int http_code = 404;
    int retries = 0;
    String payload = "Data retrieve error";
    while (http_code != 200)
    {
        http.begin(api_url);               // connect to request destination
        http_code = http.GET();            // send the request
        String answer = http.getString();  // get response payload
        http.end();                        // close connection
        
        #ifdef DEBUG
        Serial.println(http_code);         // print HTTP return code
        #endif

        retries++;
        if (retries > max_retries)
        {
            break;
            #ifdef DEBUG
            Serial.println("Couldn't get the data!");
            #endif
        }
                
        if (http_code == 200)
        {
            payload = answer;
        }
    }
    return payload;
}


void loop(void) 
{
    // Check that new data is needed to be retrieved from server
    if (((millis() - last_measurement) > data_retrieve_delay) or last_measurement == 0)
    {
        String stext = get_data();
        stext.toCharArray(text, string_length);
        last_measurement = millis();
        width = u8g2.getUTF8Width(text);    // calculate the pixel width of the text
        offset = 0;
        #ifdef DEBUG
        Serial.print("stext: ");
        Serial.println(stext);
        Serial.print("text: ");
        Serial.println(text);
        Serial.print("last_measurement: ");
        Serial.println(last_measurement);
        Serial.print("RTC Time: ");                                                                                                                                                    
        Serial.print(myRTC.hours);                                                                              
        Serial.print(":");                                                                                      
        Serial.println(myRTC.minutes); 
        #endif
    }

    // Update RTC
    myRTC.updateTime(); 

    // Now update OLED
    u8g2_uint_t x;
    u8g2.firstPage();
    do 
    {
        // draw the scrolling text at current offset
        x = offset;
        u8g2.setFont(u8g2_font_inb16_mr);       // set the target font
        do 
        {                                       // repeated drawing of the scrolling text...
            u8g2.drawUTF8(x, 58, text);         // draw the scrolling text
            x += width;                         // add the pixel width of the scrolling text
        } while (x < u8g2.getDisplayWidth());   // draw again until the complete display is filled
    
        u8g2.setFont(u8g2_font_inb30_mr);       // choose big font for clock
        u8g2.setCursor(0, 30);                  // set position of clock
        char buf[8];                            // init buffer to formatted string
        sprintf_P(buf, PSTR("%02d:%02d"), myRTC.hours, myRTC.minutes); // format clock with leading zeros
        u8g2.print(buf);                        // display clock
    } while (u8g2.nextPage());
  
    offset-=2;                                  // scroll by two pixels
    if ((u8g2_uint_t)offset < ((u8g2_uint_t) - width))
    {  
        offset = 0;                  // start over again
    }  
    delay(cycle_delay);              // do some small delay
    if millis() > reboot_timeout
    {
        ESP.restart();
    }
}
