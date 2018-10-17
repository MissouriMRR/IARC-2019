import numpy as np
from matplotlib import pyplot as plt, animation as animation

import threading
from multiprocessing import Queue

from time import sleep, time

from tools.real_time_graphing.metric import Metric

from tools.file_io import file_io

from tools.real_time_graphing.demo_data_gen import get_demo_data


class RealTimeGraph:
    """
    Description

    Parameters
    ----------
    get_data: func
        Function data reader will call to get data

    pan_width: int
        Time in seconds to display previous data
    """

    config_filename = 'config.xml'  # Location of configuration file

    max_rows = 3  # Rows of subplots per column

    data_freq_warning = .5  # If time values are this far apart warn the user

    def __init__(self, get_data=get_demo_data, pan_width=10):
        self.get_data = get_data
        self.pan_width = abs(pan_width)

        # Stored which data items we are interested in
        self.tracked_data = []

        self.plot_count = 0
        self.data_count = 0

        # Stores times corresponding to each data index
        self.times = []

        self.check_time = self.start_time = time()

        # Initializes figure for real_time_graphing
        plt.rcParams['toolbar'] = 'None'  # Disable matplot toolbar

        self.fig = plt.figure(figsize=(8, 6))
        self.fig.canvas.set_window_title('Real Time Graphing')

        self.parse_config()

        self.ani = animation.FuncAnimation(self.fig, self.plot_data, blit=False, interval=20, repeat=False)

        # Threading
        self.sleep_time = 1e-1

        self.thread_stop = threading.Event()

        self.thread_queue = Queue()

        threads = {
            'reader': threading.Thread(target=self.read_data, args=(self.thread_queue,)),
            'processor': threading.Thread(target=self.process_data, args=(self.thread_queue,))
        }

        for thread in threads.values():
            thread.start()

        self.fig.subplots_adjust(hspace=1, wspace=0.75)  # Avoid subplot overlap

        #
        # Code stops here until matplot window closed
        plt.show()

        #
        # Cleanup
        self.thread_stop.set()

        for thread in threads.values():
            thread.join()

    def parse_config(self):
        """
        Interprets the graph config file

        Returns
        -------
        dict
            Parsed config file
        """

        output = file_io.parse_config(RealTimeGraph.config_filename)

        # Total number of subplots
        graph_count = [graph["output"] == 'text' for graph in output].count(False)

        nrows = min(graph_count, RealTimeGraph.max_rows)
        ncols = int(graph_count / nrows) + (graph_count % nrows > 0)

        def unique_color_generator(colors_taken):
            color_list = ['blue', 'orange', 'red', 'green', 'yellow', 'black', 'Ran out of colors!']

            seen = set(colors_taken)

            for elem in color_list:
                if elem not in seen:
                    yield elem
                    seen.add(elem)

        for graph in output:
            if graph['output'] == 'text':
                i = 0
                for metric in graph['metrics']:
                    # Coords are percent
                    text = ax.text(i * (1 / len(graph['metrics'])) + .01, .01, 'matplotlib', transform=plt.gcf().transFigure)

                    self.tracked_data.append(Metric(output=text, label=metric['label'], func=metric['func'],
                                                    x_stream=metric['x_stream'], y_stream=metric['y_stream'],
                                                    z_stream=metric['z_stream']))
                    i += 1

            else:
                color_gen = unique_color_generator([metric['color'] for metric in graph['metrics']])

                # Make axis
                ax = self.fig.add_subplot(nrows, ncols, len(self.fig.get_axes()) + 1)

                ax.axis([0, 100, 0, 10])

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
            data = self.get_data()
            thread_queue.put(data)

            # Adjust sleep times
            if self.data_count > self.plot_count:
                self.sleep_time = self.sleep_time + 1e-5

            elif self.data_count == self.plot_count:
                self.sleep_time = self.sleep_time - 1e-5

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

                self.times.append(time() - self.start_time)

                # Checks data frequency to see if poor quality
                try:
                    if self.times[-1] > self.times[-2] + RealTimeGraph.data_freq_warning:
                        print("Data quality: Sucks")
                except IndexError:
                    pass

                for metric in self.tracked_data:
                    func = metric.func

                    x = data[metric.x_stream] if metric.x_stream else None
                    y = data[metric.y_stream] if metric.y_stream else None
                    z = data[metric.z_stream] if metric.z_stream else None

                    x_val = func(x, y, z) if z else (func(x, y) if y else func(x))

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
                print("Caught '{}'!\nPast 10 times: {}\nPast 10 outputs: {}".format(e, self.times[-10:], metric.data[-10:]))

            current_time = int(self.times[-1])

            ax.set_xlim(current_time - self.pan_width, current_time + self.pan_width)

        self.plot_count += 1

        return [metric.output for metric in self.tracked_data]


if __name__ == '__main__':
    test_object = RealTimeGraph()
