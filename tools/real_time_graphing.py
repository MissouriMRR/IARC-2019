import logging
import threading
from multiprocessing import Queue
from time import sleep, time
import os

import numpy as np
from matplotlib import animation as animation
from matplotlib import pyplot as plt

from file_oi.file_io import parse_config
from real_time_graph.metric import Metric


class RealTimeGraph:
    """
    Tool to graph data as it comes in in real time.

    Version: python 2.7 / 3.6

    Requirements: Numpy, Matplotlib

    Parameters
    ----------
    get_data: func
        Function data reader will call to get data

    pan_width: int
        Time in seconds to display previous data
    """

    LOG_LEVEL = logging.INFO

    ROW_PER_COLUMN = 3  # Rows of subplots per column

    DATA_FREQ_WARNING = .5  # If time values are this far apart warn the user

    PAN_WIDTH = 10  # Seconds of previous data to show

    REL_CONFIG_PATH = "/real_time_graph/config.xml"  # Path from this file to config file

    TITLE = 'Real Time Graphing'  # Window title

    FIGURE_SIZE = (8, 6)

    ANIMATION_INTERVAL = 20

    AXIS_BOUNDS = [0, 100, 0, 10]

    SLEEP_BALANCING = 1e-5

    SLEEP_DEFAULT = 1e-1

    def __init__(self, get_data, **kwargs):
        printer = logging.getLogger()

        if not printer.handlers:
            printer.setLevel(RealTimeGraph.LOG_LEVEL)
            handler = logging.StreamHandler()
            handler.setLevel(RealTimeGraph.LOG_LEVEL)
            printer.addHandler(handler)

        if not get_data: logging.critical("RTG: No data pull function!")
        self.get_data = get_data
        self.PAN_WIDTH = abs(kwargs['pan_width']) if 'pan_width' in kwargs.keys() else RealTimeGraph.PAN_WIDTH

        # Stored which data items we are interested in
        self.tracked_data = []

        self.plot_count = 0
        self.data_count = 0

        # Stores times corresponding to each data index
        self.times = []

        self.check_time = self.start_time = time()

        # Initializes figure for real_time_graph
        plt.rcParams['toolbar'] = 'None'  # Disable matplot toolbar

        self.fig = plt.figure(figsize=RealTimeGraph.FIGURE_SIZE)
        self.fig.canvas.set_window_title(RealTimeGraph.TITLE)

        self.fig.subplots_adjust(hspace=1, wspace=0.75)  # Avoid subplot covering up titles

        # Threading
        self.sleep_time = kwargs['sleep_time'] if 'sleep_time' in kwargs.keys() else RealTimeGraph.SLEEP_DEFAULT

        self.thread_stop = kwargs['thread_stop'] if 'thread_stop' in kwargs.keys() else threading.Event()

        self.thread_queue = Queue()

    def run(self):
        self.parse_rtg_config()

        self.ani = animation.FuncAnimation(self.fig, self.plot_data, blit=False, interval=RealTimeGraph.ANIMATION_INTERVAL, repeat=False)

        threads = {
            'reader': threading.Thread(target=self.read_data, args=(self.thread_queue,)),
            'processor': threading.Thread(target=self.process_data, args=(self.thread_queue,))
        }

        for thread in threads.values():
            thread.start()

        plt.show()

        #
        # Cleanup
        self.thread_stop.set()

        for thread in threads.values():
            thread.join()

    @property
    def config_filename(self):
        """
        Returns the filename of config file.
        """

        config_path = os.path.dirname(__file__)  # Get this files location

        config_path += RealTimeGraph.REL_CONFIG_PATH

        return config_path

    def parse_rtg_config(self):
        """
        Interprets the graph config file

        Returns
        -------
        dict
            Parsed config file
        """

        try:
            output = parse_config(self.config_filename)
        except IOError:
            logging.warning("RTG: Failed to read config file '{}'!".format(self.config_filename))
            output = None

        if output is None:
            logging.critical("RTG: No configuration file found!")
            return

        # Total number of subplots
        self.graph_count = [graph["output"] == 'text' for graph in output].count(False)

        nrows = max(min(self.graph_count, RealTimeGraph.ROW_PER_COLUMN), 1)

        ncols = int(self.graph_count / nrows) + (self.graph_count % nrows)

        def unique_color_generator(colors_taken):
            colors = ['blue', 'orange', 'red', 'green', 'yellow', 'black']

            seen = set(colors_taken)

            for elem in colors:
                if elem not in seen:
                    yield elem
                    seen.add(elem)

        for graph in output:
            if graph['output'] == 'text':
                i = 0
                for metric in graph['metrics']:
                    # (Coords are percent of width/height) This is creating a text object w/ a location.
                    text = ax.text(i * (1 / len(graph['metrics'])) + .01, .01, 'matplotlib', transform=plt.gcf().transFigure)

                    self.tracked_data.append(Metric(output=text, label=metric['label'], func=metric['func'],
                                                    x_stream=metric['x_stream'], y_stream=metric['y_stream'],
                                                    z_stream=metric['z_stream']))
                    i += 1

            else:
                color_gen = unique_color_generator([metric['color'] for metric in graph['metrics']])

                # Make axis
                ax = self.fig.add_subplot(nrows, ncols, len(self.fig.get_axes()) + 1)

                ax.axis(RealTimeGraph.AXIS_BOUNDS)

                # Configure the new axis
                ax.set_title(graph['title'])
                ax.set_xlabel(graph['xlabel'])
                ax.set_ylabel(graph['ylabel'])

                for metric in graph['metrics']:
                    color = metric['color'] if metric['color'] else next(color_gen)

                    m_line, = ax.plot([], [], color=color, label=metric['label'])

                    self.tracked_data.append(Metric(output=m_line, func=metric['func'], x_stream=metric['x_stream'],
                                                    y_stream=metric['y_stream'], z_stream=metric['z_stream']))

                if graph['legend'] == 'yes' or not graph['legend']:
                    ax.legend()

    def read_data(self, thread_queue):
        """
        Reads data from network and puts it in a queue to be processed.

        Parameters
        ----------
        thread_queue: Thread queue
            Thread queue
        """

        while not self.thread_stop.is_set():
            try:
                data = self.get_data()
                thread_queue.put(data)
            except Exception as error:
                logging.warning("RTG: {}".format(error))

            # Adjust sleep times
            if self.data_count > self.plot_count:
                self.sleep_time = self.sleep_time + RealTimeGraph.SLEEP_BALANCING

            elif self.data_count == self.plot_count:
                self.sleep_time = self.sleep_time - RealTimeGraph.SLEEP_BALANCING

            sleep(self.sleep_time)

    def process_data(self, thread_queue):
        """
        Processes data put into the queue.

        Parameters
        ----------
        thread_queue: Thread queue
            Thread queue
        """

        while not self.thread_stop.is_set():
            while not thread_queue.empty():
                data = thread_queue.get(False, self.sleep_time)

                if not data:
                    logging.warning("RTG: No data!")
                    sleep(.25)
                    continue

                self.times.append(time() - self.start_time)

                # Checks data frequency to see if poor quality
                try:
                    if self.times[-1] > self.times[-2] + RealTimeGraph.DATA_FREQ_WARNING:
                        logging.warning("RTG: Data quality: Sucks")
                        pass
                except IndexError:
                    pass

                for metric in self.tracked_data:
                    func = metric.func

                    values = []

                    axes = list('xyz')
                    for axis in axes:
                        stream = getattr(metric, '{}_stream'.format(axis))
                        if stream:
                            values.append(data[stream])

                    x_val = func(*values)

                    metric.push_data(x_val)
                self.data_count += 1

    def plot_data(self, frame):
        """
        Plots data

        Parameters
        ----------
        frame:
            Arbitrary variable, animation function sends frame in by default.

        Returns
        -------
        list
            Line of each tracked metric

        """

        # If there is no new data to plot, then exit the function.
        if self.plot_count == self.data_count:
            return [metric.output for metric in self.tracked_data]

        for metric in self.tracked_data:
            try:
                metric.output.set_data(np.asarray(self.times), np.asarray(metric.data))
            except AttributeError:
                metric.output.set_text("{}: {}".format(metric.label, str(metric.data[-1])[:5]))

        for ax in self.fig.get_axes():
            try:
                ax.relim()
                ax.autoscale(axis='y')
            except ValueError as e:
                logging.error("RGG: Caught '{}'!\n \
                              Past 10 times: {}\n \
                              Past 10 outputs: {}".format(e, self.times[-10:], metric.data[-10:]))

            current_time = int(self.times[-1])

            ax.set_xlim(current_time - self.PAN_WIDTH, current_time + self.PAN_WIDTH)

        self.plot_count += 1

        return [metric.output for metric in self.tracked_data]
