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
using Baerocats.XBee;

namespace GroundStation.Controls
{
    /// <summary>
    /// Interaction logic for DataCollection.xaml
    /// </summary>
    public partial class DataCollection : UserControl
    {

        //Provides the text name for the data collection
        public object HeadValue
        {
            get { return (object)GetValue(HeadValueProp); }
            set { SetValue(HeadValueProp, value); }
        }

        public static readonly DependencyProperty HeadValueProp =
        DependencyProperty.Register("HeadValue", typeof(object),
        typeof(DataCollection), new PropertyMetadata(null));

        public DataCollection()
        {
            InitializeComponent();
            DataC.DataContext = this;
        }

        public void Update(DataMessage msg)
        {
            UpdateIMU(msg);
            UpdateGPS(msg);
        }

        public void UpdateIMU(DataMessage msg)
        {
            string fmt = "{0:0.000}";
            Action uIMU = () =>
            {
                XData.Content =  string.Format(fmt, msg.QuatX);
                YData.Content =  string.Format(fmt, msg.QuatY);
                ZData.Content =  string.Format(fmt, msg.QuatZ);
                WData.Content  = string.Format(fmt, msg.QuatW);
                AXData.Content = string.Format(fmt, msg.AccelX);
                AYData.Content = string.Format(fmt, msg.AccelY);
                AZData.Content = string.Format(fmt, msg.AccelZ);
            };
            XData.Dispatcher.BeginInvoke(uIMU);
        }
        
        public void UpdateGPS(DataMessage msg)
        {
            string fmt = "{0:0.000000}";
            Action uGPS = () =>
            {
                //GPSValid.Content = Convert.ToString(msg.Valid);
                Lat.Content = string.Format(fmt, msg.Latitude);
                Lon.Content = string.Format(fmt, msg.Longitude);
                Alt.Content = string.Format("{0:0.0}", msg.Altitude);
            };
            XData.Dispatcher.BeginInvoke(uGPS);
        }
        

    }
}
