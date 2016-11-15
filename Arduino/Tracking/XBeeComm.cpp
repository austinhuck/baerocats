#include "XBeeComm.h"

XBeeComm::XBeeComm(Stream &stream)
{
	_xbee = XBee();
	_xbee.setSerial(stream);
}

XBeeComm::~XBeeComm()
{
}

bool XBeeComm::CheckRadio()
{
	// Check to ensure the correct radio is attached.
	// Looks at the lower byte of the serial number.

	//Serial.println("Checking XBee radio for matching serial number.");

	uint8_t slCmd[] = { 'S','L' };
	AtCommandRequest atRequest = AtCommandRequest(slCmd);
	bool valid = false;

	/*
	_xbee.send(atRequest);

	if (_xbee.readPacket(1000))
	{
		// should be an AT command response
		if (_xbee.getResponse().getApiId() == AT_COMMAND_RESPONSE)
		{
			AtCommandResponse atResponse = AtCommandResponse();
			_xbee.getResponse().getAtCommandResponse(atResponse);

			if (atResponse.isOk())
			{
				if (atResponse.getCommand()[0] == 'S'
					&& atRequest.getCommand()[1] == 'L')
				{
					if (atResponse.getValueLength() == 4)
					{
						uint32_t * serialReceived = new uint32_t();

						int i, j;
						for (i = 0, j = 3; i < 4; i++, j--)
						{
							memcpy(serialReceived + i, atResponse.getValue() + j, 1);
						}
						valid = *serialReceived == EXT_1_SERIAL_L;
						
						delete serialReceived;
					}
				}
			}
		}
	}
	*/
	
	return true; // valid;

	/*
						if (serialReceived == EXT_1_SERIAL_L)
						{
							Serial.print("Serial numbers match [");
							Serial.print(serialReceived, HEX);
							Serial.println("]!");
						}
						else
						{
							Serial.print("Serial number mismatch! Expected [");
							Serial.print(MyAddress.getLsb(), HEX);
							Serial.print("] but received [");
							Serial.print(serialReceived, HEX);
							Serial.println("].");
						}
					}
					else
					{
						Serial.println("Error: Reponse value was not the expected 4 bytes in length.");
					}
				}
				else
				{
					Serial.println("Error: AT command response was not in response of the \'SL\' command.");
				}
			}
			else
			{
				Serial.print("Error: Command return error code ");
				Serial.print(atResponse.getStatus(), HEX);
				Serial.println(".");
			}
		}
		else
		{
			Serial.println("Error: Response was not an AT command response.");
		}
	}
	else
	{
		Serial.println("Response timeout.");
	}
	*/
}

void XBeeComm::SendMessage(const Message * msg)
{
	int dataLength = msg->getDataLength();
	byte * data = new byte[dataLength];
	msg->getData(data);

	ZBTxRequest tx = ZBTxRequest(_groundAddress, data, dataLength);
	_xbee.send(tx);
	
	delete data;
}

void XBeeComm::ReceiveMessage(Message * msg, uint16_t timeout = 100)
{
	ZBTxStatusResponse txStatus;
	ZBRxResponse rx;

	if (_xbee.readPacket(timeout))
	{
		// got a response!

		switch (_xbee.getResponse().getApiId())
		{
		case ZB_TX_STATUS_RESPONSE:
			// Transmit status response
			_xbee.getResponse().getZBTxStatusResponse(txStatus);

			// get the delivery status
			if (txStatus.getDeliveryStatus() == SUCCESS)
			{
				
			}
			else
			{
				
			}
			break;

		case ZB_RX_RESPONSE:
			// Receive response
			_xbee.getResponse().getZBRxResponse(rx);

			break;

		default:
			// Something else
			break;
		}
	}
	else if (_xbee.getResponse().isError())
	{

	}
	else
	{

	}
}
