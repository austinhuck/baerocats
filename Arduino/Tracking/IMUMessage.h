#ifndef IMUMessage_h
#define IMUMessage_h

#include "Message.h"
#include <Arduino.h>
#include <utility/vector.h>
#include <utility/quaternion.h>

#define IMU_MESSAGE_ID 1

class IMUMessage :
	public Message
{
public:
	IMUMessage(uint32_t timestamp, imu::Vector<3> acceleration, imu::Quaternion orientation);
	~IMUMessage();
	int getDataLength() const override;
	void getData(byte * buffer) const override;
private:
	double _accelx;
	double _accely;
	double _accelz;
	double _orientationw;
	double _orientationx;
	double _orientationy;
	double _orientationz;
};

#endif