from sys import stderr
from termcolor import colored

def log_error(message):
    message = colored(message, 'red')
    print(message, file=stderr, flush=True)