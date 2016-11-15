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

        private double _latDeg;
        private double _longDeg;
        private bool _valid;

        public double LatitudeDegrees
        {
            get
            {
                return _latDeg;
            }
        }

        public double LongitudeDegress
        {
            get
            {
                return _longDeg;
            }
        }

        public bool Valid
        {
            get
            {
                return _valid;
            }
        }

        public GPSMessage(string timestamp, bool valid,  double latDeg, double longDeg)
            : base(GPS_MESSAGE_ID, timestamp)
        {
            _valid = valid;
            _latDeg = latDeg;
            _longDeg = longDeg;
        }

        public GPSMessage(byte[] data)
            : base (data)
        {   
            // ID-Timestamp,V,--Latitude-,--Longitude-
            // 00194509.000,A,4042.6142,N,07400.4168,W
            int readOffset = base.GetDataLength();

            char valid = ASCIIEncoding.ASCII.GetChars(data, readOffset + 1, 1)[0];
            string latitude = ASCIIEncoding.ASCII.GetString(data, readOffset + 3, 9);
            char ns = ASCIIEncoding.ASCII.GetChars(data, readOffset + 13, 1)[0];
            string longitude = ASCIIEncoding.ASCII.GetString(data, readOffset + 15, 10);
            char ew = ASCIIEncoding.ASCII.GetChars(data, readOffset + 26, 1)[0];

            _valid = (valid == 'A');

            _latDeg = ((ns == 'N') ? 1 : -1) * 
                (Double.Parse(latitude.Substring(0, 2)) + Double.Parse(latitude.Substring(2)) / 60);

            _longDeg = ((ew == 'E') ? 1 : -1) * 
                (Double.Parse(longitude.Substring(0, 3)) + Double.Parse(longitude.Substring(3)) / 60);
        }

        internal override int GetDataLength()
        {
            return 27 + base.GetDataLength();
        }

        internal override void GetData(byte[] buffer)
        {
            // The base message fills the buffer first.
            base.GetData(buffer);

            int insertOffset = base.GetDataLength();

            StringBuilder sb = new StringBuilder();
            sb.Append(',');
            sb.Append(_valid ? 'A' : 'V');
            sb.Append(',');

            double lat = Math.Abs(_latDeg);
            int latDegrees = (int)Math.Floor(lat);
            string latitude = latDegrees.ToString("D2") + ((lat - latDegrees) * 60).ToString("F4").PadLeft(7, '0');

            sb.Append(latitude);
            sb.Append(',');
            sb.Append(_latDeg < 0 ? 'S' : 'N');
            sb.Append(',');

            double lng = Math.Abs(_longDeg);
            int lngDegrees = (int)Math.Floor(lng);
            string longitude = lngDegrees.ToString("D3") + ((lng - lngDegrees) * 60).ToString("F4").PadLeft(7, '0');

            sb.Append(longitude);
            sb.Append(',');
            sb.Append(_longDeg < 0 ? 'E' : 'W');

            Array.Copy(ASCIIEncoding.ASCII.GetBytes(sb.ToString()), 0, buffer, insertOffset, 27);
        }
    }
}
