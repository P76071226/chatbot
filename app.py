#app.py
from flask import Flask, request, abort
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('UqiPibRtIFK0Nbi91uGgPEnSbftJ4bFII1mR+J2cvxUEH95lu9ezLHCBcNtRWGCUw4pqtXA3v7IzAMQULKjxlVRJxcMPrJ+4Ozk297VxgLD61phlxjKGAO8nicbZfHwseYjOBQhYOTQkbaaXtbPdnQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5f6b30cf568db2d744cc0d9b30ba5958')

# =========

import requests
from bs4 import BeautifulSoup

results = {}

url = 'https://www.cwb.gov.tw/V7/forecast/taiwan/Taoyuan_City.htm'
r = requests.get(url)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, "html5lib")
menu1 = soup.find('select', {"name": "menu1"}).find_all('option')

def f1(select):
    
    results = {}

    for option in menu1[:2]:
        city = option['value']

        url = 'https://www.cwb.gov.tw/V7/forecast/taiwan/%s' % city
        r = requests.get(url)
        r.encoding = 'utf-8'

        soup = BeautifulSoup(r.text, "html5lib")

        city = option.text
        results.setdefault(city, [])

        for i, tr in enumerate(soup.find(class_="FcstBoxTable01").find('tbody').find_all('tr')):

            result = {}
            for i, td in enumerate(tr.find_all('td')):
                if i == 0:
                    result['溫度'] = td.text
                if i == 2:
                    result['舒適度'] = td.text
                if i == 3:
                    result['降雨機率'] = td.text
            results[city].append(result)

    return results[select]

from selenium import webdriver # pip install selenium
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time

browser = None
def f2(text):
    global browser
    if browser:
        browser.quit()

    browser = webdriver.Chrome(executable_path='chromedriver')

    browser.get("https://www.youtube.com/results?search_query=" + text)
    time.sleep(5)

    link = browser.find_element_by_id('thumbnail')
    link = link.get_attribute('href')
    browser.get(link)
    time.sleep(5)

# =========

@app.route("/callback", methods=['GET'])
def callback_get():
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    return 'OK'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    text = json.loads(body)['events'][0]['message']['text']
    print('callback' + text)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event, text):

    text = event.message.text.split()
    print('handle_message: ' + text[0] + ', ' + text[1])
    
    reply_text = event.message.text
    
    if text[0] == '天氣':
        L = f1(text[1])
        reply_text =  "".join(str(x) for x in L)

    if text[0] == '音樂':
        f2(text[1])
        reply_text = '已幫你播放 %s 的音樂' % text[1]

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text))


if __name__ == "__main__":
    app.run()