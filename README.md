# IARC-2019
Autonomous flight code for [IARC
2019](http://www.aerialroboticscompetition.org/)

# Installation
All below steps will assume you are the **root** user.

## Quad
Currently, the only supported device is an Intel UPBoard running Ubilinux

### Prerequisites:
* Python 3.5 (Others may work, untested)
* Python 3.5 pip

### Steps:
1. Install pip requirements
    1. Navigate into the `quad` folder of this repository
    2. Run the following command:
    ```bash
    # Installs easy to install packages
    $ pip3.5 install -r requirements.txt
    ```
2. Install the Lidar libraries and python package
    1. Clone the repository for [sweep-sdk](https://github.com/scanse/sweep-sdk)
    2. Navigate into the **root** of the *sweep-sdk* repository, and into the folder `libsweep`
    3. Follow the directions in
      the *README* to install
    4. Navigate back to the **root** of the repository, and into the `sweeppy` folder
    5. Run the following command:
    ```bash
    # Installs the sweeppy package
    $ python3.5 setup.py install
    ```
3. Install the RPi.GPIO library for the UPBoard
    1. Clone the repository for [Ubilinux
      RPi.GPIO](https://github.com/emutex/RPi.GPIO)
    2. Navigate into the **root** of the repository
    3. Run the following command:
    ```bash
    # Installs the RPi.GPIO package
    $ python3.5 setup.py install
    ```
4. Enable the MAVLink Bridge
    1. Navigate into the `config/services` folder of this repository
    2. Run the following command:
    ```bash
    # Moves the mavlinkbridge.service to where services go
    $ cp mavlinkbridge.service /etc/systemd/system
    ```
    3. Run the following command:
    ```bash
    # Runs the service
    $ systemctl enable mavlinkbridge.service
    ```
5. Setup alias for connecting to Pixhawk
    1. Navigate into the `config` folder of this repository
    2. Run the following command:
    ```bash
    # Appends the alias command from dronerc onto the end of the .bashrc file
    $ cat dronerc >> ~/.bashrc
    ```

## Server
This can be run on any modern computer

Prerequisites:
* Python 3.5+
* Python 3.5+ pip

Steps:
1. pip3 install --user pipenv
2. Navigate into the `gcs` folder of this repository
3. Run the following command:
```bash
$ pipenv install
```


# Running the code

## Quads
First, set up the devices by doing 2 things:
1. Run the following command:
```bash
# Assuming you followed the setup instructions, this should exist
$ drone_console
```
2. Using a computer with access to Mission Planner, set the EKF Origin by right
   clicking on the map and selecting the option. This allows for clean takeoff.

In the quads folder, run:

```bash

$ python3 fly.py --name=bob --host=localhost --port=10000

```
> `-v` can be added to include additional information for debugging
Notes:
* Drone name must be unique to all other drone names.
* In the case that host, port, or name are not included, a command line interface will
  appear, and no connection to the server will be tried.
* If you are using the Gazebo simulation, specify with `--sim`

## Server
In the `gcs` folder, run:

```bash

$ python3 server.py --host=localhost --port=10000

```
> `-v` can be added to include additional information for debugging

## How to contribute
1. First make sure you are on the up to date `develop` branch.
```bash
$ git checkout develop
$ git pull
```
2. Create a branch to add your changes by running.
```bash
$ git checkout -b "branch_name"
```
> `branch_name` should follow the convention `feature/{feature_name}`, or
`hotfix/{fix_name}`
3. Make changes in your new branch.
4. Once changes are complete, go to GitHub and submit a "Pull Request". Fill in
   necessary information.
5. Once it has been reviewed by other members of the team, it can be accepted to
   the `develop` branch and the cycle continues...

> More info on the process
> [here](https://nvie.com/posts/a-successful-git-branching-model/) and
> [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

