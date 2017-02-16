using System;
using System.IO;
using System.Text;

namespace Baerocats.XBee
{
    public static class DataConverter
    {
        public static byte ReadByte(Stream stream)
        {
            byte[] rawBytes = new byte[1];
            stream.Read(rawBytes, 0, 1);
            return rawBytes[0];
        }

        public static ushort ReadUShort(Stream stream)
        {
            byte[] rawBytes = new byte[2];
            stream.Read(rawBytes, 0, 2);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            return BitConverter.ToUInt16(rawBytes, 0);
        }

        public static uint ReadUInt(Stream stream)
        {
            byte[] rawBytes = new byte[4];
            stream.Read(rawBytes, 0, 4);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            return BitConverter.ToUInt32(rawBytes, 0);
        }

        public static ulong ReadULong(Stream stream)
        {
            byte[] rawBytes = new byte[8];
            stream.Read(rawBytes, 0, 8);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            return BitConverter.ToUInt64(rawBytes, 0);
        }

        public static float ReadSingle(Stream stream)
        {
            byte[] rawBytes = new byte[4];
            stream.Read(rawBytes, 0, 4);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            return BitConverter.ToSingle(rawBytes, 0);
        }

        public static double ReadDouble(Stream stream)
        {
            byte[] rawBytes = new byte[8];
            stream.Read(rawBytes, 0, 8);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            return BitConverter.ToDouble(rawBytes, 0);
        }

        public static char ReadChar(Stream stream)
        {
            byte[] rawBytes = new byte[1];
            stream.Read(rawBytes, 0, 1);
            return Encoding.ASCII.GetChars(rawBytes)[0];
        }

        public static string ReadString(Stream stream, int length)
        {
            byte[] rawBytes = new byte[length];
            stream.Read(rawBytes, 0, length);
            return Encoding.ASCII.GetString(rawBytes);
        }

        public static void WriteByte(Stream stream, byte value)
        {
            stream.Write(new byte[] { value }, 0, 1);
        }

        public static void WriteUShort(Stream stream, ushort value)
        {
            byte[] rawBytes = BitConverter.GetBytes(value);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            stream.Write(rawBytes, 0, 2);
        }

        public static void WriteUInt(Stream stream, uint value)
        {
            byte[] rawBytes = BitConverter.GetBytes(value);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            stream.Write(rawBytes, 0, 4);
        }

        public static void WriteULong(Stream stream, ulong value)
        {
            byte[] rawBytes = BitConverter.GetBytes(value);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            stream.Write(rawBytes, 0, 8);
        }

        public static void WriteSingle(Stream stream, float value)
        {
            byte[] rawBytes = BitConverter.GetBytes(value);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            stream.Write(rawBytes, 0, 4);
        }

        public static void WriteDouble(Stream stream, double value)
        {
            byte[] rawBytes = BitConverter.GetBytes(value);

            if (!BitConverter.IsLittleEndian)
            {
                Array.Reverse(rawBytes);
            }

            stream.Write(rawBytes, 0, 8);
        }

        public static void WriteChar(Stream stream, char value)
        {
            byte[] rawBytes = Encoding.ASCII.GetBytes(new char[] { value }, 0, 1);
            stream.Write(rawBytes, 0, 1);
        }

        public static void WriteString(Stream stream, string value)
        {
            byte[] rawBytes = Encoding.ASCII.GetBytes(value);
            stream.Write(rawBytes, 0, value.Length);
        }
    }
}
