from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import time
import multiprocessing as mp
import requests
import datetime
year=16
def date_range(start, end, step=1, format="%y%m%d"):
    strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
    days = (strptime(end, format) - strptime(start, format)).days
    return [strftime(strptime(start, format) + datetime.timedelta(i), format) for i in range(0, days, step)]

os.makedirs('./img/{}/'.format(year), exist_ok=True)
os.makedirs('./explaination/{}/'.format(year), exist_ok=True)
def crawl(date):
    print('Begin opening {}'.format(date))
    url = 'https://apod.nasa.gov/apod/ap{}.html'.format(date)
    response = urlopen(url)
    #time.sleep(0.1)
    html = response.read()
    soup = BeautifulSoup(html, features='lxml')
    #get_title
    title = soup.title.string.strip()
    #get_image_url
    centers = soup.find_all('center')
    try:
        image_url = "https://apod.nasa.gov/apod/" + centers[0].find_all('p')[1].a.get('href')
        print(image_url)
        image_type = image_url[-3:]
    except AttributeError:
        image_type = 'nnnnnn'
    #get_content
    with open('./explaination/{}/{}.txt'.format(year, date),'w' ,encoding='utf-8') as f:
        f.write('{}\nTitle:{}\n'.format(date, title))
        for text in [p.get_text() for p in soup.find_all('p')]:
            if 'Explanation:' in text:
                f.write(text.replace('\n', ' ').strip())
    #make_list
    with open('./list{}.txt'.format(year),'a',encoding='utf-8') as f:
        f.write("{}\t{}\n".format(date, title))
    #get_image
    print('Begin getting images of {}'.format(date))
    if image_type in ['jpg', 'png', 'gif', 'bmp']:
        r = requests.get(image_url, stream=True)    # stream loading
        with open('./img/{}/{} {}.{}'.format(year, date, (
            title.split('-'))[1].replace(':','-').replace('/',' ').strip(), image_type), 'wb') as f:
            for chunk in r.iter_content(chunk_size=32):
                f.write(chunk)
    else:
        print("No image of {}".format(date))
    print('Done - {}'.format(date))

for date in date_range('{}0101'.format(year),'{}0101'.format(year+1)):
    crawl(date)

print('Done!')