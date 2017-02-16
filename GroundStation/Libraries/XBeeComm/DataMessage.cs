using System.IO;

namespace Baerocats.XBee
{
    public class DataMessage : Message
    {
        public float Latitude;
        public float Longitude;
        public float AccelX;
        public float AccelY;
        public float AccelZ;
        public float QuatW;
        public float QuatX;
        public float QuatY;
        public float QuatZ;
        public float OmegaX;
        public float OmegaY;
        public float OmegaZ;
        public float Altitude;
        public float Light;

        public DataMessage(
            ushort id,
            MsgSource source,
            ulong timestamp,
            MsgType type,
            float lat,
            float lng,
            float ax,
            float ay,
            float az,
            float qw,
            float qx,
            float qy,
            float qz,
            float wx,
            float wy,
            float wz,
            float alt,
            float light) :
            base(
                id,
                source,
                timestamp,
                type)
        {
            Latitude = lat;
            Longitude = lng;
            AccelX = ax;
            AccelY = ay;
            AccelZ = az;
            QuatW = qw;
            QuatX = qx;
            QuatY = qy;
            QuatZ = qz;
            OmegaX = wx;
            OmegaY = wy;
            OmegaZ = wz;
            Altitude = alt;
            Light = light;
        }

        public override void GetData(Stream stream)
        {
            base.GetData(stream);

            DataConverter.WriteSingle(stream, Latitude);
            DataConverter.WriteSingle(stream, Longitude);
            DataConverter.WriteSingle(stream, AccelX);
            DataConverter.WriteSingle(stream, AccelY);
            DataConverter.WriteSingle(stream, AccelZ);
            DataConverter.WriteSingle(stream, QuatW);
            DataConverter.WriteSingle(stream, QuatX);
            DataConverter.WriteSingle(stream, QuatY);
            DataConverter.WriteSingle(stream, QuatZ);
            DataConverter.WriteSingle(stream, OmegaX);
            DataConverter.WriteSingle(stream, OmegaY);
            DataConverter.WriteSingle(stream, OmegaZ);
            DataConverter.WriteSingle(stream, Altitude);
            DataConverter.WriteSingle(stream, Light);
        }
    }
}
