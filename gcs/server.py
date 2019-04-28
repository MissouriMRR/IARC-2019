import argparse
import json
import logging
import socket
import threading
from typing import Any, List, Tuple

logger = logging.getLogger(__name__)

DEFAULT_HOST: str = "localhost"
DEFAULT_PORT: int = 10000
TIMEOUT: int = 1

kill: bool = False
messages = {}


def handle_voice(target, text):
    if text == "land":
        msg = {"command": "land"}
    elif text == "takeoff":
        msg = {"command": "takeoff", "altitude": 1}
    elif text == "heal":
        msg = {"command": "heal"}
    else:
        if text == "forward":
            vec = (1, 0, 0)
        elif text == "left":
            vec = (0, -1, 0)
        elif text == "right":
            vec = (0, 1, 0)
        elif text == "backward":
            vec = (-1, 0, 0)
        else:
            vec = (0, 0, 0)
        msg = {
            "command": "move",
            "north": vec[0],
            "east": vec[1],
            "down": vec[2],
            "duration": 4
        }

    messages[target].append(json.dumps(msg))


class DroneThread(threading.Thread):
    def __init__(self,
                 socket=None,
                 messages: List[str] = None,
                 drone_name: str = None,
                 group=None,
                 target=None,
                 name=None) -> None:
        super().__init__(group=group, target=target, name=name)
        self.sock = socket
        self.messages: List[str] = messages
        self.name = drone_name

        self.sock.settimeout(TIMEOUT)

    def run(self) -> None:
        global kill
        try:
            while not kill:
                try:
                    if not self.sock.recv(1):
                        # Got heartbeat
                        raise Exception("Socket closed by drone")
                    if self.messages:
                        self.sock.send(b"1")
                        message: str = self.messages.pop(0).encode()
                        logger.debug("<{}> Sending: {}".format(
                            self.name, message))
                    else:
                        message: str = b"0"
                    self.sock.send(message)
                except socket.timeout:
                    continue
        except Exception as e:
            logger.error("DRONE ERROR: {}".format(str(e)))
        finally:
            self.sock.close()


class TabletThread(threading.Thread):
    def __init__(self,
                 socket=None,
                 callback=None,
                 group=None,
                 target=None,
                 name=None) -> None:
        super().__init__(group=group, target=target, name=name)
        self.sock = socket
        self.callback = callback

        self.sock.settimeout(TIMEOUT)

    def run(self) -> None:
        global kill
        try:
            while not kill:
                try:
                    # Update to have heartbeat
                    data: str = self.sock.recv(100).decode("utf8")[:-2]
                    if len(data) > 0:
                        logging.debug(data)
                        self.callback("bob", data)
                    else:
                        raise Exception("Tablet disconnect")
                except socket.timeout:
                    continue
        except Exception as e:
            logger.error("TABLET ERROR: {}".format(str(e)))
        finally:
            self.sock.close()


class Server(threading.Thread):
    def __init__(self,
                 host: str = "localhost",
                 port: int = 10000,
                 messages=None,
                 group=None,
                 target=None,
                 name=None):
        super().__init__(group=group, target=target, name=name)
        self.server_address: Tuple[str, int] = (host, port)
        self.messages = messages

    def run(self):
        global kill
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(self.server_address)
            sock.listen(5)
            logger.info("Started server on {}:{}".format(*self.server_address))
            sock.settimeout(TIMEOUT)

            count: int = 0
            while not kill:
                try:
                    connection, client_address = sock.accept()
                    logger.debug(
                        "New connection from {}".format(client_address))
                    logger.debug(
                        "Awaiting registration for {}".format(client_address))
                    device, name = connection.recv(21).decode("utf8").split()
                    connection.send(b"1")
                    logger.info("New {}: {}".format(device, name))

                    if device == "drone":
                        self.messages[name]: List[str] = []
                        DroneThread(
                            socket=connection,
                            messages=self.messages[name],
                            drone_name=name).start()
                    elif device == "tablet":
                        TabletThread(
                            socket=connection, callback=handle_voice).start()

                    count += 1
                except socket.timeout:
                    continue
        except Exception as e:
            logger.error("SERVER ERROR: {}".format(str(e)))
        finally:
            kill = True
            sock.close()


def keyboard_input(messages) -> None:
    global kill
    try:
        while True:
            try:
                thing: str = input("> ")
                data: List[str] = thing.split()
                message: Any = {}
                if data[1] == "land":
                    message["command"] = "land"
                elif data[1] == "takeoff":
                    message = {
                        "command": "takeoff",
                        "altitude": float(data[2])
                    }
                elif data[1] == "move":
                    message = {
                        "command": "move",
                        "north": float(data[2]),
                        "east": float(data[3]),
                        "down": float(data[4]),
                        "duration": float(data[5])
                    }
                else:
                    raise KeyError(data[1] + "is not a command")
                if message:
                    blob = json.dumps(message)
                    messages[data[0]].append(blob)
            except (KeyError, IndexError) as e:
                logger.error("Bad input: {}".format(str(e)))
                continue
    except Exception as e:
        logger.error("INPUT LOOP ERROR: {}".format(str(e)))
    except:
        pass
    finally:
        kill = True


def main() -> None:
    parser = argparse.ArgumentParser(description='Flight starter')
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='verbose flag')
    parser.add_argument('--host', required=False, type=str)
    parser.add_argument('--port', required=False, type=int)

    args = parser.parse_args()

    debug = False if args.host and args.port else True
    LOG_LEVEL = logging.DEBUG if args.verbose else logging.INFO

    logging.basicConfig(level=LOG_LEVEL)

    if args.host and args.port:
        server = Server(args.host, args.port, messages=messages)
    else:
        server = Server(messages=messages)
    server.start()
    keyboard_input(messages)


if __name__ == "__main__":
    main()
