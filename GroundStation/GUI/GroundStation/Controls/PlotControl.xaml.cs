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
using OxyPlot;

namespace GroundStation.Controls
{
    /// <summary>
    /// Interaction logic for PlotControl.xaml
    /// </summary>
    public partial class PlotControl : UserControl
    {

        //Plotting
        public string PlotTitle { get; set; }
        public IList<DataPoint> Points { get; private set; }
        private double TempTime;

        public PlotControl()
        {
            InitializeComponent();

            //Plotting TEMP
            TempTime = 1;
            //PlotTitle = "Altitude";
            //Points = new List<DataPoint>
            //                  {
            //                      new DataPoint(0, 4),
            //                      new DataPoint(10, 13),
            //                      new DataPoint(20, 15),
            //                      new DataPoint(30, 16),
            //                      new DataPoint(40, 12),
            //                      new DataPoint(50, 12)
            //                  };
            //Refresh();
            Points = new List<DataPoint>();

            DataContext = this;
        }

        public void UpdatePlot(double Data)
        {
            Points.Add(new DataPoint(TempTime, Data));
            TempTime++;
            Refresh();
        }

        public void Refresh()
        {
            Action RefreshPlot = () =>
            {
                Figure.InvalidatePlot(true);
            };
            Figure.Dispatcher.BeginInvoke(RefreshPlot);
            //Figure.Dispatcher.InvokeAsync(RefreshPlot);
        }

        public void ClearPlot()
        {
            Points.Clear();
            Action RefreshPlot = () =>
            {
                Figure.InvalidatePlot(true);
            };
            Figure.Dispatcher.BeginInvoke(RefreshPlot);
            //Figure.Dispatcher.InvokeAsync(RefreshPlot);
        }
    }
}
