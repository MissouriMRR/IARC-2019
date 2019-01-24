import subprocess
from time import sleep

# TODO - Re-add print statements to rtg

# TODO - RTG cannot pan?

# TODO - Way to pass in custom splitter filename?


class IPC:
    # Should be used in python 2.7
    # Python 3 must be able to be run from python3 command
    # Must have packages installed that tools will use

    def __init__(self):
        for filename in ['tools/ipc/data_splitter.py', 'data_splitter.py']:
            self.splitter = subprocess.Popen('python3 {}'.format(filename), stdin=subprocess.PIPE, shell=True)

            sleep(.1)  # Poll will return None(None means process working) if immediately called after creating obj
            if not self.splitter.poll():
                break  # Success!
            else:
                output, error_output = self.splitter.communicate()
                print(error_output)
        else:
            # If loops through file names & doesnt find data splitter
            raise IOError("Data splitter file not found!")

    def send(self, data):
        if self.splitter.poll() is None:
            self.splitter.stdin.write("{}\n".format(str(data).encode()))  # Lots of warnings against stdin!

            print("IPC: {}".format(str(data)))
            # print(self.splitter.stdout.readline())  # TODO - Blocks until line sent
        else:
            print("IPC: Cannot send data")


if __name__ == '__main__':
    from math import sin, cos

    demo = IPC()

    for j in range(10000):
        i = j / 3.14
        demo.send({
            'airspeed': cos(i),
            'velocity_x': sin(i),
            'velocity_y': cos(i),
            'velocity_z': sin(i),
            'altitude': sin(i),
            'target_altitude': sin(i),
            'roll': cos(i),
            'pitch': sin(i),
            'yaw': cos(i),
            'target_roll_velocity': cos(i),
            'target_pitch_velocity': cos(i),
            'target_yaw': sin(i),
            'voltage': cos(i)
        })

        sleep(.1)

        if demo.splitter.poll() is not None:
            print("IPC: splitter.poll(): {}".format(demo.splitter.poll()))
            break

    print("IPC: Done sending data.")
    demo.splitter.terminate()
