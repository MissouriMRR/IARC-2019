# Ours
from ..Drone.drone import Drone
from ..Drone.drone_controller import DroneController

if __name__ == '__main__':

    # Make the controller
    controller = DroneController(Drone())

    # Start the controller's loop
    controller.run_loop()
