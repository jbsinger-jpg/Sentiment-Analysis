# Module Imports
import tweepy
from textblob import TextBlob
from stocksymbol import StockSymbol

# Relative Imports
from config import *
from alpaca import create_order

# Global variables
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
stock_symbol = StockSymbol(api_key=TWITTER_API_KEY)
symbol_list_us = stock_symbol.get_symbol_list(market="US")


def sentiment_analysis(query, dead_zone_opinion, dead_zone_subjectivity):
    try:
        tweets = client.search_recent_tweets(query=query)
        with open(TWITTER_ANALYSIS_FILE, "a") as f:
            if len(tweets) != 0:
                for tweet in tweets.data:
                    if tweet is not None:
                        analysis = TextBlob(tweet.text)
                        opinion = analysis.sentiment[0]
                        subjectivity = analysis.sentiment[1]

                        if abs(opinion) > dead_zone_opinion and abs(subjectivity) < dead_zone_subjectivity:
                            if analysis is not None:
                                item = ""
                                item += str(query) + "@"
                                item += str(analysis.sentiment[0]) + "@"
                                item += str(analysis.sentiment[1]) + "\n"
                                f.write(item)
    except:
        print("Bad tweepy query")


def loop_through_queries(dead_zone_opinion, dead_zone_subjectivity):
    for symbol in symbol_list_us:
        if symbol['longName'] is not None:
            sentiment_analysis(query=symbol['longName'],
                               dead_zone_opinion=dead_zone_opinion,
                               dead_zone_subjectivity=dead_zone_subjectivity)


def analyze_investment(buy_amount, sell_amount, stock_quantity):
    analysis_dict = {}
    counter_dict = {}

    with open(TWITTER_ANALYSIS_FILE, "r") as f:
        for line in f:
            key = line.split("@")[0]
            if key not in analysis_dict:
                try:
                    analysis_dict[key] = float(line.split("@")[1])
                    counter_dict[key] = 1
                except:
                    print(key + " is not a float")
            else:
                try:
                    analysis_dict[key] += float(line.split("@")[1])
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
            create_order(symbol=key,
                         quantity=stock_quantity,
                         side="buy",
                         type_of_order="market",
                         time_in_force="gtc",
                         client_order_id=key)
            counter += 1
        elif analysis_dict[key] / counter_dict[key] < sell_amount:
            print(f'Sell: {key}')
            create_order(symbol=key,
                         quantity=stock_quantity,
                         side="sell",
                         type_of_order="market",
                         time_in_force="gtc",
                         client_order_id=key)
            counter += 1
        elif counter == 0:
            print("EVERYTHING IS POOP")
        else:
            print("Something bad happened")


loop_through_queries(dead_zone_opinion=0.1, dead_zone_subjectivity=0.3)
analyze_investment(buy_amount=0.6, sell_amount=-0.3, stock_quantity=1000)
