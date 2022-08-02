# Module imports
from textblob import TextBlob
from stocksymbol import StockSymbol
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service

from config import *
import os

try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")

# Relative Imports
from alpaca import create_order


def search_google_for_entry(sentence_length):
    # Stock data API
    os.environ['GH_TOKEN'] = GIT_HUB_PERSONAL
    stock_symbol = StockSymbol(api_key=STOCK_SYMBOL_API_KEY)
    symbol_list_us = stock_symbol.get_symbol_list(market="US")

    for symbol in symbol_list_us:
        query = symbol['symbol']
        for url in search(query, tld="com", num=5, stop=5, pause=2):
            # WebDriver FireFox
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
            # Target URL
            driver.get(url=url)
            # Printing the whole body text
            webpage_text = driver.find_element(by="xpath", value="/html/body").text
            # Closing the driver
            driver.close()
            # Determine logic for sentences
            sentences = webpage_text.split("\n")
            for phrase in sentences:
                if len(phrase.split(" ")) > sentence_length and phrase.find(query) != -1:
                    analysis = TextBlob(phrase)
                    element_exists = False
                    with open(GOOGLE_ANALYSIS_FILE, "r") as f:
                        for line in f:
                            element = line.split("@")
                            try:
                                if element[1] == url:
                                    element_exists = True
                                print(element)
                            except IndexError:
                                print(f'Index out of range for {element}')

                    if element_exists is False:
                        with open(GOOGLE_ANALYSIS_FILE, "a") as f:
                            item = ""                                   # element[index] positions
                            item += str(query) + "@"                    # 0th index
                            item += str(url) + "@"                      # 1st index
                            item += str(analysis.sentiment[0]) + "@"    # 2nd index
                            item += str(analysis.sentiment[1]) + "\n"   # 3rd index
                            f.write(item)


def analyze_investment(buy_amount, sell_amount, stock_quantity):
    analysis_dict = {}
    counter_dict = {}

    with open(GOOGLE_ANALYSIS_FILE, "r") as f:
        for line in f:
            key = line.split("@")[0]
            if key not in analysis_dict:
                try:
                    analysis_dict[key] = float(line.split("@")[2])
                    counter_dict[key] = 1
                except:
                    print(key + " is not a float")
            else:
                try:
                    analysis_dict[key] += float(line.split("@")[2])
                    counter_dict[key] += 1
                except:
                    print(key + " is not a float")
    print("=====================================")
    print('Bradley Bot Suggests')
    print("=====================================")

    for key in analysis_dict:
        counter = 0
        if analysis_dict[key] / counter_dict[key] > buy_amount:
            print(f'Buy: {key}')
            counter += 1
            create_order(symbol=key,
                         quantity=stock_quantity,
                         side="buy",
                         type_of_order="market",
                         time_in_force="gtc",
                         client_order_id=key)
        elif analysis_dict[key] / counter_dict[key] < sell_amount:
            print(f'Sell: {key}')
            create_order(symbol=key,
                         quantity=stock_quantity,
                         side="sell",
                         type_of_order="market",
                         time_in_force="gtc",
                         client_order_id=key)
        elif counter == 0:
            print("EVERYTHING IS POOP")
        else:
            print("Something bad happened")


search_google_for_entry(sentence_length=10)
analyze_investment(buy_amount=0.6, sell_amount=-0.3, stock_quantity=1000)
