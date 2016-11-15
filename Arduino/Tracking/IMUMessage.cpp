#include "IMUMessage.h"


IMUMessage::IMUMessage(char * timestamp, imu::Vector<3> acceleration, imu::Vector<3> euler) :
	Message(IMU_MESSAGE_ID, timestamp)
{
	_accelx = acceleration.x();
	_accely = acceleration.y();
	_accelz = acceleration.z();
	_eulerx = euler.x();
	_eulery = euler.y();
	_eulerz = euler.z();
}

IMUMessage::~IMUMessage()
{
}

int IMUMessage::getDataLength() const
{
	return 24 + Message::getDataLength();
}

void IMUMessage::getData(byte * buffer) const
{
	// The base message fills the buffer first.
	Message::getData(buffer);

	byte * insertPtr = buffer + Message::getDataLength();

	memcpy(insertPtr, &_accelx, 4);
	memcpy(insertPtr + 4, &_accely, 4);
	memcpy(insertPtr + 8, &_accelz, 4);
	memcpy(insertPtr + 12, &_eulerx, 4);
	memcpy(insertPtr + 16, &_eulery, 4);
	memcpy(insertPtr + 20, &_eulerz, 4);
}
