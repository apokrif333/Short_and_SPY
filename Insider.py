from bs4 import BeautifulSoup as bs
from pyautogui import press, typewrite, hotkey, keyDown, keyUp

import requests
import time
import webbrowser
import pandas as pd; pd.set_option('display.max_columns', 500)

urls_df = pd.read_csv('text_data/si_guidance_urls.csv')

for i in range(16_410, 19_532):
    print(i)

    url = urls_df.url[i]
    page = webbrowser.open(url, new=0)
    time.sleep(6)

    keyDown('ctrl')
    keyDown('w')
    keyUp('w')
    keyUp('ctrl')


    # page = requests.get(url, headers={'User-Agent': ua.random}, params={'type': 'upcoming'})
    # soup = bs(page.content, 'html.parser')
    # print(soup.prettify())

    # soup = bs(page.content, 'html.parser')
    # print(soup.prettify())
    # print([type(item) for item in list(soup.children)])
    # tables = soup.find_all(class_="article_body")
    # print(tables)
