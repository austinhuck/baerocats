#include "DataMessage.h"

DataMessage::DataMessage(
  double lat,
  double lng,
  double ax,
  double ay,
  double az,
  double qw,
  double qx,
  double qy,
  double qz,
  double wx,
  double wy,
  double wz,
  double alt,
  double light)
{
	Type = MsgType::Data;
  Latitude = lat;
  Longitude = lng;
  AccelX = ax;
  AccelY = ay;
  AccelZ = az;
  QuatW = qw;
  QuatX = qx;
  QuatY = qy;
  QuatZ = qz;
  OmegaX = wx;
  OmegaY = wy;
  OmegaZ = wz;
  Altitude = alt;
  Light = light;
}

int DataMessage::getDataLength() const
{
  return 64;
}

void DataMessage::getData(byte * buffer) const
{
	// The base message fills the buffer first.
	Message::getData(buffer);
1
	byte * insertPtr = buffer + UNKNOWN_SIZE;

	memcpy(insertPtr, &Latitude, 4);
	memcpy(insertPtr + 4, &Longitude, 4);
  memcpy(insertPtr + 8, &AccelX, 4);
  memcpy(insertPtr + 12, &AccelY, 4);
  memcpy(insertPtr + 16, &AccelZ, 4);
  memcpy(insertPtr + 20, &QuatW, 4);
  memcpy(insertPtr + 24, &QuatX, 4);
  memcpy(insertPtr + 28, &QuatY, 4);
  memcpy(insertPtr + 32, &QuatZ, 4);
  memcpy(insertPtr + 36, &OmegaX, 4);
  memcpy(insertPtr + 40, &OmegaY, 4);
  memcpy(insertPtr + 44, &OmegaZ, 4);
  memcpy(insertPtr + 48, &Altitude, 4);
  memcpy(insertPtr + 52, &Light, 4);
}
