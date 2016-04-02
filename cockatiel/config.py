import argparse

parser = argparse.ArgumentParser(description='Simple replicating file storage.')
parser.add_argument('--port', '-p', metavar='PORT', type=int, default=8080,
                    help='the port to listen on')
parser.add_argument('--host', '-H', metavar='HOST', type=str, default='0.0.0.0',
                    help='the IP address of the interface to listen on')
parser.add_argument('--storage', '-s', metavar='PATH', type=str, required=True,
                    help='Path to a directory to store the actual files in')

args = parser.parse_args()
