using System;
using System.IO;

namespace Baerocats.XBee
{
    public abstract class Message
    {
        public enum MsgType
        {
            Unknown = 0,
            Data = 1,
            Log = 2,
            Cmd = 3,
            CmdResponse = 4
        }

        private static ushort _ID = 0;
        private static object _IDLock = new object();
        
        private static ushort GetNextID()
        {
            ushort ID;

            lock (Message._IDLock)
            {
                ID = Message._ID;

                if (Message._ID >= 65535)
                {
                    Message._ID = 0;
                }
                else
                {
                    Message._ID++;
                }
            }

            return ID;
        }

        public ushort ID;
        public byte Source;
        public ulong Timestamp;
        public MsgType Type;

        public Message()
        {
            ID = GetNextID();
            Source = 0;
            Timestamp = Convert.ToUInt64(DateTime.UtcNow.Subtract(
                new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc))
                .TotalMilliseconds * 1000);
            Type = MsgType.Unknown;
        }

        public Message(ushort id, byte source, ulong timestamp, MsgType type)
        {
            ID = id;
            Source = source;
            Timestamp = timestamp;
            Type = type;
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