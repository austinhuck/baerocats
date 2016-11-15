using System;

namespace Baerocats.XBee
{
    public class Message
    {
        private short _id;
        private string _timestamp;

        public short Id
        {
            get
            {
                return _id;
            }
        }

        public string Timestamp
        {
            get
            {
                return _timestamp;
            }
        }

        public Message(short id, string timestamp)
        {
            _id = id;
            _timestamp = timestamp;
        }

        public Message(byte[] data)
        {
            _id = GetId(data);

            _timestamp = GetTimestamp(data);
        }

        internal virtual int GetDataLength()
        {
            return 12; // ID (2 bytes) + Timestamp (10 Characters)
        }

        internal virtual void GetData(byte[] buffer)
        {
            Array.Copy(BitConverter.GetBytes(_id), 0, buffer, 0, 2);
            Array.Copy(_timestamp.ToCharArray(), 0, buffer, 2, 10);   
        }

        internal static short GetId(byte[] data)
        {
            return BitConverter.ToInt16(data, 0);
        }

        internal static string GetTimestamp(byte[] data)
        {
            char[] temp = new char[10];
            Array.Copy(data, 2, temp, 0, 10);
            return new string(temp);
        }
    }
}