import urllib.request as request
from datetime import datetime

from lxml import html


def parse_calendar(webpage):
    global dates, events, web, locations, locationsweb
    tree = html.fromstring(webpage)
    dates.append([datetime.strptime(date.replace(' \n      ', ''), '%A%m/%d/%y') for date in
                  tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[2]/text()')])
    events.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/text()'))
    web.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[4]/a/@href'))
    locations.append(tree.xpath(
        '//*[@id="tableResults"]/tbody/tr[*]/td[10]/a/text()|//*[@id="tableResults"]/tbody/tr[*]/td[10]/text()'))
    locationsweb.append(tree.xpath('//*[@id="tableResults"]/tbody/tr[*]/td[10]/a/@href'))


url = 'https://www.regattacentral.com/regattas/index.jsp?c='
countries = ['AU', 'CA', 'DE', 'IT', 'US']

for country in countries:
    print('[*] Fetching page...')
    page = request.urlopen(url + country).read().decode('utf-8')
    print('[*] Parsing calendar...')
    parse_calendar(page)

