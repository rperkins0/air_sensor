/* Simultaenously run the following sensors:
 *  
 *  SGP30: an air quality sensor; breakout board by Adafruit
 *  
 *  SI7021: Humidity and temperature sensor; breakout board by
 *    Adafruit.
 *    
 *  Gravity: Formaldehyde (HCHO) sensor, breakout board by DFRobot;
 *    sensor unknown.
 *    
 *  The SPG30 and Si7021 sensors communicate over I2C; the Gravity
 *  sensor uses UART communication on a single digital pin
 *  (facilitated by SoftwareSerial package).
 * 
 */
#include "Adafruit_Si7021.h"
#include <Wire.h>
#include "Adafruit_SGP30.h"
#include <DFRobotHCHOSensor.h>
#include <SoftwareSerial.h>

//Define sensor objects
Adafruit_Si7021 si7021 = Adafruit_Si7021();
Adafruit_SGP30 sgp;
#define hchoPin 7
SoftwareSerial hchoSerial(hchoPin, hchoPin);
DFRobotHCHOSensor hchoSensor(&hchoSerial);
  

//The following was copied and pasted from the SGP30 example code 

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


//
//Define (remaining) pins
int TVOC_alarm_pin = 11;
float TVOC_alarm_level = 300.0;
bool TVOC_alarm_trip = false;
int humidity_high_pin = 10;
int humidity_low_pin  =  9;



void setup() {
  Serial.begin(115200);

  //initialize TVOC alarm pin
  pinMode(TVOC_alarm_pin, OUTPUT);
  digitalWrite(TVOC_alarm_pin, LOW);

  //initialize humidity high/low alarm pins
  pinMode(humidity_high_pin, OUTPUT);
  pinMode(humidity_low_pin, OUTPUT );
  // wait for serial port to open
  while (!Serial) {
    delay(10);
  }
  
  if (!si7021.begin()) {
    Serial.println("Did not find Si7021 sensor!");
    while (true)
      ;
  }

  if (! sgp.begin()) {
    Serial.println("SGP sensor not found");
    while(1);
  }

  //initialize HCHO serial communication
  hchoSerial.begin(9600);
  hchoSerial.listen();

  Serial.println("setup done");

}




int counter=0;
void loop() {

  //SGP Sensor read
  if (! sgp.IAQmeasure()) {
    Serial.println("SGP measrement failed");
    return;
  }
  
  //READ DATA FROM SENSORS
  float hum = si7021.readHumidity();
  float temp_f = si7021.readTemperature()*9/5+32;
  float TVOC = sgp.TVOC;
  float CO2 = sgp.eCO2; 
  float HCHO = -1;
  while(hchoSensor.available()==0)
  {
    //HCHO = hchoSensor.uartReadPPM();
    delay(1);
  }
  HCHO = hchoSensor.uartReadPPM();  
  
  //logical statements for humidity-level led's
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


  //DO A SERIAL PRINT OF ALL DATA
  Serial.print("\tHumidity: ");
  Serial.print(hum, 2);
  Serial.print("\tTemp: ");
  Serial.print(temp_f, 2);
  Serial.print("\tTVOC: "); Serial.print(TVOC); Serial.print(" ppb");
  Serial.print("\teCOtwo: "); Serial.print(CO2); Serial.print(" ppm");
  Serial.print("\tHCHO: "); Serial.print(HCHO,3); Serial.println(" ppm");
  
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
  
  delay(1000);
}
