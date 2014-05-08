from lxml import html
import urllib.request as request
from datetime import datetime
import time
import praw
import re
import os
from configparser import ConfigParser


def parse_calendar(webpage):
    tree = html.fromstring(webpage)
    dates = [date.replace(' \n      ', '') for date in tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[2]/text()')]
    events = tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/text()')
    web = tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/@href')
    locations = tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[10]/a/text()')
    locationsweb = tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[10]/a/@href')
    return dates, events, web, locations, locationsweb


def generate_table(dates, events, web, locations, locationsweb):
    out = '| **Race** | **Date** | **Venue** |\n|-|-|-|\n'
    for i in range(len(dates)):
        if (datetime.strptime(dates[i], '%A%m/%d/%y') - datetime.now()).days < 7:
            out += '| [' + events[i] + '](https://www.regattacentral.com' + web[i] + ') | ' + datetime.strptime(dates[i], '%A%m/%d/%y').strftime('%d %B') + ' | [' + locations[i] + '](https://www.regattacentral.com' + locationsweb[i] + ') |\n'
        else: return out


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


url = 'https://www.regattacentral.com/regattas/index.jsp?c='
while True:
    print('[*] Fetching page...')
    page = request.urlopen(url).read().decode('utf-8')
    print('[*] Parsing calendar...')
    dates, events, web, locations, locationsweb = parse_calendar(page)
    print('[*] Generating table...')
    out = generate_table(dates, events, web, locations, locationsweb)
    print('[*] Updating sidebar...')
    set_sidebar(out)
    print('[*] Sleeping...')
    time.sleep(10)