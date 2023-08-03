import os
import json

import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask, request, jsonify
from flasgger import Swagger

from utils.utils import *

HTTP_METHODS = ['POST']

class Processor():
    def __init__(self, name, ip, port, conf_path, cam_num):
        self.app = Flask(name)
        self.conf_path = conf_path
        self.ip = ip
        self.port = port
        self.cameras = json.load(open(conf_path))
        self.cam_num = cam_num

        swagger = Swagger(self.app, template_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "utils", 'swagger.yml'))

        @self.app.route("/preset/<location>", methods=HTTP_METHODS)
        def change_location(location):
            if preset not in list(self.cameras["remote_controller"].keys()):
                return Response(status = 400)
            else:
                self.cameras["default"] = location
                with open(self.conf_path, 'w') as j:
                    json.dump(self.cameras, j)
                ok = True
                for i in range(int(self.cameras["ports"]["first"]), int(self.cameras["ports"]["last"]) + 1):
                    if i != int(self.port):
                        response = requests.get('http://{}:{}/update/{}'.format(self.ip, i, location), timeout=5)
                        logging.info("{} - result:{}".format(i, response.status_code))
                        if response.status_code != 200:
                            ok = False
                if ok == True:
                    return Response(status=200)
                else:
                    return Response(status=500)

        @self.app.route("/location/<preset>", methods=HTTP_METHODS)
        def change_preset(preset):
            if preset not in list(self.cameras["remote_controller"].keys()):
                return Response(status = 400)
            else:
                self.cameras["default"] = preset
                with open(self.conf_path, 'w') as j:
                    json.dump(self.cameras, j)
                return jsonify({"number": len(list(self.cameras["remote_controller"][self.cameras["default"]].keys()))})

        @self.app.route("/update/<location>", methods=HTTP_METHODS)
        def update_instance(location):
            self.cameras["default"] = location
            return Response(status=200)

        @self.app.route("/<number>/onvif/<service>", methods=HTTP_METHODS)
        @self.app.route("/onvif/<service>", methods=HTTP_METHODS)
        def auditory(number = None, service = None):
            if number != None:
                paradigm = "auditories"
                auditory = str(number)
                ips = list(self.cameras[paradigm][auditory].keys())
                needed_ip = ips[0]
                direct = False
                logging.info('Аудитория {}'.format(number))
            else:
                paradigm = 'remote_controller'
                auditory = str(self.cameras["default"])
                cam_num = self.cam_num
                ips = list(self.cameras[paradigm][auditory].keys())
                needed_ip = cam_num
                direct = True
                logging.info('Аудитория {}'.format(number))
                logging.info('Камера {}'.format(cam_num))

            ip = self.cameras[paradigm][auditory][needed_ip]['ip']
            port = self.cameras[paradigm][auditory][needed_ip]['port']

            body = request.data.decode()

            if body.find('GetCapabilities') > 0 or body.find('GetServices') > 0:
                cam_ip = ip
                cam_port = port
                response = get_response('device_service',
                                        ip,
                                        port,
                                        body,
                                        direct)
                if paradigm == "auditories":
                    for i in range(1, len(ips)):
                        possbile_response = get_response('device_service',
                                                         self.cameras[paradigm][auditory][ips[i]]['ip'],
                                                         self.cameras[paradigm][auditory][ips[i]]['port'],
                                                         body,
                                                         direct)
                        if len(possbile_response) > len(response):
                            response = possbile_response
                            cam_ip = self.cameras[paradigm][auditory][ips[i]]['ip']
                            cam_port = self.cameras[paradigm][auditory][ips[i]]['port']
                response = replace_all(response,
                                       get_replace_template(cam_ip,
                                                            cam_port,
                                                            self.ip,
                                                            self.port,
                                                            number))
                response = response.encode()
            else:
                header = str(request.headers.get('Content-Type'))
                action = header[header.find('action') + 8:]
                action = action[:action.find('"')]
                if len(header) > 35:
                    logging.info('Сервис {}, action {}'.format(service, action))

                if body.find('GetScopes') > 0:
                    response = get_response(service,
                                            ip,
                                            port,
                                            body,
                                            direct)
                    if paradigm == "auditories":
                        for i in range(1, len(ips)):
                            possbile_response = get_response('device_service',
                                                             self.cameras[paradigm][auditory][ips[i]]['ip'],
                                                             self.cameras[paradigm][auditory][ips[i]]['port'],
                                                             body,
                                                             direct)

                            if len(possbile_response) > len(response):
                                response = possbile_response

                    if response.find('/location/') > 0 and response.find('/location/') != response.find(
                            '/location/country'):
                        response = response.replace('/location/', '/location/{}'.format(auditory))
                    elif response.find(':location:') > 0:
                        location = response[response.find(':location:') + 10:]
                        location = location[:location.find('<')]
                        response = response.replace(location, '{}'.format(auditory))
                    elif response.find('/location/') > 0:
                        location = response[response.find('/location/') + 10:]
                        location = location[:location.find('<')]
                        response = response.replace(location, '{}'.format(auditory))

                elif body.find('GetProfiles') > 0 or body.find('GetVideoSources') > 0:
                    if body.find('GetProfiles') > 0:
                        responseWord = 'GetProfilesResponse'
                        responseWordEnd = 'Profiles>'
                    else:
                        responseWord = 'GetVideoSourcesResponse'
                        responseWordEnd = 'VideoSources>'
                    response = get_response(service,
                                            ip,
                                            port,
                                            body,
                                            direct)
                    response = replace_token(response, needed_ip)
                    if paradigm == "auditories":
                        add_responses = []
                        add_responses.append(response)
                        for i in range(1, len(ips)):
                            add_response = get_response(service,
                                                        self.cameras[paradigm][auditory][ips[i]]['ip'],
                                                        self.cameras[paradigm][auditory][ips[i]]['port'],
                                                        body,
                                                        direct,
                                                        ips[i])
                            add_response = replace_token(add_response, ips[i])
                            add_responses.append(add_response)
                        first_and_last = False

                        for message in add_responses:
                            if message != "":
                                if first_and_last == False:
                                    first_part = message[:message.rfind(responseWord)]
                                    first_part = first_part[:first_part.rfind('>') + 1]
                                    second_part = message[message.rfind(responseWordEnd):]
                                    second_part = second_part[second_part.find('<'):]
                                    response = first_part
                                    first_and_last = True
                                else:
                                    add_response = message[message.find(responseWord) + len(responseWord) + 1:message.rfind(responseWord)]
                                    add_response = add_response[:add_response.rfind('>') + 1]
                                    response = response + add_response
                        response = response + second_part

                        response = re.sub("^\s+|\n|\r|\s+$", '', response)
                elif (body.rfind('Token') - 8) != body.rfind('UsernameToken') and body.rfind('Token') > -1 and body.rfind('UsernameToken') > -1:
                    token_with_ip = body[body.rfind('Token>', 0, body.rfind('Token>') - 7) + 6:]
                    token_with_ip = token_with_ip[: token_with_ip.find('<')]
                    if len(token_with_ip) < 3:
                        token_with_ip = body[:len(body) - len(body[body.rfind('Token>', 0, body.rfind('Token>') - 7) + 6:]) - 7]
                        token_with_ip = token_with_ip[token_with_ip.rfind('Token>',0,token_with_ip.rfind('Token>') - 7) + 6:]
                        token_with_ip = token_with_ip[: token_with_ip.find('<')]

                    octet = token_with_ip.split('_')[0]
                    token_without_ip = token_with_ip[len(octet) + 1:]

                    body = body.replace(token_with_ip, token_without_ip)
                    if body.find('GetVideoEncoderConfigurationOptions') > 0 or body.find('GetMetadataConfigurationOptions') > 0:
                        if body.find('ConfigurationToken>') > 0:
                            token_with_ip = body[body.find('ConfigurationToken>') + 19:]
                            token_with_ip = token_with_ip[: token_with_ip.find('<')]
                            token_without_ip = token_with_ip[len(octet) + 1:]
                            body = body.replace(token_with_ip, token_without_ip)

                    response = get_response(service,
                                            self.cameras[paradigm][auditory][octet]['ip'],
                                            self.cameras[paradigm][auditory][octet]['port'],
                                            body,
                                            direct)
                    if self.cameras[paradigm][auditory][octet]['streamuri'] != '':
                        if body.find('GetStreamUri') > 0:
                            old_streamuri = response[response.find('>rtsp') + 1:]
                            old_streamuri = old_streamuri[: old_streamuri.find('<')]
                            streamuri = self.cameras[paradigm][auditory][octet]['streamuri']
                            response = response.replace(old_streamuri, streamuri)

                    response = replace_token(response, octet)

                    if body.find('GetSnapshotUri'):
                        if response.find('255.255.255.255:80'):
                            response = replace_all(response,
                                                   get_replace_template('255.255.255.255',
                                                                        '80',
                                                                        self.cameras[paradigm][auditory][octet]['ip'],
                                                                        self.cameras[paradigm][auditory][octet]['port']
                                                                        ))
                else:
                    response = get_response(service,
                                            ip,
                                            port,
                                            body,
                                            False)
                    response = replace_token(response, needed_ip)
                response = re.sub("^\s+|\n|\r|\s+$", '', response)

            return return_soap(response)

    def run(self):
        self.app.run(host='0.0.0.0', port=int(self.port), debug=True)
