import json
import logging
import socket
import threading
from time import sleep
from typing import Tuple

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 10000
DEFAULT_NAME = "test"
TIMEOUT = 1

kill = False


class NetClient(threading.Thread):
    def __init__(self,
                 host=DEFAULT_HOST,
                 port=DEFAULT_PORT,
                 client_name=DEFAULT_NAME,
                 flight_session=None,
                 group=None,
                 target=None,
                 name=None) -> None:
        super().__init__(group=group, target=target, name=name)
        logger.info("Starting drone {} on {}:{}".format(
            client_name, host, port))
        self.SERVER_ADDRESS = (host, port)
        self.name = client_name
        self.command = None
        self.messages = []
        self.fs = flight_session

    def run(self) -> None:
        global kill
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.SERVER_ADDRESS)
            logger.info(
                "Established connection to Ground Control. Registering...")
            sock.send("drone {}".format(self.name).encode())
            resp = sock.recv(1)
            logger.debug("Received: {}".format(resp))
            status = "Successful" if resp == b"1" else "Failure"
            logger.info("Registration {}".format(status))
            sock.settimeout(TIMEOUT)

            while not kill:
                try:
                    if self.messages:
                        sock.send(b"1")
                        message = self.messages.pop(0).encode()
                        print("SENDING MESSAGE:", message)
                        sock.send(message)
                    else:
                        sock.send(b"0")
                    data = sock.recv(1)
                    if data == b"1":
                        command = sock.recv(1024)
                        logger.debug("Received: {}".format(command))
                        self.command = command.decode("utf8")
                except socket.timeout:
                    continue
        except socket.error as e:
            logger.error('SOCKET ERROR: {}'.format(str(e)))
        except Exception as e:
            print("NET ERROR", str(e))
        finally:
            sock.close()
            kill = True
            return

    def send_teamwork(self, message):
        self.messages.append(json.dumps(message))

    def get_command(self) -> str:
        data = self.command
        self.command = None
        return data


def main() -> None:
    global kill
    host = "localhost"
    port = 10000
    name = "footclan"
    client = NetClient(host, port, client_name=name)
    client.start()
    try:
        while not kill:
            data = client.get_command()
            if data:
                print("Command Received:", data)
            sleep(.4)
    except Exception as e:
        print(str(e))
        kill = True


if __name__ == "__main__":
    main()
