   M S B A M L   `   `   `  ���� T  PMahApps.Metro, Version=1.3.0.0, Culture=neutral, PublicKeyToken=f4fb5a3c4d1e5b4fV;clr-namespace:MahApps.Metro.Controls;assembly=MahApps.MetroMahApps.Metro.Controls  H DGroundStation, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null?$clr-namespace:GroundStation.ControlsGroundStation.Controls    GroundStation.MainWindow   \ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     PControls;clr-namespace:MahApps.Metro.Controls;assembly=MahApps.Metro     3UC$clr-namespace:GroundStation.Controls     R NOxyPlot.Wpf, Version=1.0.0.0, Culture=neutral, PublicKeyToken=75e952ba404cdbb0 oxyhttp://oxyplot.org/wpf    � Title$  Ground Station��$	��660��$	��600��.��� -   $
��Main��$��5q� � RowDefinitions �� $��* � � ColumnDefinitions �� $
��Auto ��� .+��� ��. $
��Auto=�$��0��$��0��.��� -   $��	DataPanel��$��0��$��0�� �� $
��Auto ��� $
��Auto � �� $
��Auto �.+�"  GroundStation.Controls.Comms  -     Name$ Comms��$��0��$��0��9� -   $
��Data��$
��Data�� 9� 
IsExpanded . $��1��$��0��.���  �� $��* ��� $��* ��� $��* � �� $
��Auto �.+�+  %GroundStation.Controls.DataCollection  -     Name$ Rocket��   	HeadValue$ Rocket��$��0��  -   $ TRIPOD��$ Payload��$��1���� -   $��
TestTRIPOD��$��Test Tripod��$��2���� $��0��$��1��.@��� $��Rocket��.��'  !GroundStation.Controls.RocketPage  -     Name$ 
RocketData���� $��TRIPOD��.��'  !GroundStation.Controls.TRIPODPage  -	     Name$ 
TRIPODData��