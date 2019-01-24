from tkinter import filedialog
from tkinter import Tk

import pandas as pd
import matplotlib.pyplot as plt

try:
    from tools.file_io.file_io import parse_config
    from tools.real_time_graphing.metric import Metric
except ImportError:
    from file_io import parse_config
    from metric import Metric


def make_whole_graph():
    """
    Builds graph from csv files.
    """

    # Get startup data
    root = Tk()  # Create tkinter window

    # Select config & data to graph through explorer prompt
    config_file = filedialog.askopenfilename(
        title="Select the Graphing Config file",
        filetypes=(("xml files", "*.xml"), ("csv files", "*.csv"), ("all files", "*.*"))
    )

    data_file = filedialog.askopenfilename(
        title="Select file to Graph", filetypes=(("csv files", "*.csv"), ("all files", "*.*"))
    )

    root.destroy()  # Close the tkinter window

    # Read data & config
    raw_data = pd.read_csv(data_file)

    config = parse_config(config_file)

    fig = plt.figure()

    for i, graph in enumerate(config):
        # Prepare data
        min_time_limit = float(graph['lower_time']) if graph['lower_time'] else 0
        max_time_limit = float(graph['upper_time']) if graph['upper_time'] else 100000

        rows_below_max = raw_data['secFromStart'] < max_time_limit
        rows_above_min = raw_data['secFromStart'] > min_time_limit

        parsed_data = raw_data[rows_below_max & rows_above_min]

        graphs_per_col = 3

        ax = fig.add_subplot(min(graphs_per_col, len(config)), len(config) // graphs_per_col + 1, i + 1)

        # Plot data
        for column in graph['metric']:
            metric = Metric(None, "", column['func'], "pitch", "pitch", "pitch")

            if column['func'] is 'x':
                data = parsed_data[column['x_stream']]
            else:
                print("Function for metric '{}' being processed".format(column['label']))

                if column['x_stream']:
                    if column['y_stream']:
                        if column['z_stream']:
                            data = [
                                metric.func(
                                    parsed_data[column['x_stream']][i],
                                    parsed_data[column['y_stream']][i],
                                    parsed_data[column['z_stream']][i])
                                for i in range(len(parsed_data[column['x_stream']]))]
                        else:
                            data = [metric.func(parsed_data[column['x_stream']][i], parsed_data[column['y_stream']][i])
                                    for i in range(len(parsed_data[column['x_stream']]))]
                    else:
                        data = [metric.func(x) for x in parsed_data[column['x_stream']]]
                else:
                    data = [metric.func() for _ in range(len(parsed_data[column['x_stream']]))]

            ax.plot(parsed_data['secFromStart'], data)

        plt.legend([metric['label'] for metric in graph['metric']])  # Enable legend

    plt.show()  # Show the matplotlib plot


if __name__ == '__main__':
    make_whole_graph()
