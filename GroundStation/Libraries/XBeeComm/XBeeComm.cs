

using NETMF.OpenSource.XBee;
using NETMF.OpenSource.XBee.Api;
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Ports;
using System.Threading.Tasks;
using System.Timers;

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
        private byte[] GROUND_SERIAL_LOW = new byte[] { 0x41, 0x26, 0x92, 0xE8 };
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
                _xbee = new XBeeApi(port, 115200);
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
            if (_xbee != null)
            {
                MemoryStream stream = new MemoryStream();
                msg.GetData(stream);
                _xbee.Send(stream.ToArray());
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
        /// Checks communication to the radio.
        /// </summary>
        /// <returns>True if communication is good.</returns>
        public bool CheckRadio()
        {
            if (_xbee != null)
            {
                Task<bool> atTask = new Task<bool>(() =>
                {
                    AtCommand cmd = _xbee.CreateRequest((ushort)NETMF.OpenSource.XBee.Api.Zigbee.AtCmd.SerialNumberLow);
                    AsyncSendResult result = _xbee.BeginSend(cmd, new AtResponseFilter(cmd), 2000);
                    XBeeResponse[] responses = _xbee.EndReceive(result);

                    bool valid = true;

                    if (responses.Length == 0)
                    {
                        valid = false;
                    }
                    else
                    {
                        byte[] serialLow = ((AtResponse)responses[0]).Value;
                        

                        if (serialLow.GetLength(0) == 4)
                        {
                            for (int i = 0; i < 4; i++)
                            {
                                valid &= GROUND_SERIAL_LOW[i] == serialLow[i];
                            }
                        }
                        else
                        {
                            valid = false;
                        }
                    }

                    return valid;
                });

                atTask.Start();
                atTask.Wait();
                return atTask.Result;
            }
            else
            {
                return false;
            }
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
                Message msg = MessageFactory.Parse(data);
                handler(this, new MessageReceivedEventArgs(msg));
            }
        }

        private void XBeeSimElapsed(object sender, ElapsedEventArgs e)
        {
            EventHandler<MessageReceivedEventArgs> handler = MessageReceived;

            if (handler != null)
            {
                Message msg = new DataMessage(
                    0, Message.MsgSource.Rocket, 123456789, Message.MsgType.Data,
                    39.1309584F, -84.5200646F,
                    (float)_rand.NextDouble() * 16 * (_rand.Next(1) == 1 ? -1 : 1),
                    (float)_rand.NextDouble() * 16 * (_rand.Next(1) == 1 ? -1 : 1),
                    (float)_rand.NextDouble() * 16 * (_rand.Next(1) == 1 ? -1 : 1),
                    (float)_rand.NextDouble(),
                    (float)_rand.NextDouble(),
                    (float)_rand.NextDouble(),
                    (float)_rand.NextDouble(),
                    (float)_rand.NextDouble() * 6 * (_rand.Next(1) == 1 ? -1 : 1),
                    (float)_rand.NextDouble() * 6 * (_rand.Next(1) == 1 ? -1 : 1),
                    (float)_rand.NextDouble() * 6 * (_rand.Next(1) == 1 ? -1 : 1),
                    (float)_rand.NextDouble() * 6000,
                    (float)_rand.NextDouble() * 1000);

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
