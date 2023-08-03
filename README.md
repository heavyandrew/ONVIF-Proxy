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
You can run ONVIF-Proxy in docker and in systemd.
