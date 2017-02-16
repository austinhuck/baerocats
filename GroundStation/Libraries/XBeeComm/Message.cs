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

        public enum MsgSource
        {
            Ground = 0,
            Rocket = 1,
            Tripod = 2
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
        public MsgSource Source;
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

        public Message(ushort id, MsgSource source, ulong timestamp, MsgType type)
        {
            ID = id;
            Source = source;
            Timestamp = timestamp;
            Type = type;
        }

        public virtual int GetDataLength()
        {
            // ID (2 bytes) + Source (1 Byte) + Timestamp (8 Bytes) + Type (1 Byte)
            return 12;
        }

        public virtual void GetData(Stream stream)
        {
            
        }
    }
}