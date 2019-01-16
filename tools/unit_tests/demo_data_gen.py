import numpy.random as random


def get_demo_data():
    """
    Generates random data in the format the grapher will receive data.

    Returns
    -------
    dict
        Keys of data streams w/ randomly generated data.
    """

    gen = random.rand(26, 1)

    keys = [
        'altitude', 'airspeed', 'velocity_x', 'velocity_y', 'velocity_z', 'voltage', 'state', 'mode', 'armed', 'roll',
        'pitch', 'yaw', 'altitude_controller_output', 'altitude_rc_output', 'target_altitude',
        'pitch_controller_output', 'pitch_rc_output', 'target_pitch_velocity', 'roll_controller_output',
        'roll_rc_output', 'target_roll_velocity', 'yaw_controller_output', 'yaw_rc_output', 'target_yaw', 'color_image',
        'depth_image'
    ]
    
    imaginary_data = {key: gen[i, 0] for i, key in enumerate(keys)}

    return imaginary_data
