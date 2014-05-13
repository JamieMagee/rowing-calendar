from lxml import html
import urllib.request as request
from datetime import datetime
import time
import praw
import re
import os
from configparser import ConfigParser


def parse_calendar(webpage):
    global dates, events, web, locations, locationsweb
    tree = html.fromstring(webpage)
    dates.append([datetime.strptime(date.replace(' \n      ', ''), '%A%m/%d/%y') for date in
                  tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[2]/text()')])
    events.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/text()'))
    web.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/@href'))
    locations.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[10]/a/text()|//*[@id="tableResults"]/tbody/tr[*]/td[10]/text()'))
    locationsweb.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[10]/a/@href'))


def generate_table(dates, events, web, locations, locationsweb):
    out = '|**Race**|**Date**|**Venue**|\n|-|-|-|\n'
    for i in range(len(dates)):
        if (dates[i] - datetime.now()).days < 7:
            out += '|[' + events[i] + '](https://www.regattacentral.com' + web[i] + ')|' + dates[i].strftime(
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


url = 'https://www.regattacentral.com/regattas/index.jsp?c='
countries = ['AU', 'CA', 'DE', 'IT', 'US']
while True:
    dates, events, web, locations, locationsweb = [], [], [], [], []
    for country in countries:
        print('[*] Fetching page...')
        page = request.urlopen(url + country).read().decode('utf-8')
        print('[*] Parsing calendar...')
        parse_calendar(page)

    dates = flatten_list(dates)
    events = flatten_list(events)
    web = flatten_list(web)
    locations = flatten_list(locations)
    locationsweb = flatten_list(locationsweb)
    events_ = [points[1] for points in sorted(zip(dates, events, web, locations, locationsweb))]
    web_ = [points[2] for points in sorted(zip(dates, events, web, locations, locationsweb))]
    locations_ = [points[3] for points in sorted(zip(dates, events, web, locations, locationsweb))]
    locationsweb_ = [points[4] for points in sorted(zip(dates, events, web, locations, locationsweb))]
    dates_ = sorted(dates)

    print('[*] Generating table...')
    out = generate_table(dates_, events_, web_, locations_, locationsweb_)
    print('[*] Updating sidebar...')
    set_sidebar(out)
    print('[*] Sleeping...')
    time.sleep(86400)