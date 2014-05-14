import urllib.request as request
import time
import re
import os
from configparser import ConfigParser

from bs4 import BeautifulSoup
import praw


def parse_calendar(webpage):
    soup = BeautifulSoup(webpage)
    dates = [el.text for el in soup.find_all('td', {'height': '25'})]
    events = [[b.text for b in el.find_all('b')] for el in soup.find_all('td', {'bgcolor': 'EEEECC'})]
    # Web needs work to align with events list
    #web = [[a.text for a in el.find_all(href=re.compile('http'))] for el in soup.find_all('td', {'bgcolor': 'EEEECC'})]
    return dates, events


def generate_table(dates, events):
    out = '| **Race** | **Date** |\n|-|-|\n'
    for i in range(len(dates)):
        for j in range(len(events[i])):
            try:
                out += '| ' + events[i][j] + ' | ' + time.strftime('%B %d',
                                                                   time.strptime(dates[i], '%A, %B %d, %Y')) + ' |\n'
            except ValueError:
                out += '| ' + events[i][j] + ' | ' + dates[i][:-6:] + ' |\n'
    return out


def set_sidebar(out):
    r = praw.Reddit('/r/rowing sidebar updater')

    if os.path.isfile('settings.cfg'):
        config = ConfigParser()
        config.read('settings.cfg')
        username = config.get('auth', 'username')
        password = config.get('auth', 'password')
    else:
        username = os.environ['REDDIT_USERNAME']
        password = os.environ['REDDIT_PASSWORD']

    print('[*] Logging in as %s...' % username)
    r.login(username, password)
    print('[*] Login successful...')

    sub = 'Jammie1'
    settings = r.get_settings(sub)
    desc = settings['description']
    table = re.compile('\|.*\|', re.DOTALL)
    desc = (re.sub(table, out, desc))
    r.update_settings(r.get_subreddit(sub), description=desc)
    print('[*] Logging out...')
    r.clear_authentication()


url = 'http://www.row2k.com/calendar/index.cfm?type=week'
while True:
    print('[*] Fetching page...')
    page = request.urlopen(url).read().decode('utf-8')
    print('[*] Parsing calendar...')
    dates, events = parse_calendar(page)
    print('[*] Generating table...')
    out = generate_table(dates, events)
    print('[*] Updating sidebar...')
    set_sidebar(out)
    print('[*] Sleeping...')
    time.sleep(10)