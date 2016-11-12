#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

Adafruit_BNO055 bno = Adafruit_BNO055(55);

const int XBeeStatus = 22;
const int IMUStatus = 23;
const int GPSStatus = 24;
const int GPSFix = 7;
const byte SerialLow[] = { 0x41, 0x5A, 0xE1, 0xC1 };

bool valid = false;
int remainingBytes = -1;
int receiveBufferIndex = 0;
byte receiveBuffer[256];

struct XBeeApiFrame
{
	int Length;
	byte Data[];
	byte Checksum;
};

void setup()
{
	pinMode(XBeeStatus, OUTPUT);
	pinMode(IMUStatus, OUTPUT);
	pinMode(GPSStatus, OUTPUT);
	pinMode(GPSFix, INPUT);

	int count;
	byte data[24];

	// Prepare USB Debug Serial
	Serial.begin(9600);

	// XBee Serial
	Serial1.begin(57600);

	// Test XBee communcation by entering AT command mode.
	while (!Serial);

	byte atserial[] = { 0x7E, 0x00, 0x04, 0x08, 0x01, 0x53, 0x4C, 0x57 };
	Serial.print("Sending Bytes: ");
	Serial.write(atserial, 8);
	Serial.println();
	Serial1.write(atserial, 8);
	while (Serial1.available() == false);
	count = Serial1.readBytes(data, 24);
	Serial.print("Received Bytes: ");
	for (int i = 0; i < count; i++)
	{
		Serial.print(data[i], HEX);
	}
	Serial.println();
	while (true);
	digitalWrite(XBeeStatus, HIGH);

	// Begin IMU Communication
	if (bno.begin())
	{
		digitalWrite(IMUStatus, HIGH);
	}

	// Begin GPS Communication
	//Serial2.begin(9600);
	//digitalRead(GPSFix);

	delay(1000);

	bno.setExtCrystalUse(true);
}

void loop()
{
	/* Get a new sensor event */
	sensors_event_t event;
	bno.getEvent(&event);

	/* Display the floating point data */
	Serial.print("X: ");
	Serial.print(event.orientation.x, 4);
	Serial.print("\tY: ");
	Serial.print(event.orientation.y, 4);
	Serial.print("\tZ: ");
	Serial.print(event.orientation.z, 4);
	Serial.println("");
}



void receive()
{
	int count;
	XBeeApiFrame frame;

	if (Serial1.available())
	{
		// If the receiver buffer index has content, then we're working on building a message.
		if (receiveBufferIndex != -1)
		{
			count = Serial1.readBytesUntil(0x7E, receiveBuffer + receiveBufferIndex, 256 - receiveBufferIndex);



		}
		else
		{
			count = Serial1.readBytesUntil(0x7E, receiveBuffer, 256);

			

		}


	}
}
