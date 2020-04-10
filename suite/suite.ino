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
 *  MQ-X: a suite of eight different air sensors.   
 *    
 *  The SPG30 and Si7021 sensors communicate over I2C; the Gravity
 *  sensor uses UART communication on a single digital pin
 *  (facilitated by SoftwareSerial package).
 *  
 *  The MQ sensors are analog output. In order to read all eight
 *  simultaneously, they are digitized by a MCP3008 chip.  
 * 
 */
#include "Adafruit_Si7021.h"
#include <Wire.h>
#include "Adafruit_SGP30.h"
#include <DFRobotHCHOSensor.h>
#include <SoftwareSerial.h>
#include <Adafruit_MCP3008.h>

//Define pins
#define hchoPin 7
#define mcpCLK 8
#define mcpDOUT 9
#define mcpDIN 10
#define mcpCS 11

//Define sensor objects
Adafruit_Si7021 si7021 = Adafruit_Si7021();
Adafruit_SGP30 sgp;
#define hchoPin 7
SoftwareSerial hchoSerial(hchoPin, hchoPin);
DFRobotHCHOSensor hchoSensor(&hchoSerial);
Adafruit_MCP3008 adc;

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



void setup() {
  Serial.begin(115200);
  
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

  adc.begin(mcpCLK, mcpDIN, mcpDOUT,mcpCS);

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
  float mq[8];

  
  while(hchoSensor.available()==0)
  {
    //HCHO = hchoSensor.uartReadPPM();
    delay(1);
  }
  HCHO = hchoSensor.uartReadPPM();  

  for(int i=0; i<8; i++){
    mq[i] = adc.readADC(i)*5./1023;
  }
  

  //DO A SERIAL PRINT OF ALL DATA
  Serial.print("Humidity: "); Serial.print(hum, 2); Serial.print(", ");
  
  Serial.print("Temp: "); Serial.print(temp_f, 2); Serial.print(", ");
  
  Serial.print("TVOC: "); Serial.print(TVOC); Serial.print(" ppb, ");
  
  Serial.print("eCOtwo: "); Serial.print(CO2); Serial.print(" ppm, ");
  
  Serial.print("HCHO: "); Serial.print(HCHO,3); Serial.print(" ppm, ");

  for(int i=0;i<7; i++){
    Serial.print(mq[i],2);
    Serial.print(", "); 
  }
  Serial.println(mq[7]);

  
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

  
  delay(1000);
}
