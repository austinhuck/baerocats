using Baerocats.XBee;
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Ports;
using System.Threading;
using System.Threading.Tasks;

namespace ConsoleTest
{
    class Program
    {
        private static XBeeComm _xbee;
        private static Timer _signalTimer;

        [STAThread]
        static void Main(string[] args)
        {
            // Find available ports
            List<String> portNames = XBeeComm.GetPortNames();

            Console.WriteLine("Select an available port by index:");
            Console.WriteLine();

            for (int i = 0; i < portNames.Count; i++)
            {
                Console.WriteLine("{0}: {1}", i, portNames[i]);
            }

            Console.WriteLine();
            Console.Write("Index -> ");
            string line = Console.ReadLine();
            Console.WriteLine();
            int value;

            while (!int.TryParse(line, out value) || value < 0 || value > portNames.Count)
            {
                Console.WriteLine("Invalid Input");
                Console.Write("Index -> ");
                line = Console.ReadLine();
                Console.WriteLine();
            }

            Console.WriteLine("Initializing on {0}", portNames[value]);

            //FileStream filestream = new FileStream("out.txt", FileMode.Create);
            //var streamwriter = new StreamWriter(filestream);
            //streamwriter.AutoFlush = true;
            //Console.SetOut(streamwriter);
            //Console.SetError(streamwriter);

            try
            {
                // Create the XBeeComm objects which handles all XBee communcation.
                _xbee = new XBeeComm(portNames[value]);

                // Register for the message received event.
                _xbee.MessageReceived += XBeeMessageReceived;

                _xbee.Open();

                string msg = null;
                if (_xbee.CheckRadio())
                {
                    msg = "Correct";
                }
                else
                {
                    msg = "Incorrect";
                }

                Console.WriteLine("{0} XBee connected on {1}", msg, portNames[value]);

                _signalTimer = new Timer(new TimerCallback((obj) =>
                {
                    GetSignalStrength();
                }), null, 2000, 2000);

                // Keep the console open forever
                new ManualResetEvent(false).WaitOne();
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
            finally
            {
                // Finally, ensure the serial connection has been closed.
                if (_xbee != null)
                {
                    _xbee.Close();
                }
            }

            Console.Read();
        }

        private static async void GetSignalStrength()
        {
            ushort? signalStrength = await _xbee.GetSignalStrength();
            Console.WriteLine("Signal Strength: -{0}dB", signalStrength);
        }

        private static void XBeeMessageReceived(object sender, MessageReceivedEventArgs e)
        {
            // Process message by type here.
            if (e.Message is DataMessage)
            {
                DataMessage msg = (DataMessage)e.Message;
                Console.WriteLine("Data Message : ({14}, {15}, {16}, {17}) : ({0}, {1}) : ({2}, {3}, {4}) : ({5}, {6}, {7}, {8}) : ({9}, {10}, {11}) : ({12}, {13})",
                    msg.Latitude,
                    msg.Longitude,
                    msg.AccelX,
                    msg.AccelY,
                    msg.AccelZ,
                    msg.QuatW,
                    msg.QuatX,
                    msg.QuatY,
                    msg.QuatZ,
                    msg.OmegaX,
                    msg.OmegaY,
                    msg.OmegaZ,
                    msg.Altitude,
                    msg.Light,
                    msg.ID,
                    msg.Source,
                    msg.Timestamp,
                    msg.Type);
            }
            else
            {
                
            }
        }
    }
}
