import socket
import threading
from time import sleep
from typing import Tuple

HOST = "localhost"
PORT = 10000

kill = False


class Client(threading.Thread):
    def __init__(self,
                 group=None,
                 target=None,
                 name=None,
                 args=(),
                 kwargs=dict(host="localhost", port=10000, name="test")):
        super().__init__(group=group, target=target, name=name)
        host = kwargs.get("host")
        port = kwargs.get("port")
        name = kwargs.get("name")
        print("Starting client with name {} on {}:{}".format(name, host, port))
        self.SERVER_ADDRESS: Tuple[str, int] = (host, port)
        self.name = name
        self.command = None

    def run(self):
        global kill
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.SERVER_ADDRESS)
            sock.settimeout(2)
            print("connected")
            sock.send("drone {}".format(self.name).encode())
            print(sock.recv(30).decode("utf8"))

            while not kill:
                try:
                    data = sock.recv(1024)
                    if data:
                        self.command = data.decode("utf8")
                    else:
                        raise Exception
                except socket.timeout:
                    continue
        except Exception as e:
            kill = True
            print('closing socket', str(e))
            sock.close()
            return

    def get_command(self):
        data = self.command
        self.command = None
        return data


def main():
    global kill
    name = "bob"
    client = Client(kwargs=dict(host=HOST, port=PORT, name=name))
    client.start()
    try:
        while not kill:
            data = client.get_command()
            if data:
                print("Command Received:", data)
            sleep(.4)
    except:
        kill = True
        return


if __name__ == "__main__":
    main()
