using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using MahApps.Metro.Controls;
using System.ComponentModel;
using System.Threading;
using System.IO;
using System.Collections.ObjectModel;
using Baerocats.XBee;
using OxyPlot;

namespace GroundStation
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : MetroWindow
    {
        //Backend
        private readonly BackgroundWorker Testworker = new BackgroundWorker();
        private readonly BackgroundWorker worker = new BackgroundWorker();
        private readonly BackgroundWorker SigStrength = new BackgroundWorker();
        private static XBeeComm _xbee;
        public static List<String> portNames = XBeeComm.GetPortNames();

        //File naming
        //public static string GPSDataFileName = "GPS_" + System.DateTime.Now.ToFileTime() + ".csv";
        //public static string IMUDataFileName = "IMU_" + System.DateTime.Now.ToFileTime() + ".csv";
        public static string RocketDataFileName = "RKT_" + System.DateTime.Now.ToFileTime() + ".csv";
        public static string TRIPODDataFileName = "TPD_" + System.DateTime.Now.ToFileTime() + ".csv";
        public static string DataPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\Baerocats_Data";

        private string CurrentPort
        {
            get
            {
                return ((ComboBoxItem)Comms.PortSelection.SelectedItem).Content.ToString();
            }
        }

        public MainWindow()
        {
            InitializeComponent();
            //Radio Comms Shit:
            for (int i = 0; i < portNames.Count(); i++)
            {
                Comms.Ports.Add(new ComboBoxItem { Content = portNames[i] });
            }

            //RocketAlt.PlotTitle = "Rocket Altitude";


            //Create working files for GPS and IMU data
            CreateCSVFolder();
            File.Create(DataPath + "\\" + RocketDataFileName);
            File.Create(DataPath + "\\" + TRIPODDataFileName);

            worker.DoWork += worker_DoWork;
            SigStrength.DoWork += UpdateSignalStrength;
            // When the combo box is updated,
            // the 'runWorker' code will execute
            Comms.RunWorker += runWorker;


            DataContext = this;
            
        }

        private void XBeeMessageReceived(object sender, MessageReceivedEventArgs e)
        {
            if (e.Message is DataMessage)
            {
                DataMessage msg = (DataMessage)e.Message;
                // Process message by type here.
                if (msg.Source == Message.MsgSource.Tripod) //TRIPOD
                {
                    TRIPOD.Update(msg);
                    TRIPODData.UpdatePlots(msg);
                    AppendToCSV(msg);

                    //if (e.Message is IMUMessage)
                    //{
                    //    IMUMessage msg = (IMUMessage)e.Message;
                    //    TRIPOD.UpdateIMU(msg);
                    //    TRIPODData.UpdatePlots(msg);
                    //    AppendToCSV(msg);
                    //}
                    //else if (e.Message is GPSMessage)
                    //{
                    //    GPSMessage msg = (GPSMessage)e.Message;
                    //    TRIPOD.UpdateGPS(msg);
                    //    AppendToCSV(msg);
                    //    UpdatePlot(msg);
                    //}
                }
                else if (msg.Source == Message.MsgSource.Rocket) //ROCKET
                {
                    Rocket.Update(msg);
                    RocketData.UpdatePlots(msg);
                    AppendToCSV(msg);
                    //if (true)
                    //{
                    //    IMUMessage msg = (IMUMessage)e.Message;
                    //    Rocket.UpdateIMU(msg);
                    //    AppendToCSV(msg);
                    //}
                    //else if (e.Message is GPSMessage)
                    //{
                    //    GPSMessage msg = (GPSMessage)e.Message;
                    //    Rocket.UpdateGPS(msg);
                    //    AppendToCSV(msg);
                    //    UpdatePlot(msg);
                    //}
                }
            }
        }

        private void runWorker(object sender, EventArgs e)
        {
            if (portNames.Contains(CurrentPort))
            {
                worker.RunWorkerAsync(CurrentPort);
            }
            Comms.PortSelection.IsEnabled = false;
        }

        private void worker_DoWork(object sender, DoWorkEventArgs e)
        {
            //File.AppendAllText(DataPath + "\\" + GPSDataFileName, "TimeStamp,Valid,Lattitude,Longitude,Altitude\n");
            File.AppendAllText(DataPath + "\\" + RocketDataFileName, "TimeStamp,ORX,ORY,ORZ,ORW,AX,AY,AZ,Lattitude,Longitude,Altitude,Light,ID\n");
            File.AppendAllText(DataPath + "\\" + TRIPODDataFileName, "TimeStamp,ORX,ORY,ORZ,ORW,AX,AY,AZ,Lattitude,Longitude,Altitude,Light,ID\n");


            // run all background tasks here
            //while(!e.Cancel)
            //{
            //    Thread.Sleep(1000);
            //    Rocket.UpdateIMU((float)12.31, (float)1.11, (float)2.22);
            //}
            string PortSelection = (string)e.Argument;
            try
            {
                // Create the XBeeComm objects which handles all XBee communcation.
                _xbee = new XBeeComm(PortSelection);
                
                // Register for the message received event.
                _xbee.MessageReceived += XBeeMessageReceived;

                _xbee.Open();

                SigStrength.RunWorkerAsync();

                //Console.WriteLine("XBee connected on {0}", PortSelection);

                // Keep the console open forever
                new ManualResetEvent(false).WaitOne();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
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

        private void UpdateSignalStrength(object sender, DoWorkEventArgs e)
        {
            while (!e.Cancel)
            {
                GetSignalStrength();
                Thread.Sleep(1000);
            }
        }

        private async void GetSignalStrength()
        {
            ushort? signalStrength = await _xbee.GetSignalStrength();
            Comms.UpdateSignal(signalStrength);
        }

        public void CreateCSVFolder()
        {
            if (!(System.IO.Directory.Exists(DataPath)))
            {
                System.IO.Directory.CreateDirectory(DataPath);
            }
        }

        //public void UpdatePlot(GPSMessage msg)
        //{
        //    RocketData.Altitude.UpdatePlot(msg.Altitude);
        //}

        //public void AppendToCSV(GPSMessage msg)
        //{
        //    string fmt = ":0.000}";
        //    StringBuilder CSVLine = new StringBuilder();
        //    CSVLine.AppendLine(string.Format("{0}," 
        //                                   + "{1}," 
        //                                   + "{2" + fmt + "," 
        //                                   + "{3" + fmt + "," 
        //                                   + "{4" + fmt, 
        //                                   msg.Timestamp, 
        //                                   Convert.ToString(msg.Valid), 
        //                                   msg.LatitudeDegrees, 
        //                                   msg.LongitudeDegress, 
        //                                   msg.Altitude));
        //    File.AppendAllText(DataPath + "\\" + GPSDataFileName, CSVLine.ToString());
        //}

        //public void AppendToCSV(IMUMessage msg)
        //{
        //    string fmt = ":0.000}";
        //    StringBuilder CSVLine = new StringBuilder();
        //    CSVLine.AppendLine(string.Format("{0},"
        //                                   + "{1" + fmt + "," + "{2" + fmt + "," + "{3" + fmt + "," + "{4" + fmt + ","
        //                                   + "{5" + fmt + "," + "{6" + fmt + "," + "{7" + fmt, msg.Timestamp, msg.Orientation.X, msg.Orientation.Y, msg.Orientation.Z, msg.Orientation.W, msg.Acceleration.X, msg.Acceleration.Y, msg.Acceleration.Z));
        //    File.AppendAllText(DataPath + "\\" + IMUDataFileName, CSVLine.ToString());
        //}

        public void AppendToCSV(DataMessage msg)
        {
            string fmt = ":0.0000000}";
            StringBuilder CSVLine = new StringBuilder();
            CSVLine.AppendLine(string.Format("{0},"
                                           + "{1" + fmt + "," 
                                           + "{2" + fmt + "," 
                                           + "{3" + fmt + "," 
                                           + "{4" + fmt + ","
                                           + "{5" + fmt + "," 
                                           + "{6" + fmt + "," 
                                           + "{7" + fmt + ","
                                           + "{8" + fmt + ","
                                           + "{9" + fmt + ","
                                           + "{10" + fmt + ","
                                           + "{11" + fmt + ","
                                           + "{12},", 
                                           msg.Timestamp, 
                                           msg.QuatX, 
                                           msg.QuatY, 
                                           msg.QuatZ, 
                                           msg.QuatW, 
                                           msg.AccelX, 
                                           msg.AccelY, 
                                           msg.AccelZ,
                                           msg.Latitude,
                                           msg.Longitude,
                                           msg.Altitude,
                                           msg.Light,
                                           msg.ID));

            if (msg.Source == Message.MsgSource.Tripod)
            {
                File.AppendAllText(DataPath + "\\" + TRIPODDataFileName, CSVLine.ToString());
            }
            else if (msg.Source == Message.MsgSource.Rocket)
            {
                File.AppendAllText(DataPath + "\\" + RocketDataFileName, CSVLine.ToString());
            }
        }

        public void TestVector_Click(object sender, EventArgs e)
        {
            Testworker.DoWork+=TestVector;
            Testworker.RunWorkerAsync();
        }

        public void TestVector(object sender, DoWorkEventArgs e)
        {
            CSVRead Data = new CSVRead(@"C:\Users\Justas\Box Sync\Justas\SeniorDesign\CSVReader\CSVReader\CSVReader\CSVFiles\TripodTrimmed.csv");
            List<List<string>> quatData = new List<List<string>>();
            for (int i = 4; i < 8; i++) quatData.Add(Data.CSV[i]);

            for (int idx = 0; idx < quatData[0].Count(); idx++)
            {
                List<double> quatParams = new List<double>();
                for (int tIDX = 0; tIDX < quatData.Count(); tIDX++) quatParams.Add(Convert.ToDouble(quatData[tIDX][idx]));
                TRIPODData.DispRotateTRIPOD(new System.Windows.Media.Media3D.Quaternion(quatParams[1], quatParams[2], quatParams[3], quatParams[0]));
                Thread.Sleep(50);
            }
        }
    }
}
