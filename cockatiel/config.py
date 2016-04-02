import argparse

parser = argparse.ArgumentParser(
    description='Simple replicating file storage.')
parser.add_argument('--port', '-p', metavar='PORT', type=int, default=8080,
                    help='the port to listen on')
parser.add_argument('--host', '-H', metavar='HOST', type=str,
                    default='0.0.0.0',
                    help='the IP address of the interface to listen on')
parser.add_argument('--storage', metavar='PATH', type=str, required=True,
                    help='Path to a directory to store the actual files in')
parser.add_argument('--queue', metavar='PATH', type=str, required=True,
                    help='Path to a directory to store the retry queue')
parser.add_argument('--url', metavar='URL', type=str, default='',
                    help='The URL this service is publicly reachable at, e.g. '
                         'http://10.1.1.1:8123/foo or https://mydomain.com/media, '
                         'depending on your reverse proxy setup.')
parser.add_argument('--node', metavar='URL', action='append',
                    help='Specify this option once for every other node on your cluster. '
                         'Every value should be a valid URL prefix like http://10.1.1.2:8012')

# TODO: Provide a way to include the own node name in --node but than disable it again
# via some kind of --whoami flag. This will make it easier for configuration management
# to instrument this software.

# parsing is done in server.run(), the parsed arguments are assigned to this
# variable. This "monkey-patching" approach makes the life of functional_tests.utils
# a lot easier.
args = None
