#include <XBee.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

File DBDataFile;

String DataFileName="db.txt";
#define SAMPLE_DELAY 1000

XBee xbee;

// Pin Assignments
const int Status = 6;
const int StatusGnd = 7;
const int RunSelect = 10;

uint8_t slCmd[] = { 'D','B' };
AtCommandRequest atRequest = AtCommandRequest(slCmd);

AtCommandResponse atResponse = AtCommandResponse();

void setup()
{
	// Pin Configuration
	pinMode(Status, OUTPUT);
  pinMode(StatusGnd, OUTPUT);
  pinMode(RunSelect, INPUT);
  digitalWrite(Status, LOW);
  digitalWrite(StatusGnd, LOW);
  
	Serial.begin(115200);
  Serial.println("Initializing SD card...");
	//SD setup
	if (!SD.begin(53))
	{
		Serial.println("SD Initialization failed on pin 53");

		while (true)
		{
			digitalWrite(Status, !digitalRead(Status));
			delay(100);
		}
	}

  Serial.println("Initializing XBee Radio...");
	// XBee Serial (Serial1)
	Serial1.begin(115200);
  xbee = XBee();
  xbee.setSerial(Serial1);

  Serial.println("Running...");
}

void loop()
{
  if (!digitalRead(RunSelect))
  {
    digitalWrite(Status, LOW);
    return;
  }

  digitalWrite(Status, HIGH);

  Serial.println("Requesting DB");
	// Every SAMPLE_DELAY save a sample
  xbee.send(atRequest);

  XBeeResponse r;
  
  do
  {
    xbee.readPacket(5000);
  }
  while (xbee.getResponse().getApiId() != AT_COMMAND_RESPONSE);
  
  xbee.getResponse().getAtCommandResponse(atResponse);
  
  if (atResponse.getStatus() == 0)
  {   
    uint8_t* value = atResponse.getValue();
    int db = value[0];
    
    // open the file. note that only one file can be open at a time,
    // so you have to close this one before opening another.
    DBDataFile = SD.open(DataFileName, FILE_WRITE);
    if (DBDataFile)
    {
      Serial.println(db);
      DBDataFile.println(db);
      DBDataFile.close();
    }
    else
    {
      // if the file didn't open, print an error:
      Serial.println("error opening data file");
    }
  }
  delay(SAMPLE_DELAY);
}

//uint32_t getTime()
//{
//	return gpsTime + (millis() - lastSyncTime);
//}
//
//uint32_t setTime()
//{
//	// Save off the current time.
//	gpsTime = gps->hour * 3600000;
//	gpsTime += gps->minute * 60000;
//	gpsTime += gps->seconds * 1000;
//	gpsTime += gps->milliseconds;
//
//	lastSyncTime = millis();
//}



