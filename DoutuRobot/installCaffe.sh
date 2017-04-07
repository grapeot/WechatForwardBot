#Dependencies
sudo apt-get install -y libprotobuf-dev libleveldb-dev libsnappy-dev libopencv-dev libhdf5-serial-dev protobuf-compiler
sudo apt-get install -y --no-install-recommends libboost-all-dev
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y python3-dev
sudo apt-get install -y libgoogle-glog-dev liblmdb-dev

# Caffe
git clone https://github.com/BVLC/caffe
cd caffe
cp Makefile.config.example Makefile.config
echo "ALSO NEED TO MODIFY THE FILE IF YOU WANT CPU_ONLY"
read

# Debian only
echo 'INCLUDE_DIRS := $(PYTHON_INCLUDE) /usr/local/include /usr/include/hdf5/serial/' >> Makefile.config
echo 'LIBRARY_DIRS := $(PYTHON_LIB) /usr/local/lib /usr/lib /usr/lib/x86_64-linux-gnu/hdf5/serial/' >> Makefile.config

make all -j4
