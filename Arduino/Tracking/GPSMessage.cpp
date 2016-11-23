#include "GPSMessage.h"

GPSMessage::GPSMessage(uint32_t timestamp, bool valid, float latitude, float longitude, float altitude)
	: Message(GPS_MESSAGE_ID, timestamp)
{
	_valid = valid;
	_lat = latitude;
	_lng = longitude;
	_alt = altitude;
}

GPSMessage::~GPSMessage()
{
}

int GPSMessage::getDataLength() const
{
	return 13 + Message::getDataLength();
}

void GPSMessage::getData(byte * buffer) const
{
	// The base message fills the buffer first.
	Message::getData(buffer);

	byte * insertPtr = buffer + Message::getDataLength();

	memcpy(insertPtr, &_valid, 1);
	memcpy(insertPtr + 1, &_lat, 4);
	memcpy(insertPtr + 5, &_lng, 4);
	memcpy(insertPtr + 9, &_alt, 4);
}
