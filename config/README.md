# Multirotor Onboard Computer and PixHawk Configs
`configs/` is used for keeping each and every configuration used for Multirotor in the event of an onbaord computer or flight board failure. 

## pixhawk_params/
This folder is used to store parameters exported from a ground control station into files.
### Usage
Instructions for importing a parameter file can be found [here.](https://docs.google.com/document/d/1zZzH87_Gwm47xbhOUgo8qDxqH14eNERKENXVQBF1z8E/edit#heading=h.ffn7z82owif7)

## services/ 
This folder will store systemd units/services that will be used to make onboard computing easier. 

### Add service to onboard computer
Addidng the service to the onboard computer is as simple as moving the `.service` file to `/etc/systemd/system`

### Services
* `mavlinkbridge.service` - Used to bridge the PixHawk flight board with the WiFi to allow for connecting to dronve via ground control station via the network.
    - `sudo service mavlinkbridge restart` - used to restart the network bridge 

## dronerc
`dronerc` is a collection bash aliases for onboard computers.
### Usage
`source dronerc` will apply the aliases.
### Aliases
* `drone_console` - Stops the `mavlinkbridge` service, conects to the PixHawk using USB, and opens a mavproxy command prompt.