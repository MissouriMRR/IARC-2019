# Installation Guide
## Ubuntu 18.04
### Install necessary packages
First, make sure Ubuntu is up-to-date:
```
sudo apt-get update
sudo apt-get upgrade
```
Then install the `wget` utility. This will be used to download the install script.
```
sudo apt-get install wget
```
### Installing the Realsense SDK
#### Run the install script.
To download an run a script which will perform all necessary actions to install the Intel Realsense SDK 2.0, run the following set of commands in your terminal:

```
cd ~
mkdir scripts
cd scripts
wget -w0 https://raw.githubusercontent.com/MissouriMRR/IARC-2019/feature/realsense/flight/devices/scripts/install_realsense.sh
sudo chmod +x install_realsense.sh
./install_realsense.sh
```
The executed script is a convenient wrapper for the [official installation guide commands](https://realsense.intel.com/sdk-2/#install). If this script no longer seems to work, check the aforementioned link for new installation instructions.

### Building the Python module
#### Boost Python Setup
Since this module uses [Boost Python](https://www.boost.org/doc/libs/1_69_0/libs/python/doc/html/index.html) to create its bindings, you'll need to install the all, or the relevant portions of, `Boost`. Luckily for us, the version of `Boost` provided by new editions of Ubuntu is sufficient for compilation:
```
sudo apt-get install libboost-all-dev
```
### Install OpenCV 3.4.4
Similar to before, here is a script which will perform the setup and installation required for OpenCV 3.4.4 alongside Python 3 bindings:
```
cd ~/scripts
wget -w0 https://raw.githubusercontent.com/MissouriMRR/IARC-2019/feature/realsense/flight/devices/scripts/install_opencv.sh
sudo chmod +x install_opencv.sh
./install_opencv.sh
```

## Note

This guide was updated on March 8th, 2019.


