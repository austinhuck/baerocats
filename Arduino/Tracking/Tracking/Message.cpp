#include "Message.h"


Message::Message(uint16_t id, char * timestamp)
{
	_id = id;
	_timestamp = timestamp;
}

Message::~Message()
{
}

int Message::getDataLength() const
{
	return 12; // ID (2 bytes) + Timestamp (10 Characters)
}

void Message::getData(byte * buffer) const
{
	memcpy(buffer, &_id, 2);
	memcpy(buffer + 2, _timestamp, 10);
}
