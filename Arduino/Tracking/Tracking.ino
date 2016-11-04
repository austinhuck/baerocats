#include <SoftwareSerial.h>

#define DEBUG true

const int LED = 13;
const int CTS = 5;
const int RX = 2;
const int TX = 3;

SoftwareSerial xbeeSerial =  SoftwareSerial(RX, TX);

int count = 0;
bool ledStatus = false;
bool ctsStatus = false;
char data[100];

void setup()
{
  pinMode(LED,OUTPUT);
  pinMode(CTS,INPUT);
  pinMode(RX,INPUT);
  pinMode(TX,OUTPUT);

  #if DEBUG
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Arduino Console");
  #endif
  
  xbeeSerial.begin(9600);
  xbeeSerial.println("xBee Port");
}

void loop()
{
  int i = 0;
  byte ctsStatus = 1;
  count++;
  #if DEBUG
  Serial.println(count);
  #endif

  if (xbeeSerial.available())
  {
    #if DEBUG
    Serial.write("Rx\r\n");
    #endif
    while (xbeeSerial.available() && i < 100)
    {
      digitalWrite(LED, HIGH);
      delay(250);
      digitalWrite(LED, LOW);
      data[i] = xbeeSerial.read();
  
      i++;
    }
  }

  ctsStatus = digitalRead(CTS);
  if (ctsStatus == 0)
  {
    for (int j = 0; j != i; j++)
    {
      #if DEBUG
      Serial.write("Tx\r\n");
      #endif
      xbeeSerial.write(data[j]);
    }
  }

  delay(50);
}
