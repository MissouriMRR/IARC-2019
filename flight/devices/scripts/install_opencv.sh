sudo apt-get install -y build-essential cmake unzip pkg-config
sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
sudo apt-get install -y libgtk-3-dev
sudo apt-get install -y libatlas-base-dev gfortran
sudo apt-get install -y python3-dev python3-pip python3-numpy python3-dbg

cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.4.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/3.4.4.zip

unzip opencv.zip
unzip opencv_contrib.zip
sudo rm -rf opencv
sudo rm -rf opencv_contrib
mv opencv-3.4.4 opencv
mv opencv_contrib-3.4.4 opencv_contrib

sudo -H pip3 install numpy
cd ~/opencv
mkdir build
cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D INSTALL_C_EXAMPLES=OFF \
	-D OPENCV_ENABLE_NONFREE=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D PYTHON_EXECUTABLE=$(which python3) \
	-D BUILD_EXAMPLES=ON ..

make -j$(nproc --all)
sudo make -j$(nproc --all) install
sudo ldconfig

cd /usr/local/python/cv2/python-3.6
sudo mv cv2.cpython-36m-x86_64-linux-gnu.so cv2.so
echo 'export PYTHONPATH="${PYTHONPATH}:/usr/local/python/cv2/python-3.6/"' >> ~/.bashrc
source ~/.bashrc