from tkinter import *

import file_io
from metric import Metric


class GraphNode:
    """
    Setting for an individual graph.

    Parameters
    ----------
    tab: tkinter.Frame
        Frame that the node should be displayed on.

    graph_num: number
        Index of GraphNode on current tab

    values: dict, default=None
        Any initial values that should be set. {Item name: value}
    """

    init_settings_filename = ["usable_metrics.xml", "old_config_maker/usable_metrics.xml", "tools/old_config_maker/usable_metrics.xml"]

    rows_per_graph = 3  # Baseline how many rows per graph

    checkbox_width = 6  # How many checkboxes allowed per line

    def __init__(self, tab, graph_num, values=None):

        #
        # Settings
        self.tab = tab
        self.graph_num = graph_num

        self.row_offset = self.graph_num * GraphNode.rows_per_graph

        self.height = GraphNode.rows_per_graph

        name = "Graph{}".format(self.graph_num)

        # Pull settings from hardcoded file
        check_box_settings = self.read_available_metrics()

        #
        # Item config
        self.item_locations = {}
        self.items = {}

        # self.items = GraphNode.ItemList()

        # Header
        self.add_item('title', (0, 0, 2), Label(self.tab, text=name, font=("Arial Bold", 15), borderwidth=1))

        self.add_item('update_title', (2, 0, 2), Button(self.tab, text="Change Name", command=self.update_title, bd=2))

        # Check Boxes
        self.items['check_boxes'] = {}
        self.check_box_values = {
            key: Metric(BooleanVar(), label=key, func=value[1], x_stream=value[0][0], y_stream=value[0][1], z_stream=value[0][2])
            for key, value in check_box_settings.items()}

        self.add_item('check_boxes', (1), {metric.label: Checkbutton(self.tab, text=metric.label, var=metric.output) for metric in self.check_box_values.values()})

        self.add_item('add_check_box', (4, 0), Button(self.tab, text="Add Metric", command=self.add_check_box))

        # Time interval settings
        self.add_item('lowerTime_lbl', (0, 2, 2), Label(self.tab, text="Time interval(seconds) Lower:", borderwidth=1))

        self.add_item('lowerTime_chk', (2, 2), Entry(self.tab, width=5))

        self.add_item('upperTime_lbl', (3, 2), Label(self.tab, text="Upper:", borderwidth=1))

        self.add_item('upperTime_chk', (4, 2), Entry(self.tab, width=5))

        if values: self.set_values(values)

    @staticmethod
    def read_available_metrics():
        """
        Default metrics to display, read from GraphNode.init_settings_filename

        Returns
        -------
        dict of possible metrics and the metrics data.
        """
        # print(file_io.possible_metrics(GraphNode.init_settings_filename))

        for filename in GraphNode.init_settings_filename:
            try:
                output = file_io.possible_metrics(filename)
            except IOError:
                print("Failed to read file: {}".format(filename))

        if not output:
            raise IOError("Possible metrics file not found!")

        return output

    def add_item(self, name, loc, obj):
        if type(obj) is dict:
            for item in obj.values():
                item.configure(background="#66AA33")
        elif not type(obj) is Entry:
            obj.configure(background="#66AA33")

        self.items[name] = obj
        self.item_locations[name] = loc

    def add_check_box(self):
        """
        Add checkbox/metric to be selected
        """

        def close_config_window(self, master, entries):
            """
            Saves all of the data from the window, tries to create a metric and checkboxes and then closes window

            Parameters
            ----------
            master: tkinter window
                Window to read data from and close

            entries: List of tkinter entries
                Entry boxes to read data from
            """

            data = [e.get() for e in entries]

            try:
                metric = Metric(BooleanVar(), label=data[0], func=data[1], x_stream=data[2], y_stream=data[3],
                                z_stream=data[4])

                self.check_box_values.update({metric.label: metric})
                self.items['check_boxes'].update({metric.label: Checkbutton(self.tab, text=metric.label, var=metric.output)})
                self.items['check_boxes'][metric.label].configure(background="#66AA33")

                self.set_grid()
            except AssertionError as e:
                print("Error: {}".format(e))

            master.destroy()
            master.quit()

        master = Tk()
        master.title("Add Metric")
        master.geometry('250x130')

        Label(master, text="Label").grid(row=0)
        Label(master, text="Function").grid(row=1)
        Label(master, text="x_stream").grid(row=2)
        Label(master, text="y_stream").grid(row=3)
        Label(master, text="z_stream").grid(row=4)

        entries = [Entry(master) for _ in range(5)]

        for i, entry in enumerate(entries):
            entry.grid(row=i, column=1)

        Button(master, text="Add Metric", command=lambda: close_config_window(self, master, entries)).grid(row=9, column=0)

        master.mainloop()

    def delete(self):
        """
        Deletes all tkinter items in node.

        Returns
        -------
        Self object so it can be deleted with all of its stuff in one line
        """

        for value in self.items.values():
            if type(value) is dict:
                for item in value.values():
                    item.destroy()
            else:
                value.destroy()

        return self

    def set_grid(self, row_offset=None):
        """
        Every button/item has a grid based location and this places every item to that grid space

        Parameters
        ----------
        row_offset: number, default=None
            How many rows this graph_node should start down from top of frame
        """

        if row_offset: self.row_offset = row_offset

        rolling_offset = self.row_offset  # If checkboxes take extra lines, the lines underneath will drop one

        for key, value in self.items.items():
            if key in self.item_locations.keys():
                grid_values = self.item_locations[key]

                if type(value) is dict:
                    for i, key in enumerate(value.keys()):
                        value[key].grid(sticky="W", column=i % GraphNode.checkbox_width,
                                        row=rolling_offset + grid_values + int(i / GraphNode.checkbox_width))

                    rolling_offset += int(len(value) / GraphNode.checkbox_width)
                else:
                    value.grid(column=grid_values[0],
                               row=grid_values[1] + rolling_offset if grid_values[1] > 1 else self.row_offset,
                               columnspan=grid_values[2] if len(grid_values) > 2 else 1)

        self.height = rolling_offset + GraphNode.rows_per_graph

    def update_title(self):
        """
        Allows you to update the name of the graph
        """

        if isinstance(self.items['title'], Entry):
            name = self.items['title'].get()

            self.items['title'].destroy()

            self.items['title'] = Label(self.tab, text=name, font=("Arial Bold", 15), bg="#66AA33", borderwidth=1)

            self.items['update_title']['text'] = "Change Name"

        else:
            self.items['title'].destroy()

            self.items['title'] = Entry(self.tab, width=20)

            self.items['update_title']['text'] = "Submit"

        self.set_grid()

    # TODO - NOT FOR BASE WORKING
    def reset(self, to_reset=None):
        # TODO - Add default item settings
        if type(to_reset) is not list: to_reset = [to_reset]
        if not to_reset: to_reset = [key for key in self.items.keys()]

        for item in to_reset:
            if item == 'check_boxes':
                for value in self.check_box_values.values():
                    value.output.set(False)

    # TODO - NOT FOR BASE WORKING
    def set_values(self, values):
        self.reset('check_boxes')

        for name, value in values.items():
            if name in self.items:
                if isinstance(self.items[name], Label):
                    self.items[name]['text'] = value
                elif isinstance(self.items[name], Entry):
                    self.items[name].insert(20, value)
                else:
                    self.items[name].set(value)
            elif name in self.check_box_values.keys():
                self.check_box_values[name].output.set(value)
