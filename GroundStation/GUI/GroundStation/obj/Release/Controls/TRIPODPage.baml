   M S B A M L   `   `   `  ���� H  DGroundStation, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null?$clr-namespace:GroundStation.ControlsGroundStation.Controls  ?$clr-namespace:GroundStation.ControlsGroundStation.Controls  '    !GroundStation.Controls.TRIPODPage   \ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     @d2http://schemas.microsoft.com/expression/blend/2008     6local$clr-namespace:GroundStation.Controls     3UC$clr-namespace:GroundStation.Controls     .���   � RowDefinitions  �� $��* � � ColumnDefinitions �� $��* ��� $��* �.+�'� -   $��mainViewport��$��0��$��0��}�.   J� IsHitTestVisible .   �� EdgeMode$ Aliased=� '� Camera P� -   
camera�� P� Width$ 2Q� � FarPlaneDistance$ 10Q� � NearPlaneDistance$ 1Q� � LookDirection$ 0,0,-15�	 � UpDirection$	 0,1,05�
 � Position$
 0,0,21�x�g� -   
Light1�� g� Content t�  �� Color$ White�� t� 	Direction$ 1, 1, -15�g� -   
Light2�� t� $ White��$ 	-1, 1, -15�g� -   
Light3�� t� $ White��$ 	0,-1,-0.55��� -    ��Name$ 
canvasOn3D��$��0��$��0��
������ $��0,0,0,0q�� $��0��$��1��  �� $��* ��� $
��Auto � �� $��* �.+�(   "GroundStation.Controls.PlotControl  -     Name$ Altitude��$��0��$��0���� -   $��BtnClearPlot��$��
Clear Plot��$��1��$��0��