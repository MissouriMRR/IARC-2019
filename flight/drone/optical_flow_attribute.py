
class OpticalFlow(object):
    """The Optical Flow readings.

    The message definition is here: https://pixhawk.ethz.ch/mavlink/#OPTICAL_FLOW

    time_usec :
        Timestamp
    sensor_id :
        Sensor ID
    flow_x : float
        Flow in X sensor direction
    flow_y : float
        Flow in Y sensor direction
    flow_comp_m_x : float
        Flow in x-sensor direction, angular-speed compensated
    flow_comp_m_y : float
        Flow in y-sensor direction, angular-speed compensated
    quality : float
        Optical flow quality / confidence. 0: bad, 255: maximum quality
    ground_distance : float
        Distance from the ground. A positive value means distance known, while
        a negative value means unknown distance.
    """

    FORMAT_STRING = 'OPTICAL_FLOW: time_usec={},sensor_id={},flow_x={}, \
                    flow_y={}, flow_comp_m_x={},flow_comp_m_y={},quality={}, \
                    ground_distance={}'

    def __init__(self, time_usec=None, sensor_id=None, flow_x=None,
            flow_y=None, flow_comp_m_x=None, flow_comp_m_y=None, quality=None,
            ground_distance=None):
        """
        OpticalFlow object constructor.
        """
        self.time_usec = time_usec
        self.sensor_id = sensor_id
        self.flow_x = flow_x
        self.flow_y = flow_y
        self.flow_comp_m_x = flow_comp_m_x
        self.flow_comp_m_y = flow_comp_m_y
        self.quality = quality
        self.ground_distance = ground_distance

    def __str__(self):
        """
        String representation used to print the OpticalFlow object.
        """
        return OpticalFlow.FORMAT_STRING.format(
            self.time_usec, self.sensor_id, self.flow_x, self.flow_y,
            self.flow_comp_m_x, self.flow_comp_m_y, self.quality,
            self.ground_distance)
