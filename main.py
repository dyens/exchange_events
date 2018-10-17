#!/usr/bin/env python

import argparse
import os
import re

from dateutil.parser import parse

from exchangelib import (DELEGATE, IMPERSONATION, Account, Configuration,
                         Credentials, EWSDateTime, EWSTimeZone)
from exchangelib.errors import (ErrorMailboxMoveInProgress,
                                ErrorMailboxStoreUnavailable)

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
parser.add_argument('start', help='start events YYYY-MM-DDThh:mm:ss', type=datetime_type)
parser.add_argument('end', help='end events YYYY-MM-DDThh:mm:ss', type=datetime_type)
parser.add_argument('emails', nargs='+', type=email_type)


def get_events(emails, start, end):
    credentials = Credentials(
        username=os.environ.get('EXCHANGE_USER'),
        password=os.environ.get('EXCHANGE_PASSWORD'))
    config = Configuration(server='ews.zoloto585.ru', credentials=credentials)

    tz = EWSTimeZone.timezone('Europe/Moscow')
    events = {}
    for email in emails:
        account = Account(
            primary_smtp_address=email,
            autodiscover=False,
            config=config,
            access_type=IMPERSONATION)
        start = EWSDateTime(start.year, start.month, start.day, start.hour,
                            start.minute, start.second)
        end = EWSDateTime(end.year, end.month, end.day, end.hour, end.minute,
                          end.second)
        evs = account.calendar.view(
            start=tz.localize(start), end=tz.localize(end))
        events[email] = (i for i in evs)
    return events


def print_event(event):
    attrs = [
        'is_cancelled', 'start', 'end', 'uid', 'subject', 'location',
        'organizer'
    ]

    for attr in attrs:
        print(attr, ': ', getattr(event, attr))
        print('------------------------------')
    attendees = [
        attendee.mailbox.email_address for attendee in event.required_attendees
    ]
    if attendees:
        print('ATTENDEES:')
        print(attendees)


if __name__ == '__main__':
    args = parser.parse_args()
    start=args.start
    end=args.end
    emails = args.emails
    events = get_events(emails, start, end)
    for email, event_list in events.items():
        print(email, ':')
        for ev in event_list:
            print_event(ev)
        print('------------------------------')
