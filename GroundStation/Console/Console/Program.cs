using System;
using System.Threading.Tasks;
using XBee;
using XBee.Frames;
using XBee.Frames.AtCommands;

namespace Console
{
    class Program
    {
        static void Main(string[] args)
        {
            System.Console.WriteLine("Initializing on COM9");

            XBeeController controller = new XBeeController("COM9", 9600);

            controller.NodeDiscovered += (s, a) =>
            {
                System.Console.WriteLine("Discovered {0}", a.Name);

                a.Node.SetInputOutputConfigurationAsync(InputOutputChannel.Channel2, InputOutputConfiguration.DigitalIn).Wait();
                a.Node.SetInputOutputConfigurationAsync(InputOutputChannel.Channel3, InputOutputConfiguration.AnalogIn).Wait();

                a.Node.SetChangeDetectionChannelsAsync(DigitalSampleChannels.Input2).Wait();

                a.Node.SetSampleRateAsync(TimeSpan.FromSeconds(5)).Wait();

                a.Node.SampleReceived += (node, sample) => System.Console.WriteLine("Sample recieved: {0}", sample);
            };  

            controller.OpenAsync().Wait();
            controller.DiscoverNetworkAsync().Wait();

        }
    }
}
