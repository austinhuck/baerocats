#include "IMUMessage.h"


IMUMessage::IMUMessage(uint32_t timestamp, imu::Vector<3> acceleration, imu::Quaternion orientation) :
	Message(IMU_MESSAGE_ID, timestamp)
{
	_accelx = acceleration.x();
	_accely = acceleration.y();
	_accelz = acceleration.z();
	_orientationw = orientation.w();
	_orientationx = orientation.x();
	_orientationy = orientation.y();
	_orientationz = orientation.z();
}

IMUMessage::~IMUMessage()
{
}

int IMUMessage::getDataLength() const
{
	return 28 + Message::getDataLength();
}

void IMUMessage::getData(byte * buffer) const
{
	// The base message fills the buffer first.
	Message::getData(buffer);

	byte * insertPtr = buffer + Message::getDataLength();

	memcpy(insertPtr, &_accelx, 4);
	memcpy(insertPtr + 4, &_accely, 4);
	memcpy(insertPtr + 8, &_accelz, 4);
	memcpy(insertPtr + 12, &_orientationw, 4);
	memcpy(insertPtr + 16, &_orientationx, 4);
	memcpy(insertPtr + 20, &_orientationy, 4);  
	memcpy(insertPtr + 24, &_orientationz, 4);
}
