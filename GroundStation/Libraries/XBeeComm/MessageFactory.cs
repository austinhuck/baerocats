using System.IO;

namespace Baerocats.XBee
{
    public static class MessageFactory
    {
        /// <summary>
        /// Parses message data into a message object.
        /// </summary>
        /// <param name="data">Raw message data</param>
        /// <returns><see cref="Message"/></returns>
        public static Message Parse(byte[] data)
        {
            Message msg = null;

            using (MemoryStream stream = new MemoryStream(data))
            {
                ushort id = DataConverter.ReadUShort(stream);
                Message.MsgSource source = (Message.MsgSource)DataConverter.ReadByte(stream);
                ulong timestamp = DataConverter.ReadULong(stream);
                Message.MsgType type = (Message.MsgType)DataConverter.ReadByte(stream);

                switch (type)
                {
                    case Message.MsgType.Data:
                        float lat = DataConverter.ReadSingle(stream);
                        float lng = DataConverter.ReadSingle(stream);
                        float ax = DataConverter.ReadSingle(stream);
                        float ay = DataConverter.ReadSingle(stream);
                        float az = DataConverter.ReadSingle(stream);
                        float qw = DataConverter.ReadSingle(stream);
                        float qx = DataConverter.ReadSingle(stream);
                        float qy = DataConverter.ReadSingle(stream);
                        float qz = DataConverter.ReadSingle(stream);
                        float wx = DataConverter.ReadSingle(stream);
                        float wy = DataConverter.ReadSingle(stream);
                        float wz = DataConverter.ReadSingle(stream);
                        float alt = DataConverter.ReadSingle(stream);
                        float light = DataConverter.ReadSingle(stream);

                        msg = new DataMessage(
                            id,
                            source,
                            timestamp,
                            type,
                            lat,
                            lng,
                            ax,
                            ay,
                            az,
                            qw,
                            qx,
                            qy,
                            qz,
                            wx,
                            wy,
                            wz,
                            alt,
                            light);

                        break;
                    default:
                        break;
                }
            }

            return msg;
        }
    }
}
