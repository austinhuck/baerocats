   M S B A M L   `   `   `  ����T  PMahApps.Metro, Version=1.3.0.0, Culture=neutral, PublicKeyToken=f4fb5a3c4d1e5b4fV;clr-namespace:MahApps.Metro.Controls;assembly=MahApps.MetroMahApps.Metro.Controls  5      H DGroundStation, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null?$clr-namespace:GroundStation.ControlsGroundStation.Controls 5         GroundStation.MainWindow   5      \ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    5      R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     5      PControls;clr-namespace:MahApps.Metro.Controls;assembly=MahApps.Metro     5      3UC$clr-namespace:GroundStation.Controls     5      R NOxyPlot.Wpf, Version=1.0.0.0, Culture=neutral, PublicKeyToken=75e952ba404cdbb0 oxyhttp://oxyplot.org/wpf  5        � Title$  Ground Station��5      $	��660��6$   $	��600��61   .��5      � -   5        $
��Main��5      $��5q�6    � RowDefinitions 5	   
   �� 5
      $��* �6    � ColumnDefinitions 5   
   �� 5      $
��Auto �6   �� 5      .+�5   
   �� ��. $
��Auto=�6<   $��0��6m   $��0��6z   .��5      � -   5        $��	DataPanel��5      $��0��6$   $��0��61    5      �� 5      $
��Auto �6$   �� 5      $
��Auto �6$    5      �� 5      $
��Auto �6'   .+�5      "  GroundStation.Controls.Comms  -   5          Name$ Comms��5      $��0��6*   $��0��67   6I   9� 5      -   5        $
��Data��5      $
��Data��6'    9� 
IsExpanded . $��1��6G   $��0��6T   .��5      �  5      �� 5      $��* �6,   �� 5      $��* �6,   �� 5      $��* �6,    5!      �� 5"      $
��Auto �6/   .+�5$      +  %GroundStation.Controls.DataCollection  -   5          Name$ Rocket��5$   ,      	HeadValue$ Rocket��6<   $��0��6P   6_     5%      -   5        $ TRIPOD��5%   ,   $ Payload��6<   $��1��6P   6_   �� 5&      -   5        $��
TestTRIPOD��5&   !   $��Test Tripod��63   $��2��6I   6V   5'      5(      5)      5*      �� 5+   
   $��0��6   $��1��6"   .@�5,      �� $��Rocket��6   .��5-      '  !GroundStation.Controls.RocketPage  -   5          Name$ 
RocketData��5-       66   5.      �� 5/      $��TRIPOD��6   .��50      '  !GroundStation.Controls.TRIPODPage  -	   5          Name$ 
TRIPODData��50       51      52      54      55      