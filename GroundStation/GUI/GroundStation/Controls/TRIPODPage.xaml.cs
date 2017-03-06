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
using System.Windows.Media.Media3D;
using System.Collections;
using Baerocats.XBee;

namespace GroundStation.Controls
{
    /// <summary>
    /// Interaction logic for TRIPODPage.xaml
    /// </summary>
    public partial class TRIPODPage : UserControl
    {
        // transform class object for rotate the 3d model
        public GroundStation.TransformMatrix m_transformMatrix = new GroundStation.TransformMatrix();

        // ***************************** 3d chart ***************************
        private GroundStation.Chart3D m_3dChart;    // data for 3d chart
        public int m_nChartModelIndex = -1;         // model index in the Viewport3d
        public int m_nSurfaceChartGridNo = 100;     // surface chart grid no. in each axis
        public int m_nScatterPlotDataNo = 5000;     // total data number of the scatter plot

        // ***************************** selection rect ***************************
        ViewportRect m_selectRect = new ViewportRect();
        public int m_nRectModelIndex = -1;

        public TRIPODPage()
        {
            InitializeComponent();
            DataContext = this;

            Altitude.PlotTitle = "TRIPOD Altitude";

            // selection rect
            m_selectRect.SetRect(new Point(-0.5, -0.5), new Point(-0.5, -0.5));
            GroundStation.Model3D model3d = new GroundStation.Model3D();
            ArrayList meshs = m_selectRect.GetMeshes();
            m_nRectModelIndex = model3d.UpdateModel(meshs, null, m_nRectModelIndex, this.mainViewport);

            // display the 3d chart data no.
            //gridNo.Text = String.Format("{0:d}", m_nSurfaceChartGridNo);
            //dataNo.Text = String.Format("{0:d}", m_nScatterPlotDataNo);

            // display surface chart
            RotateTRIPOD(new Quaternion(1,0,0,0));
            TransformChart();
        }

        public virtual void ClearPlot(object sender, RoutedEventArgs e)
        {
            Altitude.ClearPlot();
        }

        private void RotateTRIPOD(Quaternion rotation)
        {
            rotation.Normalize();
            Matrix3D rotMTX = Matrix3D.Identity;
            rotMTX.Rotate(rotation);
            Vector3D TRIPODZ = new Vector3D(-1, 0, 0);
            Vector3D rotatedTRIPOD = rotMTX.Transform(TRIPODZ);
            PayloadVector((float)rotatedTRIPOD.X, (float)rotatedTRIPOD.Y, (float)rotatedTRIPOD.Z);
        }

        public void UpdatePlots(DataMessage msg)
        {
            
            Action RefreshPlot = () =>
            {
                //mainViewport.InvalidateVisual();
                RotateTRIPOD(new Quaternion(msg.QuatX, msg.QuatY, msg.QuatZ, msg.QuatW));
            };
            mainViewport.Dispatcher.BeginInvoke(RefreshPlot);
            Altitude.UpdatePlot(msg.Altitude);
        }

        public void DispRotateTRIPOD(Quaternion rotation)
        {
            Action RefreshPlot = () =>
            {
                RotateTRIPOD(rotation);
            };
            mainViewport.Dispatcher.BeginInvoke(RefreshPlot);
        }

        #region 3DPlotting

        public void PayloadVector(float x, float y, float z)
        {
            // 1. set scatter chart data no.
            m_3dChart = new ScatterChart3D();
            m_3dChart.SetDataNo(22);

            // 2. set property of each dot (size, position, shape, color)
            Random randomObject = new Random();
            int nDataRange = 6;

            for (int i = 0; i < 2; i++)
            {
                ScatterPlotItem plotItem = new ScatterPlotItem();

                plotItem.w = 1;
                plotItem.h = 1;

                plotItem.x = i * 5 * x + (float)2.5;
                plotItem.y = i * 5 * y + (float)2.5;
                plotItem.z = i * 5 * z + (float)2.5;

                plotItem.shape = 1;

                plotItem.color = Color.FromRgb((byte)(255 * (1 - i)), 0, (byte)(255 * (i)));
                ((ScatterChart3D)m_3dChart).SetVertex(i, plotItem);
            }

            for (int i = 2; i < 22; i++)
            {
                ScatterPlotItem plotItem = new ScatterPlotItem();

                plotItem.w = (float).25;
                plotItem.h = (float).25;

                plotItem.x = ((float)i / 22) * 5 * x + (float)2.5;
                plotItem.y = ((float)i / 22) * 5 * y + (float)2.5;
                plotItem.z = ((float)i / 22) * 5 * z + (float)2.5;

                plotItem.shape = 1;

                plotItem.color = Color.FromRgb(0, 0, 0);
                ((ScatterChart3D)m_3dChart).SetVertex(i, plotItem);
            }

            // 3. set the axes
            m_3dChart.GetDataRange();
            m_3dChart.SetAxes();

            // 4. get Mesh3D array from the scatter plot
            ArrayList meshs = ((ScatterChart3D)m_3dChart).GetMeshes();

            // 5. display model vertex no and triangle no
            UpdateModelSizeInfo(meshs);

            // 6. display scatter plot in Viewport3D
            GroundStation.Model3D model3d = new GroundStation.Model3D();
            m_nChartModelIndex = model3d.UpdateModel(meshs, null, m_nChartModelIndex, this.mainViewport);

            // 7. set projection matrix
            float viewRange = (float)nDataRange;
            m_transformMatrix.CalculateProjectionMatrix(0, viewRange, 0, viewRange, 0, viewRange, 0.5);
            TransformChart();

        }

        private void UpdateModelSizeInfo(ArrayList meshs)
        {
            int nMeshNo = meshs.Count;
            int nChartVertNo = 0;
            int nChartTriangelNo = 0;
            for (int i = 0; i < nMeshNo; i++)
            {
                nChartVertNo += ((Mesh3D)meshs[i]).GetVertexNo();
                nChartTriangelNo += ((Mesh3D)meshs[i]).GetTriangleNo();
            }
            //labelVertNo.Content = String.Format("Vertex No: {0:d}", nChartVertNo);
            //labelTriNo.Content = String.Format("Triangle No: {0:d}", nChartTriangelNo);
        }

        public void OnViewportMouseDown(object sender, System.Windows.Input.MouseButtonEventArgs args)
        {
            Point pt = args.GetPosition(mainViewport);
            if (args.ChangedButton == MouseButton.Left)         // rotate or drag 3d model
            {
                m_transformMatrix.OnLBtnDown(pt);
            }
            else if (args.ChangedButton == MouseButton.Right)   // select rect
            {
                m_selectRect.OnMouseDown(pt, mainViewport, m_nRectModelIndex);
            }
        }

        public void OnViewportMouseMove(object sender, System.Windows.Input.MouseEventArgs args)
        {
            Point pt = args.GetPosition(mainViewport);

            if (args.LeftButton == MouseButtonState.Pressed)                // rotate or drag 3d model
            {
                m_transformMatrix.OnMouseMove(pt, mainViewport);

                TransformChart();
            }
            else if (args.RightButton == MouseButtonState.Pressed)          // select rect
            {
                m_selectRect.OnMouseMove(pt, mainViewport, m_nRectModelIndex);
            }
            else
            {
                /*
                String s1;
                Point pt2 = m_transformMatrix.VertexToScreenPt(new Point3D(0.5, 0.5, 0.3), mainViewport);
                s1 = string.Format("Screen:({0:d},{1:d}), Predicated: ({2:d}, H:{3:d})", 
                    (int)pt.X, (int)pt.Y, (int)pt2.X, (int)pt2.Y);
                this.statusPane.Text = s1;
                */
            }
        }

        public void OnViewportMouseUp(object sender, System.Windows.Input.MouseButtonEventArgs args)
        {
            Point pt = args.GetPosition(mainViewport);
            if (args.ChangedButton == MouseButton.Left)
            {
                m_transformMatrix.OnLBtnUp();
            }
            else if (args.ChangedButton == MouseButton.Right)
            {
                if (m_nChartModelIndex == -1) return;
                // 1. get the mesh structure related to the selection rect
                MeshGeometry3D meshGeometry = Model3D.GetGeometry(mainViewport, m_nChartModelIndex);
                if (meshGeometry == null) return;

                // 2. set selection in 3d chart
                m_3dChart.Select(m_selectRect, m_transformMatrix, mainViewport);

                // 3. update selection display
                m_3dChart.HighlightSelection(meshGeometry, Color.FromRgb(200, 200, 200));
            }
        }

        private void TransformChart()
        {
            if (m_nChartModelIndex == -1) return;
            ModelVisual3D visual3d = (ModelVisual3D)(this.mainViewport.Children[m_nChartModelIndex]);
            if (visual3d.Content == null) return;
            Transform3DGroup group1 = visual3d.Content.Transform as Transform3DGroup;
            group1.Children.Clear();
            group1.Children.Add(new MatrixTransform3D(m_transformMatrix.m_totalMatrix));
        }

        #endregion
    }
}
