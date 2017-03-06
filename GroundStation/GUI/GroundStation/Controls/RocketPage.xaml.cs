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
    /// Interaction logic for RocketPage.xaml
    /// </summary>
    public partial class RocketPage : UserControl
    {
        public RocketPage()
        {
            InitializeComponent();
            Altitude.PlotTitle = "Rocket Altitude";
        }

        public virtual void UpdatePlots(DataMessage msg)
        {
            Altitude.UpdatePlot(msg.Altitude);
        }

        public void ClearPlot(object sender, RoutedEventArgs e)
        {
            Altitude.ClearPlot();
        }
    }
}
