# Config Maker IARC-2019
A GUI to easily create config files for various tools.

## Configuration
A base list of possible metrics is generated from the usable_metrics.xml file.

The file is read in the format:

    <desiredgraphs>
        <graph title="Possible Metrics" xlabel="Seconds" ylabel="Y">
            <metric label="label" x_stream="data stream" />
            <metric label="label" x_stream="data stream" />
            ...
        </graph>
    </desiredgraphs>


A data stream is a stream of data as it comes in from the drone in pairs {header: value}.

Possible data streams - List of headers:
    
    'roll', 'pitch', 'yaw', 'target_altitude', 'target_roll_velocity',
    'target_pitch_velocity', 'altitude', 'airspeed', 'velocity_x', 
    'velocity_y', 'velocity_z', 'voltage', 'state', 'mode',
    'armed', 'altitude_controller_output', 'altitude_rc_output', 
    'pitch_controller_output', 'pitch_rc_output', 'roll_controller_output', 
    'roll_rc_output', 'yaw_controller_output', 'yaw_rc_output', 
    'target_yaw', 'color_image', 'depth_image'

## Operating
#### Starting
To start the config maker, the file gui_main.py should be run.

#### Use
When the gui is started there is 3 sections. 
- Menu Bar
- Tab Selector
- Graph display

The Menu Bar currently has three buttons. 
- Add Graph -> Adds graph to currently selected tab
- Delete Graph -> Deletes last graph on currently selected tab
- Save -> Opens prompt to select filename and saves data on tab to that file.


The Tab Selector currently has two settings which are currently arbitrary.

The Graph Display contains the data that will actually be saved.

- Each graph on the display represents a different graph to be displayed.
- Each graph can contain different or multiple metrics 
- Can have different time intervals.
- Can add custom metrics -> A prompt is opened when the 'Add Metric' 
  button is clicked
- The name of the graph can be changed which the 'Change Name' button
  but submit must be clicked before saving.
- Can delete individual graphs by clicking its specific delete function
- Currently no scroll bar so the number of graphs possible is how many 
  can fit on screen, although the graphers cannot handle more than 3 at
  a time very effectively.


## Troubleshooting
If you have issues or suggestions, message Cole Dieckhaus on slack or email csdhv9@mst.edu.