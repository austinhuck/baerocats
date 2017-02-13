using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

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

        public Message(ushort id,
            byte source,
            ulong timestamp,
            MsgType type,
            )
    }
}
