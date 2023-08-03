import argparse
from processor import Processor

def main():
    parser = argparse.ArgumentParser(description='Insert port, conf_path, cam_num, sub_instance_list_path')
    parser.add_argument(
        '--ip',
        type=str,
        help='IP of host'
    )
    parser.add_argument(
        '--port',
        type=str,
        help='Port for instance'
    )
    parser.add_argument(
        '--conf_path',
        type=str,
        help='Path to conf file'
    )
    parser.add_argument(
        '--cam_num',
        type=str,
        help='Camera number (1, 2, 3, ...)'
    )
    input = parser.parse_args()

    app = Processor("API_", input.ip, input.port, input.conf_path, input.cam_num)
    app.run()

#python .\onvif-proxy\flask-app\main.py --ip 192.168.1.86 --port 80 --conf_path "C:\Users\andre\PycharmProjects\OnvifProxyGit\onvif-proxy\flask-app\confs\director.json" --cam_num 1

if __name__ == "__main__":
    main()