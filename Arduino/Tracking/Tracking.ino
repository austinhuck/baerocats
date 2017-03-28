#include <Adafruit_GPS.h>
#include <Adafruit_BNO055_Baerocats.h>
#include <Adafruit_Sensor.h>
#include <utility/imumaths.h>
#include <stdint.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>


#include "Message.h"
#include "DataMessage.h"
#include "XBeeComm.h"
File IMUDataFile;

// !!! TRANSMIT_DELAY must be greater than and 
// a multiple of SAMPLE_DELAY
String DataFileName="reamer.txt";
#define SAMPLE_DELAY 100
#define TRANSMIT_DELAY 1000

unsigned long gpsTime = 0;
unsigned long lastSyncTime = 0;
unsigned long lastSendTime = 0;
unsigned long lastSampleTime = 0;

Adafruit_GPS * gps;
Adafruit_BNO055 * bno;
XBeeComm * xbee;

// Pin Assignments
const int XBeeStatus = 22;
const int IMUStatus = 23;
const int GPSStatus = 24;
const int SDStatus = 25;
const int Ground = 7;
const int RecordStatus = 6;
const int ModeSelect = 10;
const int Buzzer = 40;

//Recording Settings ...
bool Record;
unsigned int Address = 0;
const unsigned int MaxAddress = 32767; // 32KB

void setup()
{
	// Pin Configuration
	pinMode(XBeeStatus, OUTPUT);
	pinMode(IMUStatus, OUTPUT);
	pinMode(GPSStatus, OUTPUT);
	pinMode(Ground, OUTPUT);
	pinMode(RecordStatus, OUTPUT);
	pinMode(ModeSelect, INPUT);
	pinMode(Buzzer, OUTPUT);

	digitalWrite(Ground, LOW);

	delay(100);

	Serial.begin(115200);
  Serial.print("Initializing SD card...");
	//SD setup
	if (!SD.begin(53))
	{
		Serial.print("SD Initialization failed on pin 53");

		while (true)
		{
			digitalWrite(SDStatus, !digitalRead(SDStatus));
			delay(500);
		}
	}

  Serial.println("initialization done.");

	if (digitalRead(ModeSelect))
	{
		// Record Mode (HIGH)
		digitalWrite(RecordStatus, HIGH);

		// Prepare USB Debug Serial
		Serial.println("Record Mode");
	}
	else
	{
		// Playback Mode (LOW)
		digitalWrite(RecordStatus, LOW);

		while (true)
		{
			// Clear inbound serial data.
			while (Serial.available())
			{
				Serial.read();
			}

			// Wait for a serial connection.
			while (Serial.available() == false)
			{
				digitalWrite(RecordStatus, !digitalRead(RecordStatus));
				delay(100);
			}

			digitalWrite(RecordStatus, LOW);

			Serial.println("Playback Mode");

			unsigned long timestamp;
			float accelX;
			float accelY;
			float accelZ;
			float quatW;
			float quatX;
			float quatY;
			float quatZ;

			Serial.println("Timestamp, Accel X, Accel Y, Accel Z, Quat W, Quat X, Quat Y, Quat Z, Latitude, Longitude");
      IMUDataFile = SD.open(DataFileName);
			Address = 0;

			while (IMUDataFile.available())
			{
				Serial.write(IMUDataFile.read());
			}
      IMUDataFile.println("Timestamp, Accel X, Accel Y, Accel Z, Quat W, Quat X, Quat Y, Quat Z, Latitude, Longitude");
      IMUDataFile.close();
		}
	}
	
	// XBee Serial (Serial1)
	Serial1.begin(19200);
	xbee = new XBeeComm(Serial1);

	if (xbee->CheckRadio())
	{
		digitalWrite(XBeeStatus, HIGH);
	}
	else
	{
		Serial.println("Error with XBee");

		while (true)
		{
			digitalWrite(XBeeStatus, !digitalRead(XBeeStatus));
			delay(500);
		}
	}

	// Prepare IMU Communcation
	bno = new Adafruit_BNO055(55);

	// Begin in default mode (NDOF)
	if (bno->begin())
	{
		digitalWrite(IMUStatus, HIGH);
	}
	else
	{
		Serial.println("Error with IMU");

		while (true)
		{
			digitalWrite(IMUStatus, !digitalRead(IMUStatus));
			delay(500);
		}
	}

	bno->setExtCrystalUse(true);
	bno->setGRange(Adafruit_BNO055::G_RANGE_8G);

	Serial.print("Set IMU G-Range: 8G");

	// Begin GPS Communication
	Serial2.begin(9600);
	gps = new Adafruit_GPS(&Serial2);
	gps->begin(9600);
	
	// Configure GPS to send RMC (recommended minimum) and GGA (fix data)
	gps->sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);

	// Configure GPS to update at 1 Hz
	gps->sendCommand(PMTK_API_SET_FIX_CTL_1HZ);

	// Activate buzzer to indicate successful setup
	for (int i = 0; i < 10; i++)
	{
		for (int j = 3000; j < 5000; j += 20)
		{
			tone(Buzzer, j);
			delay(2);
		}

//		for (int j = 4500; j > 3500; j -= 10)
//		{
//			tone(Buzzer, j);
//			delay(1);
//		}
	}

	noTone(Buzzer);
}

void loop()
{
	// Read on the gps and see if a NMEA was received.
	char c = gps->read();

	if (gps->newNMEAreceived())
	{
		// Statistics: 1-2ms

		// parsing sets the newNMEAreceived() flag to false
		// we can fail to parse a sentence in which case we should just wait for another
		if (gps->parse(gps->lastNMEA()))   
		{
			//if (gps->fix)
			//{
			//	setTime();
			//}
		}
		else
		{
			Serial.println("Parse Failure");
		}
	}

	// Every SAMPLE_DELAY save a sample
	unsigned long currentTime = millis();
	if (currentTime - lastSampleTime >= SAMPLE_DELAY)
	{
		lastSampleTime = currentTime;

		imu::Vector<3> accel = bno->getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
		imu::Quaternion quat = bno->getQuat();

		// save data sample
   
    // open the file. note that only one file can be open at a time,
    // so you have to close this one before opening another.
    IMUDataFile = SD.open(DataFileName, FILE_WRITE);
    if (IMUDataFile) {
    IMUDataFile.print(currentTime);
    IMUDataFile.print(",");
    IMUDataFile.print(accel.x());
    IMUDataFile.print(",");
    IMUDataFile.print(accel.y());
    IMUDataFile.print(",");
    IMUDataFile.print(accel.z());
    IMUDataFile.print(",");
    IMUDataFile.print(quat.w());
    IMUDataFile.print(",");
    IMUDataFile.print(quat.x());
    IMUDataFile.print(",");
    IMUDataFile.print(quat.y());
    IMUDataFile.print(",");
    IMUDataFile.print(quat.z());
    IMUDataFile.print(",");
    IMUDataFile.print(gps->latitudeDegrees);
    IMUDataFile.print(",");
    IMUDataFile.print(gps->longitudeDegrees);
    IMUDataFile.println("");
    IMUDataFile.close();

    } else {
    // if the file didn't open, print an error:
    Serial.println("error opening data file");
    }
		// Every TRANSMIT_DELAY, send out the current data.
		if (currentTime - lastSendTime > TRANSMIT_DELAY)
		{
			// Statistics: 5-10ms

			//unsigned long sendStart = millis();

			lastSendTime = currentTime;

			DataMessage dataMessage(
			  (double)gps->latitudeDegrees,
			  (double)gps->longitudeDegrees,
			  (double)accel.x(),
			  (double)accel.y(),
			  (double)accel.z(),
			  (double)quat.w(),
			  (double)quat.x(),
			  (double)quat.y(),
			  (double)quat.z(),
			  0.0,0.0,0.0,0.0,0.0);
			xbee->SendMessage(&dataMessage);
      
			//Serial.print("Time to Send: ");
			//Serial.println(millis() - sendStart);
		}
	}
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



