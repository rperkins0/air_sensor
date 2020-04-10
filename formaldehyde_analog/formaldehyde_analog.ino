/*
  fomaldehyde_analog
  
  Simple implementation to do an analog read of DFRobot's Gravity 
  formadehyde sensor.  
  
  Make sure sensor is switched 
*/

#define AnalogPin A0
#define vref 5.0

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

// the loop routine runs over and over again forever:
void loop() {
  Serial.println(analogReadPPM());
  delay(1000);
}

float analogReadPPM()
{
  float analogVoltage = analogRead(AnalogPin) / 1024.0 * vref;
  float ppm = 3.125 * analogVoltage - 1.25;
  if(ppm<0) ppm = 0;
  else if(ppm>5) ppm=5;
  return ppm;
}
