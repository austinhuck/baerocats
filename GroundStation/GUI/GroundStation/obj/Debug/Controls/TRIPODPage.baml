   M S B A M L   `   `   `  ����H  DGroundStation, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null?$clr-namespace:GroundStation.ControlsGroundStation.Controls  5      ?$clr-namespace:GroundStation.ControlsGroundStation.Controls  5      '    !GroundStation.Controls.TRIPODPage   5      \ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    5      R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     5      Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     5      @d2http://schemas.microsoft.com/expression/blend/2008     5      6local$clr-namespace:GroundStation.Controls     5      3UC$clr-namespace:GroundStation.Controls     5      .��5
      �   � RowDefinitions  5   
   �� 5      $��* �6    � ColumnDefinitions 5   
   �� 5      $��* �6   �� 5      $��* �6   .+�5   
   '� -   5        $��mainViewport��5      $��0��5      $��0��5      }�.   J� IsHitTestVisible .   �� EdgeMode$ Aliased=�5       '� Camera 5      P� 5      -   5        
camera�� P� Width$ 2Q�5   5    � FarPlaneDistance$ 10Q�5       � NearPlaneDistance$ 1Q�5       � LookDirection$ 0,0,-15�5      	 � UpDirection$	 0,1,05�5      
 � Position$
 0,0,21�5      x�5       g� 5!      -   5        
Light1�� g� Content 5"      t� 5#       �� Color$ White��6+    t� 	Direction$ 1, 1, -15�69   5%      g� 5&      -   5        
Light2�� 5'      t� 5(      $ White��6+   $ 	-1, 1, -15�69   5*      g� 5+      -   5        
Light3�� 5,      t� 5-      $ White��6+   $ 	0,-1,-0.55�69   5/      51      �� 52   
   -   5         ��Name$ 
canvasOn3D��52      $��0��53      $��0��54      
������ $��0,0,0,0q�58   1   59      � 5:   
   $��0��6   $��1��6     5;      �� 5<      $��* �6    �� 5=      $
��Auto �6     5?      �� 5@      $��* �6#   .+�5B      (   "GroundStation.Controls.PlotControl  -   5          Name$ Altitude��5B      $��0��6/   $��0��6<   �� 5C      -   5        $��BtnClearPlot��5C      $��
Clear Plot��6)   $��1��6>   $��0��6K   6[   5D      5E      5F      