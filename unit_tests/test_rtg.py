from demo_data_gen import get_demo_data

import simple_imports
simple_imports.import_distributor()

from rtg.real_time_graphing import RealTimeGraph


class RTGTest():
    base_path = r"test_configs/real_time_graphing/"

    def main(self):
        func_list = [func for func, value in RTGTest.__dict__.items() if isinstance(RTGTest.__dict__[func], staticmethod)]

        for func in func_list:
            getattr(self, func)()

    @staticmethod
    def plotter_normal():
        """
        Runs real time graph.
        """

        test_object = RealTimeGraph(get_demo_data)

        test_object.config_filename = RTGTest.base_path + "normal.xml"

        print("Working: Should be showing 3 metrics w/ random input data.")

        test_object.run()

    @staticmethod
    def plotter_config():
        """
        Runs real time graph.
        """

        test_object = RealTimeGraph(get_demo_data)

        print("Config Test: Should be using default config file.")

        test_object.run()

    @staticmethod
    def plotter_multiple_graphs():
        """
        Runs real time graph.
        """

        test_object = RealTimeGraph(get_demo_data)

        test_object.config_filename = RTGTest.base_path + "multiple_graphs.xml"

        print("Multiple Graphs: Should be showing multiple graphs.")
        
        test_object.run()


if __name__ == '__main__':
    RTGTest().main()
