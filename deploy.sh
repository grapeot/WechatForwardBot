# Install mongodb and python
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
# We assume it's 16.04. Check out https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/ for other versions.
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo apt-get install -y python3 python3-pip

# Install python dependencies
sudo pip3 install -r requirements.txt
