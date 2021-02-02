/* ***************************************************************************
 * This sketch contains wind speed/direction sensor logic        .           *
 *                                                                           *
 * Sketch uses Arduino Nano controller, and it contains limited amount of    *
 * RAM. Due to that - to achieve stability - at least 20% of RAM should be   *
 * free and debug serial output is commented-out in this sketch.             *
 *                                                                           *
 * Flight controller contains:                                               *
 *    - Arduino Nano v3 (CH340g), GY-271 compass and LM-393 luminosity       *
 *    sensor with paired LED;                                                *
 *    - As output: SD card, LCD1602 or serial output can be used;            *
 *    - Alternatively, send data via wireless LoRA module (SX1278 (Ra-02));  *
 *    - As error indicator buzzer output can be used;                        *
 *    - As option, RTC may be attached.                                      *
 *                                                                           *
 * Third-party libraries:                                                    *
 *    - http://wiki.sunfounder.cc/images/6/6d/QMC5883L.zip                   *
 *    - http://amperkot.ru/static/3236/uploads/libraries/HMC5883L.zip        *
 *                                                                           *
 * Note:                                                                     *
 *    - To set desired outputs comment/uncomment related define.             *
 *                                                                           *
 * Logic:                                                                    *
 *    1) Init all modules;                                                   *
 *    2) Start anemometr measurement loop (several measurements per period); *
 *    3) Measure instant wind speed for a short period;                      *
 *    4) Calculate average wind speed for whole loop period, max and min;    *
 *    5) Get wind direction data from compass;                               *
 *    6) Convert measurements to human-readable format;                      *  
 *    7) Display/send all data via desired output;                           *
 *    8) Go to point 2.                                                      * 
 *                                                                           *
 * Sketch written by Iliya Vereshchagin 2020.                                *
 *****************************************************************************/

// Desired outputs, comment/uncomment what is needed
#define DEBUG
//#define LCD_OUT
//#define SD_OUT
#define WIRELESS_OUT
#define BUZZER_OUT
//#define RTC_CLOCK

// Required includes
#include <Wire.h>
#include <QMC5883L.h>  // for QMC chip
//#include <HMC5883L.h>  // for HMC chip

// Configurable imports
#ifdef SD_OUT
#include <SdFat.h>  // use alternative include, get rid of usage of SD.h because works unstable for SDHC FAT32 flash memory cards
#endif
#ifdef LCD_OUT
#include <LiquidCrystal.h>
#endif
#ifdef WIRELESS_OUT
#include <LoRa.h>
#endif
#ifdef RTC_CLOCK
#include <RTClib.h>
#endif

/* Globals section */

// Reset delay
long reset_delay = 300000;   // delay after error, to prevent endless count of reboots in case of fatal error

// Serial const
#ifdef DEBUG
const int BAUD_RATE = 9600;  // default serial output baud rate
#endif

// Photo pin const
const int IN_PIN = 8;       // input pin for luminocity sensor (photo pair)
const int HOLES_COUNT = 8;  // count of holes in rotatin disk (use less for strong winds, or more for weak)

// Wind speed data
struct wind_data {      // we'll use this structure to pass all wind data to loggers
    float average_rps;  // average measured rotations of disk per second
    float max_rps;      // maximum measured rotations of disk per second
    float min_rps;      // minimum measured rotations of disk per second
};
const unsigned long CYCLE_MILLIS = 5000;                        // one meas period time
const int MEAS_PERIODS = 12;                                    // count of measurements for long period
const unsigned long LONG_PERIOD = CYCLE_MILLIS * MEAS_PERIODS;  // whole period for average calculation
const float COEFF = 2.05;                                       // rpm to m/s coeff is calibrated value, or use 3.0 as calculated Robinson's constant

// Compass
QMC5883L compass;                     // for QMC chip
//HMC5883L compass;                     // for HMC chip
float declination_angle = -0.191986;  // (in rads) +11° 35' For Moscow, Russia. Find yours here: http://www.magnetic-declination.com/

#ifdef SD_OUT
// SD CARD globals
SdFat SD;                                // set same name as in SD.h to backward compatibility
File my_file;                            // file descriptor variable
const String filename = "WIND_DATA.TXT"; // default filename
const int SD_CS_PIN = 5;                 // force to use digital 5 pin instead of default, for sheilds use 10
#endif

// LCD
#ifdef LCD_OUT
// LCD globals
const int rs = 9, en = 8, d4 = 5, d5 = 4, d6 = 3, d7 = 2;  // set LCD pins, please not that pin 3 will conflict with buzzer, make sure to reslove it using both of them
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);                 // lcd variable
struct lcd_out{                                            // we'll use struct to output for each string of LCD diplay. Each string contains 16 characters.
    String first;
    String second;
};  
#endif

// LoRA
#ifdef WIRELESS_OUT
const int LORA_POWER = 20;    // set TX power to maximum 
const int LORA_RETRIES = 12;  // try to init LoRa several times before error
const int LORA_DELAY = 500;   // delay between retries
const int LORA_SEND_DELAY = 20;  // delay between send data
const int LORA_SEND_RETRIES = 5; // how much ackets will be sent
#endif

// Buzzer
#ifdef BUZZER_OUT
const int PIN_BUZZER = 3;            // digital pin of buzzer
const int GHZ = 2500;                // set default GHZ tone
const int BUZZER_DELAY = 250;        // delay between tone i/o, delay between beeps is BUZZER_DELAY * 2
const int BUZZER_REPEATS = 3;        // count of repeats of error notification
const int BUZZER_LONG_DELAY = 2000;  // delay between each error notification 
#endif

// RTC global
#ifdef RTC_CLOCK
RTC_DS1307 RTC;
DateTime cur_time;
#endif

// Device id
const String DEVICE_ID = "0";


/* Main functions */

void(* reset_func) (void) = 0;  // force reboot controller to re-init each and every pin and variable

void setup()  // setup all input and output devices
{
    #ifdef DEBUG
    init_serial();
    #endif
    init_pin();
    #ifdef RTC_CLOCK
    init_RTC();
    #endif
    //init_compass();
    #ifdef SD_OUT
    init_SD_card();
    #endif
    #ifdef LCD_OUT
    init_LCD();
    #endif
    #ifdef WIRELESS_OUT
    init_LoRa();
    #endif
}

void loop()  // colelct & send data to all desired outputs
{
    #ifdef DEBUG
    Serial.println(get_all_data_as_string());
    #endif
    #ifdef SD_OUT
    write_to_file(get_all_data_as_csv());
    #endif
    #ifdef LCD_OUT
    display_on_LCD(get_LCD_string());
    #endif
    #ifdef WIRELESS_OUT
    LoRa_send(get_all_data_as_csv());
    #endif
    #ifdef BUZZER_OUT
    beep();
    #endif
}

void stop(int error)  // if error happened, call this function - notify (if applicable) and reset controller after delay
{
    #ifdef BUZZER_OUT
    for (int i=0; i < BUZZER_REPEATS; i++)
    {
        buzzer_error(error);
        delay(BUZZER_LONG_DELAY);
    }
    #endif  
    delay(reset_delay);
    reset_func();
}


/* Init functions */

#ifdef DEBUG
void init_serial()  // init serial output
{
    Serial.begin(BAUD_RATE);
    #ifdef DEBUG
    Serial.println("Serial output activated");
    #endif
}
#endif


void init_pin()  // init luminocity sensor
{
    pinMode(IN_PIN, INPUT);
    #ifdef DEBUG
    Serial.println("Photo pin set.");
    #endif
}


void init_compass()  // init compass
{
    Wire.begin();
    compass.init();
    #ifdef DEBUG
    Serial.println("Compass initialized");
    #endif
}


#ifdef SD_OUT
bool init_SD_card()  // init SD card
{
    #ifdef DEBUG
    Serial.println("Initializing SD card...");
    #endif
    pinMode(SD_CS_PIN, OUTPUT);     // some SD modules need to be forced init by 
    digitalWrite(SD_CS_PIN, HIGH);  // sending high voltage to CS/SS pin
    if (!SD.begin(SD_CS_PIN))
    {
        #ifdef DEBUG
        Serial.println("Init SD failed!");
        #endif
        stop(2);
    }
    #ifdef DEBUG
    Serial.println("SD init OK");
    #endif
}
#endif


#ifdef LCD_OUT
void init_LCD()  // init 1602 LCD
{
    lcd.begin(16, 2);
    lcd.setCursor(0, 0);
    lcd.clear();
    lcd.print("                 ");
    lcd.setCursor(0, 1);
    lcd.print("                 ");
}
#endif


#ifdef WIRELESS_OUT
void init_LoRa()  // try to init LoRA at 433Mhz for several retries
{
    bool success = false;
    for (int i=0; i < LORA_RETRIES; i++)
    
    {
        if (LoRa.begin(433E6))
        {
            success = true;
            break;
        }
        delay(LORA_DELAY);
    }
    if (!success)
    {
        #ifdef DEBUG
        Serial.println("LoRa init failed.");
        #endif
        stop(4);
    }
    
    LoRa.setTxPower(LORA_POWER);  // aplify TX power
    #ifdef DEBUG
    Serial.println("LoRa started!");
    #endif  
}
#endif

#ifdef RTC_CLOCK
void init_RTC()
{
    RTC.begin();
    if (! RTC.isrunning()) 
    {
        #ifdef DEBUG
        Serial.println("RTC is NOT running!");
        #endif
        // following line sets the RTC to the date & time this sketch was compiled
        // uncomment it & upload to set the time, date and start run the RTC!
        RTC.adjust(DateTime(__DATE__, __TIME__));
    }
    #ifdef DEBUG
    Serial.println("RTC OK, now is " + get_time_stamp());
    #endif    
}
#endif

/* RTC functions */
#ifdef RTC_CLOCK
String get_time_stamp()
{
    
    cur_time = RTC.now();
    return String(cur_time.year(), DEC) + "/" + String(cur_time.month(), DEC) + "/" + String(cur_time.day(), DEC) + " " + String(cur_time.hour(), DEC) + ":" + String(cur_time.minute(), DEC);
}
#endif


/* Compass functions */

float get_heading()  // get current wind heading in degrees
{
    int x,y,z;
    float heading;

    compass.read(&x,&y,&z);
    heading = atan2(y, x);    // calculate heading
    heading += declination_angle;

  // correct signs
    if(heading < 0)
    {
        heading += 2*PI;
    }
    if(heading > 2*PI)
    {
        heading -= 2*PI;
    }
    return heading * RAD_TO_DEG;
}


/* Anemometr functions */

float get_avg_rps(unsigned long measurement_time)  // count average rps per period
{
    /* Note 1. We can't check direction of the wind, this means if wind direction will be changed to opposite,   /
    /  we may encounter of some measurement error. It will affect measurement until rotator stops because of     /
    /  inertion and accelerate again to opposite direction. Also aware of wrong meausements while strong wind    /
    /  and frequently changed direction of it.                                                                   /
    /  Note 2: Rotor has same inertion due to friction force. We can't fight it at all. Rotor will not start     /
    /  or stop instantly. If friction force is strong, then heavier rotor will start. Otherwise, if              /
    /  friction force will be too small, then rotor will longer rotate after wind blowing stops.                 /
    /  All of it will lead to measurements error.                                                                /
    /  If you need more precise measurement of weak wind (<0.5 m/s) or peak values, ensure that friction force   /
    /  is low. Also reduce measurement period (measurement_time = CYCLE_MILLIS) to minimum reasonable (down to   /
    /  1000/HOLES_COUNT). In other hand, if you need more preciese measurement of average wind data for average  /
    /  winds (2-10 m/s), then ensure that friction force is average - rotor should start rotating at human blow  /
    /  (~0.4-0.6 m/s). Also, result meaurement will be accurate for averages for measurement time equal to       /
    /  average wind speed in your location * 1000. (for 5 m/s it will be 5000 millis).                           /
    /  Note 3. Try not to use anemometr while strong wind. It may lead to destruction of it. Or in such case,    /
    /  use heavy construction, materials, small bawls and bigger friction force of rotor. Rotation speed (at     /
    /  least hole change ratio) should be always less than cycle of contoller measurement. It's better to        /
    /  ensure that holes will not change more often than 10ms, what is equal to 100/HOLES_COUNT = rps.           /
    /  For strong winds measurement it's better reduce count of holes also.                                      /
    /  In my case (set as default in sketch) upper limit of maximum possible wind is 25 m/s.                    */

    unsigned long start_time = millis();
    int counter = 0;
    bool last_state = digitalRead(IN_PIN) == HIGH;
    bool actual_state = digitalRead(IN_PIN);

    while (((unsigned long)(millis() - start_time)) < measurement_time)
    {
        if (millis() < start_time)  // if underflow occured, we need to force reset controller
        {
            stop(5);
        }
        actual_state = digitalRead(IN_PIN) == HIGH;
        if (last_state != actual_state)
        {
            if (actual_state == true)  // we'll count only HIGH state of sensor, this may lead to error of 1/16 rps per for whole measurement
            {
                counter++;  
            }
            last_state = actual_state;
        }
    }
    return (((float)counter*(float)1000.0)/(float)HOLES_COUNT)/(float)measurement_time;  // we assume that 1 rps is HOLES_COUNT detections
}

wind_data get_rps_data_per_period(unsigned long whole_period, int measurements)  // get average, minimum and maximum wind speed per long period
{
    wind_data return_value = {0, 0, 255.0};
    float current_rps = 0;

    for (int i = 0; i < measurements; i++)
    {
        current_rps = get_avg_rps(whole_period/measurements);
        return_value.average_rps += current_rps;  // just add current measured rps to sum of averages
        if (current_rps > return_value.max_rps)
        {
            return_value.max_rps = current_rps;  // update maximum value if current value is greater
        }
        if (current_rps < return_value.min_rps)
        {
            return_value.min_rps = current_rps;  // update minimumvalue if current value is less
        }
    }

    return_value.average_rps /= measurements;  // denominate sum of average values with count of measurements
    return return_value;
}


#ifdef LCD_OUT
/* LCD output functions */
void display_on_LCD(lcd_out message)  // display message on LCD
{
    lcd.setCursor(0, 0); // set input to first string, first position
    lcd.clear();  // erase old text
    lcd.print(message.first);  // set first string of message 
    lcd.setCursor(0, 1); // set input to second string, first position
    lcd.print(message.second);  // set second string of message 
}
#endif


#ifdef WIRELESS_OUT
/* LoRa out functions */
void LoRa_send(String data)  // send pre-formatted data via LoRA
{
    #ifdef DEBUG
    Serial.println("Sending via LoRa packet with payload: " + data);
    #endif
    for (int i=0; i < LORA_SEND_RETRIES; i++)
    {
        LoRa.beginPacket();  // just open packet
        LoRa.print(data);    // send whole data
        LoRa.endPacket();    // end packet
        delay(LORA_SEND_DELAY);
    }  
}
#endif


#ifdef SD_OUT
/* SD out functions */
void write_to_file(String data) // write pre-formatted data to file on SD card
{
    #ifdef DEBUG
    //pinMode(SD_CS_PIN, OUTPUT);     // some SD modules need to be forced init by 
    //digitalWrite(SD_CS_PIN, HIGH);  // sending high voltage to CS/SS pin
    Serial.println("Opening IO file...");
    #endif
    my_file = SD.open(filename, FILE_WRITE);  // open output file, if none of it exists, new file will be created
    if (my_file)
    {
        #ifdef DEBUG
        Serial.println("SD OK");
        #endif
    }
    else
    {
        #ifdef DEBUG
        Serial.println("Can't open file!");
        #endif
        stop(3);
    }
    my_file.println(data);  // print data to file
    my_file.close();  // close file
}
#endif


/* Convert functions */

float rps_to_ms(float rps)  // convert rps to ms using conversion COEFF
{
    return rps * COEFF;
}

float ms_to_kmh(float ms)  // convert ms to kmh
{
    return (ms * 3.6);
}

float ms_to_knots(float ms)  // convert ms to knots
{
    return (ms * 1.94384);
}

String heading_to_abbr(float heading)  // convert degrees to human-readable heading abbrevation
{
    String return_value;

    if (heading >= 337.5 or heading < 22.5)
    {
        return_value = "N";
    }
    else if (heading >= 22.5 and heading < 67.5)
    {
        return_value = "NE";
    }
    else if (heading >= 67.5 and heading < 112.5)
    {
        return_value = "E";
    }
    else if (heading >= 112.5 and heading < 157.5)
    {
      return_value = "SE";
    }
    else if(heading >= 157.5 and heading < 202.5)
    {
        return_value = "S";
    }
    else if (heading >= 202.5 and heading < 247.5)
    {
        return_value = "SW";
    }
    else if (heading >= 247.5 and heading < 292.5)
    {
        return_value = "W";
    }
    else
    {
        return_value = "NW";
    }

    return return_value;
}


/* String format functions */

String get_all_data_as_csv()  // get all data and format it as CSV 
{   
    wind_data wd;
    float heading;
    String return_string;
    String delimiter = ",";  // use as default delimiter
    
    wd = get_rps_data_per_period(CYCLE_MILLIS*MEAS_PERIODS, MEAS_PERIODS);
    heading = get_heading();
    
    return_string = DEVICE_ID + delimiter +String(millis()) + delimiter + String(wd.average_rps) + delimiter + String(wd.max_rps) + delimiter + String(wd.min_rps);
    return_string += delimiter + String(rps_to_ms(wd.average_rps)) + delimiter + String(rps_to_ms(wd.max_rps)) + delimiter + String(rps_to_ms(wd.min_rps));
    return_string += delimiter + String(ms_to_kmh(rps_to_ms(wd.average_rps))) + delimiter + String(ms_to_kmh(rps_to_ms(wd.max_rps))) + delimiter + String(ms_to_kmh(rps_to_ms(wd.min_rps)));
    return_string += delimiter + String(ms_to_knots(rps_to_ms(wd.average_rps))) + delimiter + String(ms_to_knots(rps_to_ms(wd.max_rps))) + delimiter + String(ms_to_knots(rps_to_ms(wd.min_rps)));
    return_string += delimiter + String(heading) + delimiter + heading_to_abbr(heading);
    #ifdef RTC_CLOCK
    return_string += get_time_stamp();
    #endif

    return return_string;
}

#ifdef DEBUG
String get_all_data_as_string()  // get all data and format in human-readable form
{   
    wind_data wd;
    float heading;
    String return_string;
    
    wd = get_rps_data_per_period(LONG_PERIOD, MEAS_PERIODS);
    heading = get_heading();
    
    return_string = "Millis: "+ String(millis()) + "\n";
    #ifdef RTC_CLOCK
    return_string += get_time_stamp() + "\n";
    #endif
    return_string += "\tAverage\tMaximum\tMinimum\n";
    return_string += "RPS\t" + String(wd.average_rps) + "\t" + String(wd.max_rps) + "\t" + String(wd.min_rps) + "\n";
    return_string += "m/s\t" + String(rps_to_ms(wd.average_rps)) + "\t" + String(rps_to_ms(wd.max_rps)) + "\t" + String(rps_to_ms(wd.min_rps)) + "\n";
    return_string += "km/h\t" + String(ms_to_kmh(rps_to_ms(wd.average_rps))) + "\t" + String(ms_to_kmh(rps_to_ms(wd.max_rps))) + "\t" + String(ms_to_kmh(rps_to_ms(wd.min_rps))) + "\n";
    return_string += "kt/t\t" + String(ms_to_knots(rps_to_ms(wd.average_rps))) + "\t" + String(ms_to_knots(rps_to_ms(wd.max_rps))) + "\t" + String(ms_to_knots(rps_to_ms(wd.min_rps))) + "\n";
    return_string += "Direction: " + String(heading) + " degrees, heading " + heading_to_abbr(heading) + "\n\n";

    return return_string;
}
#endif


#ifdef LCD_OUT
lcd_out get_LCD_string()  // get al data and format it for LCD
{
    wind_data wd;
    float heading;
    lcd_out lcd_text;
    char display_string[16];  // char array for first line, needed to format floats

    wd = get_rps_data_per_period(CYCLE_MILLIS*MEAS_PERIODS, MEAS_PERIODS);
    heading = get_heading();

    lcd_text.first = "AVG/MAX/HEADING ";
    sprintf(display_string, "%2.2f/%2.2f/%3.1f ", rps_to_ms(wd.average_rps), rps_to_ms(wd.max_rps), heading);
    lcd_text.second = String(display_string) + heading_to_abbr(heading);

    return lcd_text;
}
#endif

/* Buzzer functions */

#ifdef BUZZER_OUT
void beep()  // beep via buzzer
{
    tone(PIN_BUZZER, GHZ, BUZZER_DELAY);
    delay(BUZZER_DELAY);
    pinMode(PIN_BUZZER, INPUT);
    delay(BUZZER_DELAY);
}

void buzzer_error(int repeats) // beep several times depend on error type
{
    for (int i=0; i < repeats; i++)
    {
        beep();
    }
}
#endif
