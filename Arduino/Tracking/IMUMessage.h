#ifndef IMUMessage_h
#define IMUMessage_h

#include "Message.h"
#include <Arduino.h>
#include <utility/vector.h>

#define IMU_MESSAGE_ID 1

class IMUMessage :
	public Message
{
public:
	IMUMessage(char * timestamp, imu::Vector<3> acceleration, imu::Vector<3> euler);
	~IMUMessage();
	int getDataLength() const override;
	void getData(byte * buffer) const override;
private:
	double _accelx;
	double _accely;
	double _accelz;
	double _eulerx;
	double _eulery;
	double _eulerz;
};

#endif