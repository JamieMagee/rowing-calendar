import re
import os
from configparser import ConfigParser
import urllib.request as request
from datetime import datetime
import time

import praw
from lxml import html


def parse_british_rowing(webpage):
    global dates, events, web, locations
    tree = html.fromstring(webpage)
    dates.append([datetime.strptime(date, '%d/%m/%Y') for date in
                  tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/small/text()')])
    events.append(tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/a/text()'))
    web.append(['http://www.britishrowing.org' + site for site in tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/a/@href')])
    locations.append(['']*len(tree.xpath('//*[@id="britishrowing-calendar"]/tbody/tr[*]/td[2]/span[*]/a/text()')))


def parse_regatta_central(webpage):
    global dates, events, web, locations
    tree = html.fromstring(webpage)
    dates.append([datetime.strptime(date.replace(' \n      ', ''), '%A%m/%d/%y') for date in
                  tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[2]/text()')])
    events.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/text()'))
    web.append(['https://www.regattacentral.com' + site for site in
                tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/@href')])
    locations.append(tree.xpath(
        '//*[@id="tableResults"]/tbody/tr[*]/td[10]/a/text()|//*[@id="tableResults"]/tbody/tr[*]/td[10]/text()'))


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


rc, br = 'https://www.regattacentral.com/regattas/index.jsp?c=', 'http://www.britishrowing.org/competing/calendar'
countries = ['AU', 'CA', 'DE', 'IT', 'US']
while True:
    dates, events, web, locations = [], [], [], []

    for country in countries:
        print('[*] Fetching page...')
        page = request.urlopen(rc + country).read().decode('utf-8')
        print('[*] Parsing calendar...')
        parse_regatta_central(page)

    page = request.urlopen(br).read().decode('utf-8')
    print('[*] Parsing calendar...')
    parse_british_rowing(page)

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
    set_sidebar(out)
    print('[*] Sleeping...')
    time.sleep(43200)