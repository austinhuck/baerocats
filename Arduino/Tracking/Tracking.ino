#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <utility/imumaths.h>
#include <stdint.h>
#include <Wire.h>

#include "IMUMessage.h"
#include "XBeeComm.h"



Adafruit_BNO055 * bno;
XBeeComm * xbee;

char timestamp[] = { '0', '0', '0', '0',  '0', '0', '.', '0', '0', '0' };

const int XBeeStatus = 22;
const int IMUStatus = 23;
const int GPSStatus = 24;
const int GPSFix = 7;

void setup()
{
	// Configure pins.
	pinMode(XBeeStatus, OUTPUT);
	pinMode(IMUStatus, OUTPUT);
	pinMode(GPSStatus, OUTPUT);
	pinMode(GPSFix, INPUT);
	
	// Prepare USB Debug Serial
	Serial.begin(9600);

	// XBee Serial (Serial1)
	Serial1.begin(57600);
	xbee = new XBeeComm(Serial1);

	if (xbee->CheckRadio())
	{
		digitalWrite(XBeeStatus, HIGH);
	}
	else
	{
		while (true)
		{
			digitalWrite(XBeeStatus, !digitalRead(XBeeStatus));
			delay(500);
		}
	}

	// Prepare IMU Communcation
	bno = new Adafruit_BNO055(55);

	if (bno->begin())
	{
		digitalWrite(IMUStatus, HIGH);
	}
	else
	{
		while (true)
		{
			digitalWrite(IMUStatus, !digitalRead(IMUStatus));
			delay(500);
		}
	}

	// Begin GPS Communication
	//Serial2.begin(9600);
	//digitalRead(GPSFix);	
}

void loop()
{
	IMUMessage * imuMessage;

	imu::Vector<3> accel = bno->getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
	imu::Vector<3> euler = bno->getVector(Adafruit_BNO055::VECTOR_EULER);

	imuMessage = new IMUMessage(timestamp, accel, euler);
	xbee->SendMessage(imuMessage);
	delete imuMessage;

	delay(1000);
}



