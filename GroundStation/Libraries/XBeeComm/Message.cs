using System;

namespace Baerocats.XBee
{
    public class Message
    {
        private short _id;
        private uint _timestamp;

        public short Id
        {
            get
            {
                return _id;
            }
        }

        public uint Timestamp
        {
            get
            {
                return _timestamp;
            }
        }

        public Message(short id, uint timestamp)
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
            return 12; // ID (2 bytes) + Timestamp (4 Bytes)
        }

        internal virtual void GetData(byte[] buffer)
        {
            Array.Copy(BitConverter.GetBytes(_id), 0, buffer, 0, 2);
            Array.Copy(BitConverter.GetBytes(_timestamp), 0, buffer, 2, 4);   
        }

        internal static short GetId(byte[] data)
        {
            return BitConverter.ToInt16(data, 0);
        }

        internal static uint GetTimestamp(byte[] data)
        {
            return BitConverter.ToUInt32(data, 2);
        }
    }
}