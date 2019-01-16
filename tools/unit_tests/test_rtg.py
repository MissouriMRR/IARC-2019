import import_parent_directory

from demo_data_gen import get_demo_data

from real_time_graphing import RealTimeGraph


class RTGTest():
    base_path = r"test_configs/real_time_graphing/"

    def main(self):
        func_list = [func for func, value in RTGTest.__dict__.items() if type(RTGTest.__dict__[func]) is staticmethod]

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
        try:
            test_object.run()
        except Exception as e:
            print("Success!")


if __name__ == '__main__':
    RTGTest().main()
