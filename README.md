# ONVIF-Proxy

ONVIF-Proxy is Flask-based proxy-server which is made to redirect ONVIF-messages. Functionalities which it provides are:
1. Grouping devices to collections
2. Replacing RTSP-URLs with those which are in config-file

There are two types of collections:
1. Dynamic collection which is available through http://<ip>:port>/onvif/device_service and can be switched to another fro config
2. Static collection which is available through http://<ip>:<port>/<collection>/onvif/device_service

Logically, dynamic collection is represented on picture below:
![NewOnvifProxy drawio (1)](https://github.com/heavyandrew/ONVIF-Proxy/assets/76702752/7e02f233-8f32-4829-a3bf-04045d2791a8)
So, if you want to unite
