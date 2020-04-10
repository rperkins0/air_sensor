#include <DFRobotHCHOSensor.h>
#include <SoftwareSerial.h>

#define SerialPin 7

SoftwareSerial sensorSerial(SerialPin,SerialPin);

DFRobotHCHOSensor hchoSensor(&sensorSerial);

void setup() {
  // put your setup code here, to run once:
  sensorSerial.begin(9600);   //the baudrate of HCHO is 9600
  sensorSerial.listen();
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(hchoSensor.available()>0)
  {
    Serial.println(hchoSensor.uartReadPPM());
  }
}
