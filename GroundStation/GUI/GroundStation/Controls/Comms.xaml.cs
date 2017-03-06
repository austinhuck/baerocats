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
using System.Collections.ObjectModel;

namespace GroundStation.Controls
{
    /// <summary>
    /// Interaction logic for Comms.xaml
    /// </summary>
    public partial class Comms : UserControl
    {
        //GUI related stuff
        public ObservableCollection<ComboBoxItem> Ports { get; set; }
        public ComboBoxItem SelectedPort { get; set; }

        //run worker event
        public delegate void EventHandler(object sender, EventArgs args);
        public event EventHandler RunWorker = delegate { };

        public Comms()
        {
            InitializeComponent();
            DataContext = this;
            Ports = new ObservableCollection<ComboBoxItem>();
            Ports.Add(new ComboBoxItem { Content = "--Select Port--" });
            SelectedPort = Ports[0];
        }

        private void PortSelection_DropDownClosed(object sender, EventArgs e)
        {
            RunWorker(this, new EventArgs());
        }

        public void UpdateSignal(ushort? sigStrength)
        {
            Action uSig = () =>
            {
                RocketRadio.Content = Convert.ToString(sigStrength.Value);
            };
            RocketRadio.Dispatcher.BeginInvoke(uSig);
        }
    }
}
