#include "Adafruit_Si7021.h"
#include <Wire.h>
#include "Adafruit_SGP30.h"
#include <LCD.h>
#include <LiquidCrystal_I2C.h>

Adafruit_Si7021 si7021 = Adafruit_Si7021();
Adafruit_SGP30 sgp;

/* return absolute humidity [mg/m^3] with approximation formula
* @param temperature [°C]
* @param humidity [%RH]
*/
uint32_t getAbsoluteHumidity(float temperature, float humidity) {
    // approximation formula from Sensirion SGP30 Driver Integration chapter 3.15
    const float absoluteHumidity = 216.7f * ((humidity / 100.0f) * 6.112f * exp((17.62f * temperature) / (243.12f + temperature)) / (273.15f + temperature)); // [g/m^3]
    const uint32_t absoluteHumidityScaled = static_cast<uint32_t>(1000.0f * absoluteHumidity); // [mg/m^3]
    return absoluteHumidityScaled;
}

int TVOC_alarm_pin = 11;
float TVOC_alarm_level = 300.0;
bool TVOC_alarm_trip = false;

int humidity_high_pin = 10;
int humidity_low_pin  =  9;


//LCD setup
#define I2C_ADDR    0x27 // <<----- Add your address here.  Find it from I2C Scanner
#define BACKLIGHT_PIN     3
#define En_pin  2
#define Rw_pin  1
#define Rs_pin  0
#define D4_pin  4
#define D5_pin  5
#define D6_pin  6
#define D7_pin  7
int button_high = 4;
int button_sense = 2;
LiquidCrystal_I2C  lcd(I2C_ADDR,En_pin,Rw_pin,Rs_pin,D4_pin,D5_pin,D6_pin,D7_pin);


void setup() {
  Serial.begin(115200);

  //initialize TVOC alarm pin
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(TVOC_alarm_pin, OUTPUT);
  digitalWrite(TVOC_alarm_pin, LOW);

  //initialize humidity high/low alarm pins
  pinMode(humidity_high_pin, OUTPUT);
  pinMode(humidity_low_pin, OUTPUT );
  // wait for serial port to open
  while (!Serial) {
    delay(10);
  }

  Serial.println("Si7021 test!");
  
  if (!si7021.begin()) {
    Serial.println("Did not find Si7021 sensor!");
    while (true)
      ;
  }

  Serial.print("Found model ");
  switch(si7021.getModel()) {
    case SI_Engineering_Samples:
      Serial.print("SI engineering samples"); break;
    case SI_7013:
      Serial.print("Si7013"); break;
    case SI_7020:
      Serial.print("Si7020"); break;
    case SI_7021:
      Serial.print("Si7021"); break;
    case SI_UNKNOWN:
    default:
      Serial.print("Unknown");
  }
  Serial.print(" Rev(");
  Serial.print(si7021.getRevision());
  Serial.print(")");
  Serial.print(" Serial #"); Serial.print(si7021.sernum_a, HEX); Serial.println(si7021.sernum_b, HEX);

  if (! sgp.begin()) {
    Serial.println("SGP sensor not found");
    while(1);
  }
  Serial.print("Found SGP30 serial #");
  Serial.print(sgp.serialnumber[0], HEX);
  Serial.print(sgp.serialnumber[1], HEX);
  Serial.println(sgp.serialnumber[2], HEX);

  //LCD setup
  lcd.begin (16,2); //  <<----- My LCD was 16x2
  // Switch on the backlight
  lcd.setBacklightPin(BACKLIGHT_PIN,POSITIVE);
  lcd.setBacklight(HIGH);
  lcd.home (); // go home
  pinMode(button_high, OUTPUT);
  pinMode(button_sense, INPUT);
  digitalWrite(button_high, HIGH);

}




int counter=0;
void loop() {

  //READ DATA FROM SENSORS
  float hum = si7021.readHumidity();
  
  
  if( hum > 45 ) {
    digitalWrite(humidity_high_pin,HIGH);
  }
  else {
    digitalWrite(humidity_high_pin,LOW);
  }
  
  if( hum < 30 ) {
    digitalWrite(humidity_low_pin,HIGH);
  }
  else
  {
    digitalWrite(humidity_low_pin,LOW);
  }

  //SGP Sensor read
  if (! sgp.IAQmeasure()) {
    Serial.println("Measrement failed");
    return;
  }


  Serial.print("\tHumidity: ");
  Serial.print(hum, 2);
  Serial.print("\tTemp: ");
  Serial.print(si7021.readTemperature()*9/5+32, 2);
  Serial.print("\tTVOC: "); Serial.print(sgp.TVOC); Serial.print(" ppb");
  Serial.print("\teCO2: "); Serial.print(sgp.eCO2); Serial.println(" ppm");

  counter++;
  if (counter==30) {
    counter=0;
//    uint16_t TVOC_base, eCO2_base;
//    if (! sgp.getIAQBaseline(&eCO2_base, &TVOC_base)) {
//        Serial.println("Cannot get baseline SGP readings");
//        return;
//    }
//    Serial.print("****Baseline values: eCO2: 0x"); Serial.print(eCO2_base, HEX);
//    Serial.print(" & TVOC: 0x"); Serial.println(TVOC_base, HEX);
  }

  //see if TVOC reading has gone high
  //if so, sound the alarm 
  if (sgp.TVOC > TVOC_alarm_level) {
    TVOC_alarm_trip = true;
    digitalWrite(TVOC_alarm_pin, HIGH);  //alert that TVOC level is currently high
  } else {
   if (TVOC_alarm_trip) {
    //make led blink
    //let everyone know a high level was sensed in past
    digitalWrite(TVOC_alarm_pin, !digitalRead(TVOC_alarm_pin));
    } 
  }

 //LCD DISPLAY
 lcd.setCursor (0,0);        // go to start of 2nd line
 lcd.print("TVOC:");
 lcd.print(sgp.TVOC,DEC);
 lcd.setCursor(0,1);
 lcd.print("Hum:");
 hum = si7021.readHumidity();
 lcd.print((long) hum, DEC);
 lcd.print("  T: ");
 lcd.print(si7021.readTemperature()*9/5+32, DEC);
  
 if (digitalRead(button_sense)) {
 // Backlight on/off every 3 seconds
 lcd.setBacklight(HIGH);      // Backlight off
 } else {
 lcd.setBacklight(LOW);     // Backlight on 
 }

  
  delay(3000);
}
