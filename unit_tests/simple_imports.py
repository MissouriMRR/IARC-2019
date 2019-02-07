import os, sys, inspect

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

def import_parent():
    sys.path.insert(0, parent_dir)


def import_distributor():
    directory = os.path.join(parent_dir, 'tools', 'data_distributor')

    sys.path.insert(0, directory)