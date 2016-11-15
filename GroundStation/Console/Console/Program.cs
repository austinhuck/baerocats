using Baerocats.XBee;
using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Threading;

namespace ConsoleTest
{
    class Program
    {
        private static XBeeComm _xbee;

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

            try
            {
                // Create the XBeeComm objects which handles all XBee communcation.
                _xbee = new XBeeComm(portNames[value]);

                // Register for the message received event.
                _xbee.MessageReceived += XBeeMessageReceived;

                _xbee.Open();

                Console.WriteLine("XBee connected on {0}", portNames[value]);

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
        }

        private static void XBeeMessageReceived(object sender, MessageReceivedEventArgs e)
        {
            // Process message by type here.
            if (e.Message is IMUMessage)
            {
                IMUMessage msg = (IMUMessage)e.Message;
                Console.WriteLine("IMU Message: ({0}) ({1})",
                    msg.Acceleration.ToString(),
                    msg.Euler.ToString());
            }
            else if (e.Message is GPSMessage)
            {
                GPSMessage msg = (GPSMessage)e.Message;
                Console.WriteLine("GPS Message: Valid[{0}] Lat[{1}] Long[{2}]",
                    msg.Valid.ToString(),
                    msg.LatitudeDegrees,
                    msg.LongitudeDegress);
            }
            else
            {
                
            }
        }
    }
}
