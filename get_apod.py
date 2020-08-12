from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.error
import os
import time
import requests
import datetime

YEAR=19
#generate a date range in format "200812"
def date_range(start, end, step=1, format="%y%m%d"):
    strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
    days = (strptime(end, format) - strptime(start, format)).days
    return [strftime(strptime(start, format) + datetime.timedelta(i), format) for i in range(0, days, step)]

os.makedirs('./img/{}/'.format(YEAR), exist_ok=True)
os.makedirs('./description/{}/'.format(YEAR), exist_ok=True)

def crawl(date):
    print('Opening {}'.format(date))
    url = 'https://apod.nasa.gov/apod/ap{}.html'.format(date)
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, features='lxml')
    #get_title
    title = soup.title.string.strip()
    #get_image_url
    centers = soup.find_all('center')
    try:
        image_url = "https://apod.nasa.gov/apod/" + centers[0].find_all('p')[1].a.get('href')
        print(image_url)
        image_type = image_url.split('.')[-1]
    except AttributeError: #No image in this page
        image_type = 'none'
    except urllib.error.HTTPError: #This page may not exist
        print("HTTPError for {}".format(date))
        return
    #get_content
    with open('./description/{}/{}.txt'.format(YEAR, date),'w' ,encoding='utf-8') as f:
        f.write('{}\nTitle:{}\n'.format(date, title))
        for text in [p.get_text() for p in soup.find_all('p')]:
            if 'Explanation:' in text:
                f.write(text.replace('\n', ' ').strip())
    #make_list
    with open('./list{}.txt'.format(YEAR),'a',encoding='utf-8') as f:
        f.write("{}\t{}\n".format(date, title))
    #get_image
    print('Getting images of {}'.format(date))
    if image_type != 'none':
        r = requests.get(image_url, stream=True)    #download the picture
        with open('./img/{}/{} {}.{}'.format(YEAR, date, 
        (title.split('-'))[1].replace(':','-').replace('/',' ').strip(), image_type), 'wb') as f:
            for chunk in r.iter_content(chunk_size=32):
                f.write(chunk)
    else:
        print("No image of {}".format(date))
    print('Done - {} !'.format(date))

for date in date_range('{}0101'.format(YEAR),'{}0101'.format(YEAR+1)):
    crawl(date)

print('Done!')