# IoT BASC Project 🚀  
An IoT system using two Raspberry Pi boards to control sensors, store sensor data in a database, and display real-time data on Node-RED.

## 🔧 Features
- Connect and control sensors using two Raspberry Pi devices.
- Store sensor data in a database.
- Visualize and control devices through Node-RED.
- Support communication via **MQTT** and **HTTP** protocols.
- Monitor and manage system remotely.

### ✅ Grove Sensor Setup
- Grove:
  curl -sL http://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s -
- DHT:
  pip3 install seeed-python-dht
- config rasp:
  sudo raspi-config
- NODE RED:
  curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash
  sudo apt-get install -y nodejs
  node -v
