# Real Time Graphing IARC-2019
## Installation
When creating a grapher object there is 2 optional parameters:
```
    get_data: (func, default get_demo_data) The function to be called to get data.
    pan_width: (int, default 10) Time in seconds to display graph in the past. This is essentially the x limit.
```

## Configuration
There is a configuration file located in the same folder as real_time_graphing.py.
You may edit the config file by hand or using the config editor GUI.

Subplot settings:
```
    title: (optional) The title of the graph.
    output: (optional) If output is set to 'text', every metric will be displayed at bottom in text form(should only be
                        one of these at a time.
    xlabel: (optional) The x axis label.
    ylabel: (optional) The y axis label.
    legend: (optional, default='yes') Whether or not to display a legend on the subplot, must be yes to make true.
```
Metric settings:

```
    line: Either the animation line or a piece of text.
    label: (optional, taken from line if is one) Title of metric that appears on legend.
    func: Function to generate data for graph. Can use variables x, y, z(if a data stream is set for that variable).
            Can make use of primitive python math functions ie +, -, *, /, (), max, min...
    x_stream: (optional) The data stream to be sent to x variable.
    y_stream: (optional) The data stream to be sent to y variable(x variable must be set first!).
    z_stream: (optional) The data stream to be sent to z variable(x & y variables must be set first!).
    color: (optional) Matplotlib standard colors or hex(#FFFFFF) color value. Can set color or have generated on per
            subplot basis. Color generator currently only can generate 6 unique colors so if you have more than 6
            metrics on a plot you may need to manually set colors.
```
Choices of data_streams are:
```
    'roll', 'pitch', 'yaw', 'target_altitude', 'target_roll_velocity',
    'target_pitch_velocity', 'altitude', 'airspeed', 'velocity_x', 
    'velocity_y', 'velocity_z', 'voltage', 'state', 'mode',
    'armed', 'altitude_controller_output', 'altitude_rc_output', 
    'pitch_controller_output', 'pitch_rc_output', 'roll_controller_output', 
    'roll_rc_output', 'yaw_controller_output', 'yaw_rc_output', 
    'target_yaw', 'color_image', 'depth_image'
```
## Operating
This tool is only for the real time graphing, pulling data from the drone. If you wish to plot data from csv files, there is a csv graphing tool.
## Troubleshooting
If you have issues or suggestions, message Cole Dieckhaus or Thomas McKanna on slack or email cole - csdhv9@mst.edu.