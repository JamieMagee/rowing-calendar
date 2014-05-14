import urllib.request as request
from datetime import datetime
from configparser import ConfigParser
import os
import re
import time

from lxml import html
import praw


def parse_calendar(webpage):
    global dates, events, web, locations
    tree = html.fromstring(webpage)
    dates.append([datetime.strptime(date, '%d/%m/%Y') for date in
                  tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/small/text()')])
    events.append(tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/a/text()'))
    web.append(tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/a/@href'))
    locations.append(['']*len(tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/a/text()')))


def generate_table(dates, events, web, locations):
    out = '|**Race**|**Date**|**Venue**|\n|-|-|-|\n'
    for i in range(len(dates)):
        if (dates[i] - datetime.now()).days < 7:
            out += '|[' + events[i] + '](' + web[i] + ')|' + dates[i].strftime(
                '%d %B') + '|' + locations[i] + '|\n'
        else:
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

    sub = 'Rowing'
    settings = r.get_settings(sub)
    desc = settings['description']
    table = re.compile('\|.*\|', re.DOTALL)
    desc = (re.sub(table, out, desc))
    r.update_settings(r.get_subreddit(sub), description=desc)
    print('[*] Logging out...')
    r.clear_authentication()


def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

url = 'http://www.britishrowing.org/competing/calendar'
while True:
    dates, events, web, locations = [], [], [], []
    print('[*] Fetching page...')
    page = request.urlopen(url).read().decode('utf-8')
    print('[*] Parsing calendar...')
    parse_calendar(page)

    dates = flatten_list(dates)
    events = flatten_list(events)
    web = flatten_list(web)
    locations = flatten_list(locations)

    events_ = [points[1] for points in sorted(zip(dates, events, web, locations))]
    web_ = [points[2] for points in sorted(zip(dates, events, web, locations))]
    locations_ = [points[3] for points in sorted(zip(dates, events, web, locations))]
    dates_ = sorted(dates)

    print('[*] Generating table...')
    out = generate_table(dates_, events_, web_, locations_)
    print('[*] Updating sidebar...')
    print(out)
    #set_sidebar(out)
    print('[*] Sleeping...')
    time.sleep(86400)