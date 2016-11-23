

using NETMF.OpenSource.XBee;
using NETMF.OpenSource.XBee.Api;
using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Threading.Tasks;
using System.Timers;
using System.Windows.Media.Media3D;

namespace Baerocats.XBee
{
    /// <summary>
    /// Class which handles all XBee communcation.
    /// </summary>
    public class XBeeComm
    {
        /// <summary>
        /// Gets a list of available serial ports.
        /// </summary>
        /// <returns></returns>
        public static List<String> GetPortNames()
        {
            List<String> portNames = new List<String>(SerialPort.GetPortNames());
            portNames.Insert(0, "SIM");
            return portNames;
        }

        private const ulong EXT_1_SERIAL= 0x0013A200415AE1C1;
        private const ulong EXT_2_SERIAL = 0x0013A200412692E7;
        private const ulong GROUND_SERIAL = 0x0013A200412692E8;
        private Random _rand = new Random(DateTime.Now.Millisecond);
        private bool _simSwap = true;
        private XBeeApi _xbee = null;
        private Timer _xbeeSim = null;
        private XBeeAddress64 _ext1Address = new XBeeAddress64(EXT_1_SERIAL);

        /// <summary>
        /// Create a new XBeeComm object.
        /// </summary>
        /// <remarks>Serial port baud set for 57600.</remarks>
        /// <param name="port">The name of the serial port to connect on.</param>
        public XBeeComm(string port)
        {
            if (port == "SIM")
            {
                _xbeeSim = new Timer(1000);
                _xbeeSim.Elapsed += XBeeSimElapsed;
            }
            else
            {
                _xbee = new XBeeApi(port, 57600);
                _xbee.DataReceived += XbeeDataReceived;
            }
        }

        /// <summary>
        /// Open the serial port to the XBee.
        /// </summary>
        public void Open()
        {
            if (_xbee == null)
            {
                _xbeeSim.Start();
            }
            else
            {
                _xbee.Open();
            }
        }

        /// <summary>
        /// Close the serial port to the XBee.
        /// </summary>
        public void Close()
        {
            if (_xbee == null)
            {
                _xbeeSim.Stop();
            }
            else
            {
                _xbee.Close();
            }
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

            if (_xbee != null)
            {
                _xbee.Send(data);
            }
        }

        /// <summary>
        /// Returns the signal strength of the last received message in units of -dB.
        /// </summary>
        public async Task<ushort?> GetSignalStrength()
        {
            if (_xbee != null)
            {
                Task<ushort?> atTask = new Task<ushort?>(() =>
                {
                    AtCommand cmd = _xbee.CreateRequest((ushort)NETMF.OpenSource.XBee.Api.Zigbee.AtCmd.ReceivedSignalStrength);
                    AsyncSendResult result = _xbee.BeginSend(cmd, new AtResponseFilter(cmd), 2000);
                    XBeeResponse[] responses = _xbee.EndReceive(result);

                    if (responses.Length == 0)
                    {
                        return null;
                    }
                    else
                    {
                        return (ushort)((AtResponse)responses[0]).Value[0];
                    }
                });

                atTask.Start(); 

                return await atTask;
            }
            else
            {
                return 0;
            }
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
                    case GPSMessage.GPS_MESSAGE_ID:
                        msg = new GPSMessage(data);
                        break;
                    default:
                        msg = new Message(data);
                        break;
                }
                
                handler(this, new MessageReceivedEventArgs(msg));
            }
        }

        private void XBeeSimElapsed(object sender, ElapsedEventArgs e)
        {
            EventHandler<MessageReceivedEventArgs> handler = MessageReceived;

            if (handler != null)
            {
                Message msg = null;
                if (_simSwap)
                {
                    msg = new IMUMessage(0,
                        new Vector3D(
                            _rand.NextDouble() * 16 * (_rand.Next(1) == 1 ? -1 : 1),
                            _rand.NextDouble() * 16 * (_rand.Next(1) == 1 ? -1 : 1),
                            _rand.NextDouble() * 16 * (_rand.Next(1) == 1 ? -1 : 1)),
                        new Quaternion(
                            _rand.NextDouble(),
                            _rand.NextDouble(),
                            _rand.NextDouble(),
                            _rand.NextDouble()));
                }
                else
                {
                    msg = new GPSMessage(0, true, 39.1309584, -84.5200646, 800.12);
                }

                handler(this, new MessageReceivedEventArgs(msg));

                _simSwap = !_simSwap;
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
