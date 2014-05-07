from bs4 import BeautifulSoup
import urllib.request as request
import time


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
            except:
                out += '| ' + events[i][j] + ' | ' + dates[i][:-6:] + ' |\n'
    return out


url = 'http://www.row2k.com/calendar/index.cfm?type=week'
page = request.urlopen(url).read().decode('utf-8')
dates, events = parse_calendar(page)
out = generate_table(dates, events)
print(out)