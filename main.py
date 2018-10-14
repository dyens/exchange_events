from exchangelib import DELEGATE, Account, Credentials, Configuration
from exchangelib import EWSTimeZone
from exchangelib import EWSDateTime
from exchangelib import IMPERSONATION

from exchangelib.errors import ErrorMailboxMoveInProgress
from exchangelib.errors import ErrorMailboxStoreUnavailable

import argparse
import re
from dateutil.parser import parse

ereg = r'[^@]+@[^@]+\.[^@]+'


def email_type(string):
    if re.match(ereg, string):
        return string
    else:
        raise argparse.ArgumentTypeError('Wrong email')


def datetime_type(string):
    try:
        return parse(string)
    except ValueError:
        raise argparse.ArgumentTypeError('Wrong datetime')


parser = argparse.ArgumentParser(description='Exchange events')
parser.add_argument('start', help='start events', type=datetime_type)
parser.add_argument('end', help='end events', type=datetime_type)
parser.add_argument('emails', nargs='+', type=email_type)

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
