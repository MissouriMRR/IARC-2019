'''
The plotter backend contains the tools needed to generate a graph from a
set of values provided from a .csv file.

NOTE: This plotter backend is meant to be ran through the tools  GUI
TODO: Eventually integrate backend into the GUI in a more structured way
'''
import os

import pandas
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt

PLOT_FONT_PARAMETERS = {'sans-serif' : 'Arial', 'family' : 'sans-serif'}
matplotlib.rc('font', **PLOT_FONT_PARAMETERS)

DEFAULT_MARKER_COLOR = 'black'

def get_csv_headers(filename):
    """
    Returns a list of a csv files column names. Meant to generate choices for drop down menu.

    Parameters
    ----------
    filename: str
        Filename of csv file to be parsed

    Returns
    -------
    list: List of column names from filename
    """

    return pandas.read_csv(filename, encoding="utf-8").columns.tolist()


def submit_chosen_columns(filename, x_axis_label, y_axis_label):
    """
    Parse csv file and plot the two columns against each other.

    Parameters
    ----------
    filename: str
        Filename of csv to be parsed

    x_axis_label: str
        Name of column to be used

    y_axis_label: str
        Name of column to be used
    """

    raw_data = pandas.read_csv(filename, encoding="utf-8")

    plt.title("".join([os.path.basename(filename), " : ", x_axis_label, " vs. ", y_axis_label]))

    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)

    plt.scatter(raw_data[x_axis_label], raw_data[y_axis_label], c=DEFAULT_MARKER_COLOR)

    plt.show()
