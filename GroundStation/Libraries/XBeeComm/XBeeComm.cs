

using NETMF.OpenSource.XBee;
using NETMF.OpenSource.XBee.Api;
using System;

namespace Baerocats.XBee
{
    /// <summary>
    /// Class which handles all XBee communcation.
    /// </summary>
    public class XBeeComm
    {
        private const ulong EXT_1_SERIAL= 0x0013A200415AE1C1;
        private const ulong EXT_2_SERIAL = 0x0013A200412692E7;
        private const ulong GROUND_SERIAL = 0x0013A200412692E8;

        private XBeeApi _xbee;
        private XBeeAddress64 _ext1Address = new XBeeAddress64(EXT_1_SERIAL);

        /// <summary>
        /// Create a new XBeeComm object.
        /// </summary>
        /// <remarks>Serial port baud set for 57600.</remarks>
        /// <param name="port">The name of the serial port to connect on.</param>
        public XBeeComm(string port)
        {
            _xbee = new XBeeApi(port, 57600);
            _xbee.DataReceived += XbeeDataReceived;
        }

        /// <summary>
        /// Open the serial port to the XBee.
        /// </summary>
        public void Open()
        {
            _xbee.Open();
        }

        /// <summary>
        /// Close the serial port to the XBee.
        /// </summary>
        public void Close()
        {
            _xbee.Close();
        }

        /// <summary>
        /// Sends a message.
        /// </summary>
        /// <param name="msg">The prepared message.</param>
        public void SendMessage(Message msg)
        {
            int dataLength = msg.GetDataLength();
            byte[] data = new byte[dataLength];
            msg.GetData(data);

            _xbee.Send(data);
        }

        /// <summary>
        /// Ignore
        /// </summary>
        /// <returns></returns>
        public bool CheckRadio()
        {
            // TODO
            return true;
        }

        /// <summary>
        /// Event called upon receiving a message.
        /// </summary>
        public event EventHandler<MessageReceivedEventArgs> MessageReceived;

        private void XbeeDataReceived(XBeeApi receiver, byte[] data, XBeeAddress sender)
        {
            EventHandler<MessageReceivedEventArgs> handler = MessageReceived;

            if (handler != null)
            {
                short msgId = Message.GetId(data);
                Message msg = null;

                switch (msgId)
                {
                    case IMUMessage.IMU_MESSAGE_ID:
                        msg = new IMUMessage(data);
                        break;
                    default:
                        msg = new Message(data);
                        break;
                }
                
                handler(this, new MessageReceivedEventArgs(msg));
            }
        }
    }

    /// <summary>
    /// Event arguments class for Message Received event.
    /// </summary>
    public class MessageReceivedEventArgs : EventArgs
    {
        private Message _msg;

        /// <summary>
        /// Creates a new Message Received event arguments object.
        /// </summary>
        /// <param name="msg"></param>
        public MessageReceivedEventArgs(Message msg)
        {
            _msg = msg;
        }

        /// <summary>
        /// The received message.
        /// </summary>
        public Message Message
        {
            get
            {
                return _msg;
            }
        }
    }
}
