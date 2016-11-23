#ifndef GPSMessage_h
#define GPSMessage_h

#include "Message.h"

#define GPS_MESSAGE_ID 2

class GPSMessage :
	public Message
{
public:
	GPSMessage(uint32_t timestamp, bool valid, float latitude, float longitude, float altitude);
	~GPSMessage();
	int getDataLength() const override;
	void getData(byte * buffer) const override;
private:
	double _lat;
	double _lng;
	double _alt;
	bool _valid;
};
#endif

