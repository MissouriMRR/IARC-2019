from tkinter import Menu, PhotoImage, TclError, Tk, filedialog

import file_io
from tab_manager import TabManager


class GUI:
    """
    GUI to edit and create config files for all tools.

    Version: python 3.6
    """

    icon_file = 'ninja_icon.gif'

    def __init__(self):
        # Window setup
        self.window = Tk()
        self.window.title("Multirotor Robot Data Graphing Tool")
        self.window.geometry('750x500')
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        try:
            icon = PhotoImage(file=GUI.icon_file)
            self.window.tk.call('wm', 'iconphoto', self.window._w, icon)

        except TclError:
            print("Failed to open icon")

        # Tabs
        self.graph_manager = TabManager(self.window)
        self.graph_manager.add_graph()

        # Top Menu
        self.menu_bar = Menu(self.window, fg="#66AA33")
        self.window.config(menu=self.menu_bar)

        # TODO - self.menu_bar.add_command(label='Pick a file', command=self.graphs.pick_graphing_file)

        self.menu_bar.add_command(label="Add new graph", command=self.graph_manager.add_graph)
        self.menu_bar.add_command(label="Delete Last Graph", command=self.graph_manager.delete_graph)

        # TODO - self.menu_bar.add_command(label="Pull old config")

        self.menu_bar.add_command(label="Save", command=self.save)

        # TODO - self.menu_bar.add_checkbutton(label="Share tab settings", command=self.graphs.share_settings)

        # Display window
        self.window.mainloop()

    def close_window(self):
        """
        A custom close function.
        """

        self.window.destroy()

    def save(self, section=None):
        """
        Save tab data into config file.

        Parameters
        ----------
        section: number, default=None
            Tab index to save, if not default use current tab.
        """

        filename = filedialog.asksaveasfilename(
            title="Save config as...", defaultextension=".xml", filetypes=(("xml file", "*.xml"),("All Files", "*.*")))

        if filename:
            file_io.write_config(filename, self.graph_manager.get_graph_data(tab_id=section))


if __name__ == "__main__":
    myClass = GUI()
