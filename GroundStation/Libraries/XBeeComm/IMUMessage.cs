using System;
using System.Windows.Media.Media3D;

namespace Baerocats.XBee
{

    public class IMUMessage : Message
    {
        internal const short IMU_MESSAGE_ID = 1;

        Vector3D _acceleration;
        Quaternion _orientation;

        public Vector3D Acceleration
        {
            get
            {
                return _acceleration;
            }
        }

        public Quaternion Orientation
        {
            get
            {
                return _orientation;
            }
        }

        public IMUMessage(uint timestamp, Vector3D acceleration, Quaternion ortientation)
            : base(IMU_MESSAGE_ID, timestamp)
        {
            _acceleration = acceleration;
            _orientation = ortientation;
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

            _orientation = new Quaternion(
                BitConverter.ToSingle(data, readOffset + 12),
                BitConverter.ToSingle(data, readOffset + 16),
                BitConverter.ToSingle(data, readOffset + 20),
                BitConverter.ToSingle(data, readOffset + 24)
                );
        }

        internal override int GetDataLength()
        {
            return 28 + base.GetDataLength();
        }

        internal override void GetData(byte[] buffer)
        {
            // The base message fills the buffer first.
            base.GetData(buffer);

            int insertOffset = base.GetDataLength();
            
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_acceleration.X)), 0, buffer, insertOffset, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_acceleration.Y)), 0, buffer, insertOffset + 4, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_acceleration.Z)), 0, buffer, insertOffset + 8, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_orientation.W)), 0, buffer, insertOffset + 12, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_orientation.X)), 0, buffer, insertOffset + 16, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_orientation.Y)), 0, buffer, insertOffset + 20, 4);
            Array.Copy(BitConverter.GetBytes(Convert.ToSingle(_orientation.Z)), 0, buffer, insertOffset + 24, 4);
        }
    }
}
