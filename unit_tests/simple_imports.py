import os, sys, inspect

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

def import_parent():
    sys.path.insert(0, parent_dir)


def import_distributor():
    directory = parent_dir + r"\tools\data_distributor"

    sys.path.insert(0, directory)