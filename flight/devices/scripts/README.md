# Installation Guide
## Ubuntu 18.04
### Section <insert section here>: Installing the Realsense SDK
#### Run the install script.
To download an run a script which will perform all necessary actions to install the Intel Realsense SDK 2.0, run the following set of commands in
your terminal:

```
cd ~
mkdir scripts
cd scripts
wget -w0 https://raw.githubusercontent.com/MissouriMRR/IARC-2019/feature/realsense/flight/devices/scripts/install_realsense.sh
sudo chmod +x install_realsense.sh
./install_realsense.sh
```
The executed script is a convenient wrapper for the [official installation guide commands](https://realsense.intel.com/sdk-2/#install). If this script no longer seems to work, check the aforementioned link for new installation instructions.

## Note

This guide was updated on March 8th, 2019.


