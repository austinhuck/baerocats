#ifndef DataMessage_h
#define DataMessage_h

#include "Message.h"

class DataMessage :
	public Message
{
public:
	DataMessage(
    double lat,
    double lng,
    double ax,
    double ay,
    double az,
    double qw,
    double qx,
    double qy,
    double qz,
    double wx,
    double wy,
    double wz,
    double alt,
    double light);
  int getDataLength() const override;
	void getData(byte * buffer) const override;
private:
  double Latitude;
  double Longitude;
  double AccelX;
  double AccelY;
  double AccelZ;
  double QuatW;
  double QuatX;
  double QuatY;
  double QuatZ;
  double OmegaX;
  double OmegaY;
  double OmegaZ;
  double Altitude;
  double Light;
};
#endif

