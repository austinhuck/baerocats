#ifndef XBeeComm_h
#define XBeeComm_h

#include <Arduino.h>
#include "Message.h"
#include <XBee.h>

#define EXT_1_SERIAL_H 0x0013A200
#define EXT_1_SERIAL_L 0x415AE1C1
#define EXT_2_SERIAL_H 0x0013A200
#define EXT_2_SERIAL_L 0x412692E7
#define GROUND_SERIAL_H 0x0013A200
#define GROUND_SERIAL_L 0x412692E8

class XBeeComm
{
public:
	XBeeComm(Stream &stream);
	~XBeeComm();
	void SendMessage(const Message * msg);
	void ReceiveMessage(Message * msg, uint16_t timeout);
	bool CheckRadio();
private:
	XBee _xbee;
	XBeeAddress64 _groundAddress = XBeeAddress64(GROUND_SERIAL_H, GROUND_SERIAL_L);
};

#endif
