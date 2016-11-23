#ifndef Message_h
#define Message_h

#include <Arduino.h>

class Message
{
public:
	Message(uint16_t id, uint32_t timestamp);
	~Message();
	virtual int getDataLength() const;
	virtual void getData(byte * buffer) const;
private:
	uint16_t _id;
	uint32_t _timestamp;
};

#endif

