#include "Message.h"

Message::Message()
{
  ID = getNextID();
  Source = 1;
  Timestamp = millis();
  Type = MsgType::Unknown; 
}

int Message::getDataLength() const
{
  return 12;
}

void Message::getData(byte * buffer) const
{
	memcpy(buffer, &ID, 2);
  memcpy(buffer + 2, &Source, 1);
	memcpy(buffer + 3, &Timestamp, 4);
  memset(buffer + 7, 0, 4);
  memcpy(buffer + 11, &Type, 1);
}

uint16_t Message::_ID = 0;

uint16_t Message::getNextID()
{
  uint16_t id = _ID;

  if (_ID >= 65535)
  {
    _ID = 0;
  }
  else
  {
    _ID = _ID + 1;
  }

  return id;
}

void Message::memcpyrvs(void * buffer, const void * value, size_t n)
{
  for (int i = n, j = 0; i > 0; j++, i--)
  {
    memcpy(buffer + j, value + i, 1);
  }
}

