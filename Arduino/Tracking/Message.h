#ifndef Message_h
#define Message_h

#include <Arduino.h>

class Message
{
public:
	Message();

  enum MsgType
  {
    Unknown = 0,
    Data = 1,
    Log = 2,
    Cmd = 3,
    CmdResponse = 4
  };

  int UNKNOWN_SIZE = 12;
  int DATA_SIZE = 64;

  uint16_t ID;
  uint8_t Source;
  uint32_t Timestamp;
  uint8_t Type;
  virtual int getDataLength() const;
	virtual void getData(byte * buffer) const;
protected:
  static void memcpyrvs(void * buffer, const void * value, size_t n);
private:
  static uint16_t _ID;
  static uint16_t getNextID();
};

#endif

