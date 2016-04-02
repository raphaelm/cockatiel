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

# parsing is done in server.run(), the parsed arguments are assigned to this
# variable. This "monkey-patching" approach makes the life of functional_tests.utils
# a lot easier.
args = None
