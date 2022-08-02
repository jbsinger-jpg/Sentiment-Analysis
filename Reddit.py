# Module Imports
import requests
from textblob import TextBlob
from stocksymbol import StockSymbol
import operator

# Relative Imports
from config import *
from alpaca import create_order

auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)

# Header used to represent meta-data associated with API Request
headers = {'User-Agent': 'MyAPI/0.0.1'}
res = requests.post(REDDIT_ACCESS_TOKEN_URL, auth=auth, data=REDDIT_CONFIG_DATA, headers=headers)
TOKEN = res.json()['access_token']
headers['Authorization'] = f'bearer {TOKEN}'

# format of http link goes 'https://oauth.reddit.com/r/<subreddit>/<post_type>'
# review documentation for more details
hot_res = requests.get('{}/wallstreetbets/hot'.format(REDDIT_POST_URL), headers=headers)

# Stock data API
stock_symbol = StockSymbol(api_key=STOCK_SYMBOL_API_KEY)
symbol_list_us = stock_symbol.get_symbol_list(market="US")

with open(REDDIT_ANALYSIS_FILE, "a") as f:
    for post in hot_res.json()['data']['children']:
        analysis = TextBlob(post['data']['selftext'])
        for symbol in symbol_list_us:
            if operator.contains(post['data']['selftext'], symbol['longName']):
                analysis = TextBlob(post['data']['selftext'])
                item = ""
                item += str(analysis.sentiment[0]) + ","
                item += str(analysis.sentiment[1]) + "\n"
                f.write(item)

            if operator.contains(post['data']['title'], symbol['longName']):
                analysis = TextBlob(post['data']['title'])
                item = ""
                item += str(analysis.sentiment[0]) + ","
                item += str(analysis.sentiment[1]) + "\n"
                f.write(item)


def analyze_investment(buy_amount, sell_amount, stock_quantity):
    analysis_dict = {}
    counter_dict = {}

    with open(REDDIT_ANALYSIS_FILE, "r") as f:
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


analyze_investment(buy_amount=0.6, sell_amount=-0.3, stock_quantity=1000)