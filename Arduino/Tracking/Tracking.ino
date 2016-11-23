#include <Adafruit_GPS.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <utility/imumaths.h>
#include <stdint.h>
#include <Wire.h>
#include <extEEPROM.h>

#include "IMUMessage.h"
#include "GPSMessage.h"
#include "XBeeComm.h"

unsigned long gpsTime = 0;
unsigned long lastSyncTime = 0;
unsigned long lastSendTime = 0;
unsigned long lastSampleTime = 0;

Adafruit_GPS * gps;
Adafruit_BNO055 * bno;
XBeeComm * xbee;
extEEPROM * eep;

// Pin Assignments
const int XBeeStatus = 22;
const int IMUStatus = 23;
const int GPSStatus = 24;
const int EEPStatus = 25;
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

	//extEEPROM setup
	eep = new extEEPROM(kbits_256, 1, 64);
	uint8_t eepStatus = eep->begin(twiClock400kHz);      //go fast!
	if (eepStatus)
	{
		Serial.print("Error with EEPROM - ");
		Serial.println(eepStatus);

		while (true)
		{
			digitalWrite(EEPStatus, !digitalRead(EEPStatus));
			delay(500);
		}
	}

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

			Serial.println("Timestamp, Accel X, Accel Y, Accel Z, Quat W, Quat X, Quat Y, Quat Z");

			Address = 0;

			while (Address + 31 <= MaxAddress)
			{
				byte data[32];

				eep->read(Address, data, 32);

				Address += 32;

				memcpy(&timestamp, data, 4);
				memcpy(&accelX, data + 4, 4);
				memcpy(&accelY, data + 8, 4);
				memcpy(&accelZ, data + 12, 4);
				memcpy(&quatW, data + 16, 4);
				memcpy(&quatX, data + 20, 4);
				memcpy(&quatY, data + 24, 4);
				memcpy(&quatZ, data + 28, 4);

				Serial.print(timestamp);
				Serial.print(',');
				Serial.print(accelX);
				Serial.print(',');
				Serial.print(accelY);
				Serial.print(',');
				Serial.print(accelZ);
				Serial.print(',');
				Serial.print(quatW);
				Serial.print(',');
				Serial.print(quatX);
				Serial.print(',');
				Serial.print(quatY);
				Serial.print(',');
				Serial.println(quatZ);
			}
		}
	}
	
	// XBee Serial (Serial1)
	Serial1.begin(57600);
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

	// Begin GPS Communication
	Serial2.begin(9600);
	gps = new Adafruit_GPS(&Serial2);
	gps->begin(9600);
	
	// Configure GPS to send RMC (recommended minimum) and GGA (fix data)
	gps->sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);

	// Configure GPS to update at 1 Hz
	gps->sendCommand(PMTK_API_SET_FIX_CTL_1HZ);

	// Activate buzzer to indicate successful setup
	for (int i = 0; i < 25; i++)
	{
		for (int i = 3500; i < 4500; i += 10)
		{
			tone(Buzzer, i);
			delay(1);
		}

		for (int i = 4500; i > 3500; i -= 10)
		{
			tone(Buzzer, i);
			delay(1);
		}
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

	// Every 200ms (5Hz) save a sample
	unsigned long currentTime = millis();
	if (currentTime - lastSampleTime > 50)
	{
		lastSampleTime = currentTime;

		imu::Vector<3> accel = bno->getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
		imu::Quaternion quat = bno->getQuat();

		// save data sample
		if ((Address + 31) <= MaxAddress)
		{
			// Statistics: 12-16ms

			//unsigned long writeStart = millis();

			//Serial.print("Sample Address [");
			//Serial.print(Address);
			//Serial.print("] ");

			byte data[32];

			memcpy(data, &currentTime, 4);
			memcpy(data + 4, &accel.x(), 4);
			memcpy(data + 8, &accel.y(), 4);
			memcpy(data + 12, &accel.z(), 4);
			memcpy(data + 16, &quat.w(), 4);
			memcpy(data + 20, &quat.x(), 4);
			memcpy(data + 24, &quat.y(), 4);
			memcpy(data + 28, &quat.z(), 4);

			eep->write(Address, data, 32);

			Address += 32;

			//Serial.print("Time to Write: ");
			//Serial.println(millis() - writeStart);
		}

		// Every second, send out the current data.
		if (currentTime - lastSendTime > 1000)
		{
			// Statistics: 5-10ms

			//unsigned long sendStart = millis();

			lastSendTime = currentTime;

			IMUMessage imuMessage(currentTime, accel, quat);
			xbee->SendMessage(&imuMessage);

			GPSMessage gpsMessage(currentTime, gps->fix, gps->latitudeDegrees, gps->longitudeDegrees, gps->altitude);
			xbee->SendMessage(&gpsMessage);

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



