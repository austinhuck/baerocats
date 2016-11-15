using System;
using System.Windows.Media.Media3D;

namespace Baerocats.XBee
{

    public class IMUMessage : Message
    {
        internal const short IMU_MESSAGE_ID = 1;

        Vector3D _acceleration;
        Vector3D _euler;

        public Vector3D Acceleration
        {
            get
            {
                return _acceleration;
            }
        }

        public Vector3D Euler
        {
            get
            {
                return _euler;
            }
        }

        public IMUMessage(string timestamp, Vector3D acceleration, Vector3D euler)
            : base(IMU_MESSAGE_ID, timestamp)
        {
            _acceleration = acceleration;
            _euler = euler;
        }

        public IMUMessage(byte[] data)
            : base(data)
        {
            int readOffset = base.GetDataLength();

            _acceleration = new Vector3D(
                BitConverter.ToSingle(data, readOffset),
                BitConverter.ToSingle(data, readOffset + 4),
                BitConverter.ToSingle(data, readOffset + 8)
                );

            _euler = new Vector3D(
                BitConverter.ToSingle(data, readOffset + 12),
                BitConverter.ToSingle(data, readOffset + 16),
                BitConverter.ToSingle(data, readOffset + 20)
                );
        }

        internal override int GetDataLength()
        {
            return 24 + base.GetDataLength();
        }

        internal override void GetData(byte[] buffer)
        {
            // The base message fills the buffer first.
            base.GetData(buffer);

            int insertOffset = base.GetDataLength();
            
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_acceleration.X)), 0, buffer, insertOffset, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_acceleration.Y)), 0, buffer, insertOffset + 4, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_acceleration.Z)), 0, buffer, insertOffset + 8, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_euler.X)), 0, buffer, insertOffset + 12, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_euler.Y)), 0, buffer, insertOffset + 16, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_euler.Z)), 0, buffer, insertOffset + 20, 4);
        }
    }
}
