import csv
import logging
import os
import time

from numpy import nan


class Logger:
    """
    Logs data sent to it.

    Run Requirements: Must be run from base folder or in tools folder so that it has somewhere to save logs to.
                      Else make a folder called generated_logs in the running directory.

    Version: python 2.7 / 3.6

    Parameters
    ----------
    desired_headers: list
        List of headers of data streams to logger.
    """

    EMPTY_VALUE = nan  # (np.nan) Value to put in csv if no data given

    TIME_HEADER = 'secFromStart'  # Header for time value, log_grapher also uses - must change there too

    SAVE_FOLDER = "generated_logs/"

    def __init__(self, desired_headers):

        # Setup dict w/ headers matched to desired data stream
        if not desired_headers: logging.critical("Logger: No headers given!!!")
        self.desired_headers = [Logger.TIME_HEADER] + desired_headers

        # Find directory and choose filename

        self.resource_file_dir = self.find_directory()

        date = time.strftime('%x').replace('/', '-')  # Gets today's date & sets / to _ as not mess up the directory

        file_name_start = '{}_flight_'.format(date)

        if os.listdir(self.resource_file_dir):
            # For each file in the directory with the same date, find the highest flight number

            flight_num_list = []

            for element in os.listdir(self.resource_file_dir):
                if file_name_start in element:
                    flight_num_list.append(int(element.split(file_name_start)[1].split('.csv')[0]))
                else:
                    flight_num_list.append(0)

            prev_flight_num = max(flight_num_list)

        else:
            prev_flight_num = 0

        daily_flight = prev_flight_num + 1

        self.directory = '{}{}{}.csv'.format(self.resource_file_dir, file_name_start, str(daily_flight))

        # Create file
        self.logging_file = open(self.directory, "w")

        logging.warning("Logger: File created: {}".format(self.directory))

        self.writer = csv.DictWriter(self.logging_file, fieldnames=self.desired_headers)

        self.writer.writeheader()

        # Init timing variables
        self.start_time = time.time()
        self.last_update_time = 0

    @staticmethod
    def find_directory():
        """
        Finds the generated_logs folder
        """

        resource_file_dir = os.getcwd()

        project_filename = 'IARC-2019'

        if project_filename in resource_file_dir:
            resource_file_dir = resource_file_dir.split(project_filename)[0]

        if resource_file_dir[-1] not in ["\\", "/"]:
            resource_file_dir += '/'

        resource_file_dir += Logger.SAVE_FOLDER

        if not os.path.isdir(resource_file_dir):
            os.mkdir(resource_file_dir)

        return resource_file_dir

    def __enter__(self):
        """
        On with statement creation
        """

        return self

    def __exit__(self, *args):
        """
        On with statement exit
        """

        self.logging_file.close()

    def quit(self):
        """
        Closes file that was logging data.
        """

        self.logging_file.close()

    def update(self, input_data):
        """
        Log data to file.

        Parameters
        ----------
        input_data: dict {header: value}
            Stream of new data to be logged
        """

        current_time = time.time()

        if self.last_update_time != current_time:
            # Format data to write
            output_data = {}

            for element in self.desired_headers:
                if element is Logger.TIME_HEADER:
                    output_data.update({element: current_time - self.start_time})
                elif element not in input_data:
                    output_data.update({element: Logger.EMPTY_VALUE})
                else:
                    output_data.update({element: input_data[element]})

            # Write data
            self.writer.writerow(output_data)

            self.last_update_time = current_time
