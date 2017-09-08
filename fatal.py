import sys

def fatal(message=None):
    if message:
        print(message)
    sys.exit(0)