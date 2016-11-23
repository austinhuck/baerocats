using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Baerocats.XBee
{
    public class GPSMessage : Message
    {
        public const int GPS_MESSAGE_ID = 2;

        private double _altitude;
        private double _latitude;
        private double _longitude;
        private bool _valid;

        public double LatitudeDegrees
        {
            get
            {
                return _latitude;
            }
        }

        public double LongitudeDegress
        {
            get
            {
                return _longitude;
            }
        }

        public bool Valid
        {
            get
            {
                return _valid;
            }
        }

        public double Altitude
        {
            get
            {
                return _altitude;
            }

            set
            {
                _altitude = value;
            }
        }

        public GPSMessage(uint timestamp, bool valid,  double latitude, double longitude, double altitude)
            : base(GPS_MESSAGE_ID, timestamp)
        {
            _valid = valid;
            _latitude = latitude;
            _longitude = longitude;
            _altitude = altitude;
        }

        public GPSMessage(byte[] data)
            : base (data)
        {   
            // ID-TimestampVLTLGAL
            int readOffset = base.GetDataLength();

            _valid = BitConverter.ToBoolean(data, readOffset);
            _latitude = BitConverter.ToSingle(data, readOffset + 1);
            _longitude = BitConverter.ToSingle(data, readOffset + 5);
            _altitude = BitConverter.ToSingle(data, readOffset + 9);
        }

        internal override int GetDataLength()
        {
            return 13 + base.GetDataLength();
        }

        internal override void GetData(byte[] buffer)
        {
            // The base message fills the buffer first.
            base.GetData(buffer);

            int insertOffset = base.GetDataLength();

            Array.Copy(BitConverter.GetBytes(_valid), 0, buffer, insertOffset, 1);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_latitude)), 0, buffer, insertOffset + 1, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_longitude)), 0, buffer, insertOffset + 5, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_altitude)), 0, buffer, insertOffset + 9, 4);        
        }
    }
}
