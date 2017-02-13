using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Baerocats.XBee
{
    internal static class MessageFactory
    {
        internal static Message Parse(byte[] data)
        {
            Message msg = null;

            MemoryStream stream = new MemoryStream(data);

            ushort id = DataConverter.ReadUShort(stream);
            byte source = DataConverter.ReadByte(stream);
            ulong timestamp = DataConverter.ReadULong(stream);
            Message.MsgType type = (Message.MsgType)DataConverter.ReadByte(stream);

            switch (type)
            {
                case Message.MsgType.Data:
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);
                    float  = DataConverter.ReadFloat(stream);


                    break;
                default:
                    break;
            }

            return null;
        }
    }
}
