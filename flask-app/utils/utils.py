import re
import requests

import logging
logging.basicConfig(level=logging.INFO)

from flask import Response

servicepatterns = {
    'device': ['device', 'device_service', 'services'],
    'services': ['device', 'device_service', 'services'],
    'analytics': ['analytics_service', 'Analytics', 'analytics'],
    'event': ['event_service', 'event', 'Events', 'Event'],
    'events': ['event_service', 'event', 'Events', 'Event'],
    'image': ['imaging_service', 'image_service', 'Imaging', 'imaging', 'image_services'],
    'imaging': ['imaging_service', 'image_service', 'Imaging', 'imaging', 'image_services'],
    'deviceio': ['deviceIO_service', 'deviceio_service', 'deviceio'],
    'media': ['media_service', 'Media', 'media'],
    'ptz': ['ptz', 'ptz_service', 'PTZ', 'ptz_services'],
    'ptz_services': ['ptz_services', 'ptz', 'ptz_service', 'PTZ'],
    'onvif_ext': ['onvif_ext'],
    'Subscription': ['Subscription'],
    'scdl_service': ['scdl_service']
}

def get_replace_template(cam_ip, cam_port, proxy_ip, proxy_port, auditory = None):
    if auditory == None:
        to_replace = r'http://{}:{}/'.format(proxy_ip, proxy_port)
    else:
        to_replace = r'http://{}:{}/{}/'.format(proxy_ip, proxy_port, auditory)
    dict = {
        r'http://{}:{}/'.format(cam_ip, cam_port): to_replace,
        r'http://{}:80/'.format(cam_ip): to_replace,
        r'http://{}/'.format(cam_ip): to_replace,
        r'http://255.255.255.255:80/': to_replace,
        r'http://255.255.255.255/': to_replace
    }
    return dict

'''
dic is dict where strings stored in template "what_replace: replace_with"
This function find all what_replace-strings in text and replace them with replace_with-strings
then return updated string
'''
def replace_all(message, dic):
    for i, j in dic.items():
        message = message.replace(i, j)
    return message

def replace_token(response, octet):
    if response == None:
        return ''
    else:
        token_as = [m.start() for m in re.finditer('token=', response)]
        token_arrow = [m.start() for m in re.finditer('Token>', response)]
        token_to_replace_as = []
        token_to_replace_arrow = []
        for i in token_as:
            token = response[i + 7:]
            token = token[: token.find('"')]
            token_to_replace_as.append(token)
        for i in range(len(token_arrow)):
            if i % 2 == 1:
                pass
            else:
                token = response[token_arrow[i] + 5:]
                token = token[: token.find('<')]
                if '<' in token:
                    token = token.replace('<', '')
                elif '>' in token:
                    token = token.replace('>', '')
                token_to_replace_arrow.append(token)
        token_to_replace_as = [*set(token_to_replace_as)]
        token_to_replace_arrow = [*set(token_to_replace_arrow)]
        split = response.find('Body') + 5
        first_part = response[:split]
        second_part = response[split:]
        response = first_part
        if len(token_to_replace_as) > 0:
            for what_replace in token_to_replace_as:
                if what_replace != '':
                    token_what_replace = 'token="' + what_replace + '"'
                    to_replace = 'token="' + octet + '_' + what_replace + '"'
                    second_part = second_part.replace(token_what_replace, to_replace)
        if len(token_to_replace_arrow) > 0:
            for what_replace in token_to_replace_arrow:
                if what_replace != '':
                    token_what_replace = 'Token>' + what_replace + '<'
                    to_replace = 'Token>' + octet + '_' + what_replace + '<'
                    second_part = second_part.replace(token_what_replace, to_replace)
        response = response + second_part
        return response

def return_soap(response):
    return Response(response, mimetype='application/soap+xml')

def return_ports_and_presets(input):
    first = int(input["ports"]["first"])
    presets = {}
    presets["default"] = input["ports"]["first"]
    for i in list(input["remote_controller"].keys()):
        preset = {}
        for j in list(input["remote_controller"][i].keys()):
            preset[j] = int(j) + first - 1
        presets[i] = preset
    return presets

'''

'''
def make_request(ip, port, service, data):
    service = 'http://' + ip + ':' + port + '/onvif/' + service
    try:
        response = requests.post(service, data = data, timeout = 3)
        return response
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return ''

'''

'''
def get_response(service, ip, port, body, direct, octet = None):
        response = make_request(ip, port, service, body)
        if direct == True:
            if response != '':
                return response.text
            else:
                return ''
        else:
            if response != '':
                if response.status_code != 500:
                    if response.status_code == 400 or response.text == '' or response.text.find('400 Bad Request') > 0 or response.text.find('404 Not Found') > 0 or response.text.find('404 File Not Found') > 0:
                        service = service.split('_')[0].lower()
                        if service.rfind('/') > -1:
                            to_list = service.split('/')
                            service = to_list[len(to_list) - 1].lower()
                            if service in list(servicepatterns.keys()):
                                service_length = len(servicepatterns[service])
                                iterrator = 0
                                while (response.status_code == 400 or response.text == '' or response.text.find('400 Bad Request') > 0 or response.text.find('404 Not Found') > 0 or response.text.find('404 File Not Found') > 0) and iterrator < service_length:
                                    response = make_request(ip, port, servicepatterns[service][iterrator], body)
                                    iterrator += 1
                            else:
                                logging.info('Нет сервиса {}'.format(service))
                        if response.status_code == 400 or response.text == '' or response.text.find('400 Bad Request') > 0 or response.text.find('404 Not Found') > 0 or response.text.find('404 File Not Found') > 0:
                            return ''
                        else:
                            return response.text
                    else:
                        return response.text
                else:
                    return ''
            else:
                return ''