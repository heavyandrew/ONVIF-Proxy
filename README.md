# ONVIF-Proxy
## Description
ONVIF-Proxy is Python Flask-based proxy-server which is made to redirect ONVIF-messages. Functionalities which it provides are:
1. Grouping devices to collections
2. Replacing RTSP-URLs with those which are in config-file

There are two types of collections:
1. Dynamic collection which is available through http://<ip>:port>/onvif/device_service and can be switched to another fro config
2. Static collection which is available through http://<ip>:<port>/<collection>/onvif/device_service

## How it works
ONVIF-Proxy doesnot emulate ONVIF-device, if all devices in collection are off, it will return nothing.

Logically, dynamic collection is represented on picture below:
![NewOnvifProxy drawio (1)](https://github.com/heavyandrew/ONVIF-Proxy/assets/76702752/7e02f233-8f32-4829-a3bf-04045d2791a8)
So, if you have several collections with the same number of devices, running ONVIF-Proxy in dynamic mode means running several instances. Each instance points to specific number of device in dynamic collections. Moreover, it can point to all devices in collection, so can work in static mode.

Logically, static collection is represented on picture below:
![OldOnvifProxy drawio (1)](https://github.com/heavyandrew/ONVIF-Proxy/assets/76702752/4185eded-b6f3-4656-b2b2-2a5d600cb1b3)
So, ONVIF-Proxy recieve ONVIF-request, change something in it if there is a need and send it to devices. Then it combines ONVIF-responses and return resulted message to ONVIF-client.
## How to run
### conf.json - defenitions
1. **default** - dynamic collection that will be chosen when server is started
2. **ports** - when you run several instances and want to choose another dynamic collection, you will send change request to one instance and it will resend this request to another. In ports dict you define group of ports which are listened by instances and where the first instance will send request to change. So, if you run 7 instances on ports 9001 to 9007, you define
```
"ports": {
    "first": "9001",
    "last": "9007"
  },
```
3. **remote_controller** - is a dict for dynamic collections, **auditories** - is for static ones. Both dicts are filled with collections which names can consist of letters and digits.
4. Number of devices in collection can be from 0 to whatever you want. For each device **ip** and **port** is mandatory, **streamuri** is optional.
5. Example.

You can run ONVIF-Proxy in docker and in systemd.
### Systemd
1. Clone repo
2. Install Python 3.9
3. Install virtualenv
```
pip3 install virtualenv
```
4. Create virtual environment
```
python3 -m venv onvif
```
5. Activate and install packeges from requirements.txt
```
. onvif/bin/activate && pip install -r requirements.txt
```
6. Fill paths in .service file, copy it to **/etc/systemd/system** and run.
```
nano onvif-proxy.service
```
```
cp onvif-proxy.service /etc/systemd/system
```
```
sudo systemd start onvif-proxy.service
```
```
sudo systemd enable onvif-proxy.service
```
### Docker-compose
1. Clone repo
2. Install docker-compose
3. 
