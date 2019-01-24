# Wraps around 2DLine/plt.text object

from math import *


class Metric:
    """
    Piece of data to be tracked.

    Parameters
    ----------
    output: Line2D(plt animation) or text(plt/ax.text)
        Where to output data
    func: string
        The function, as string, to generate values(takes variables x, y, z corresponding to data streams)
    x_stream: string, optional unless x used in func
        Data from drone to serve as x variable in function
    y_stream: string, optional unless y used in func
        Data from drone to serve as y variable in function
    z_stream: string, optional unless z used in func
        Data from drone to serve as z variable in function
    """

    possible_data_streams = [
        'altitude', 'airspeed', 'velocity_x', 'velocity_y', 'velocity_z', 'voltage', 'state', 'mode', 'armed',
        'roll', 'pitch', 'yaw', 'altitude_controller_output', 'altitude_rc_output', 'target_altitude',
        'pitch_controller_output', 'pitch_rc_output', 'target_pitch_velocity', 'roll_controller_output',
        'roll_rc_output', 'target_roll_velocity', 'yaw_controller_output', 'yaw_rc_output', 'target_yaw',
        'color_image', 'depth_image', None]

    def __init__(self, output, label=None, func=None, x_stream=None, y_stream=None, z_stream=None):
        self._output = output

        try:
            self._label = output.label() if not label else label
        except AttributeError:
            self._label = label

        #
        # Set func
        self._raw_func = func if func else 'x'

        # Func safety check
        for letter in self._raw_func:
            assert letter in ',.0123456789 xyz()+-*/%absintfloatsincostanhlogp', \
                "{}: Determined to be potentially unsafe at letter '{}'.".format(func, letter)

        # Init func
        if 'x' in self._raw_func:
            assert x_stream, "X in function but no x_stream!"
            assert x_stream in Metric.possible_data_streams, "Invalid x_stream!"

            if 'y' in self._raw_func:
                assert y_stream, "Y in function but no y_stream!"
                assert y_stream in Metric.possible_data_streams, "Invalid y_stream!"

                if 'z' in self._raw_func:
                    assert z_stream, "Z in function but no z_stream!"
                    assert z_stream in Metric.possible_data_streams, "Invalid z_stream!"

                    self._func = lambda x, y, z: eval(self._raw_func)
                else:
                    self._func = lambda x, y: eval(self._raw_func)
            else:
                self._func = lambda x: eval(self._raw_func)
        else:
            self._func = lambda: eval(self._raw_func)

        # Set data streams
        self._x_stream = x_stream
        self._y_stream = y_stream
        self._z_stream = z_stream

        # Create data storage
        self._data = []

    @property
    def output(self):
        """
        Line getter.

        Returns
        -------
        line
            The animation line where this metrics data will be plotted
        """

        return self._output

    @property
    def label(self):
        """
        Label getter.

        Returns
        -------
        string
            Line label
        """

        return self._label

    @label.setter
    def set_label(self, label):
        """
        Label setter.

        Parameters
        ----------
        label: string
            New line label
        """

        self._label = label

    @property
    def func(self):
        """
        Func getter.

        Returns
        -------
        lambda
            The lambda functions that this metrics values will be generated with
        """

        return self._func

    @property
    def raw_func(self):
        """
        Raw_func getter.

        Returns
        -------
        str
            The string that the function was created with
        """

        return self._raw_func

    @property
    def x_stream(self):
        """
        x_stream getter.

        Returns
        -------
        string
            Data stream to be used for x value in metric.
        """

        return self._x_stream

    @property
    def y_stream(self):
        """
        y_stream getter.

        Returns
        -------
        string
            Data stream to be used for y value in metric.
        """

        return self._y_stream

    @property
    def z_stream(self):
        """
        z_stream getter.

        Returns
        -------
        string
            Data stream to be used for z value in metric.
        """

        return self._z_stream

    @x_stream.setter
    def set_x_stream(self, stream):
        """
        x_stream setter.

        Parameters
        ----------
        stream: string
            New x_stream value
        """

        self._x_stream = stream

    @y_stream.setter
    def set_y_stream(self, stream):
        """
        y_stream setter.

        Parameters
        ----------
        stream: string
            New y_stream value
        """

        self._y_stream = stream

    @z_stream.setter
    def set_z_stream(self, stream):
        """
        z_stream setter.

        Parameters
        ----------
        stream: string
            New z_stream value
        """

        self._z_stream = stream

    @property
    def data(self):
        """
        Data getter.

        Returns
        -------
        list
            All previously generated data
        """

        return self._data

    def push_data(self, data_point):
        """
        Data setter.

        Parameters
        ----------
        data_point: float
            Data to be appended to data
        """

        self._data.append(data_point)
