# -*- coding: utf-8 -*-
import time
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from project_database import get_or_create_advert, get_unpublished_adverts

header = Headers(
    headers=True  # generate misc headers
)


def send_message_to_telegram(text: str):
    requests.post(
        url='https://api.telegram.org/bot2080371506:AAG-RM5hgb8gI-IPPf5IsVqutHVq09-CMDk/sendMessage',
        json={
            'chat_id': '663427704',
            'text': text,
            'parse_mode': 'html'
        }
    )


def get_page(url: str):
    res = requests.get(
        url=url,
        headers=header.generate()
    )
    return res.content


def parse_adv_div(soup: BeautifulSoup):
    title = soup.find('h6').text
    price = soup.find('p', {'data-testid': 'ad-price'}).text.replace('Договорная', '')
    date = soup.find('p', {'data-testid': 'location-date'}).text
    url = ('https://www.olx.uz' + soup.select('a')[0]['href']) if len(soup.select('a')) else ''
    print('url: ', url)
    return {'title': title, 'price': price, 'date': date, 'url': url}


def parse_page_adverts(url):
    page_content = get_page(url)
    soup = BeautifulSoup(page_content, 'html5lib')
    counter = 0

    for adv_div in soup.findAll("div", {"data-cy": "l-card"}):
        counter += 1
        print('adv_div', counter)
        adv_info = parse_adv_div(adv_div)
        print(adv_info)
        get_or_create_advert(**adv_info)


def publish_unpublished_adverts():
    adverts, sess = get_unpublished_adverts()
    for adv in adverts:
        send_message_to_telegram(
            f'<b>{adv.name}</b>\n\n<b>{adv.price}</b>\n\n{adv.date}\n\n{adv.url}'
        )

        adv.published = True
        sess.add(adv)
        sess.commit()
        time.sleep(1)


while True:
    print("SLEEPING")

    time.sleep(5)
    try:
        publish_unpublished_adverts()

        parse_page_adverts(
            'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/nukus/'
        )
        time.sleep(2)

        parse_page_adverts(
            'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/nukus/?page=2'
        )
        time.sleep(2)

        parse_page_adverts(
            'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/nukus/?page=3'
        )
    except Exception as exp:
        send_message_to_telegram("ERROR: " + str(exp))
