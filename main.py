# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
from operator import itemgetter
import itemList
import requests
import numpy as np
import pandas as pd


def getItemById(id):
    r = requests.get('https://prices.runescape.wiki/api/v1/osrs/latest?id=' + str(id),
                     headers={'Accept': 'application/json',
                              'User-Agent': 'I am trying to create a program to quickly find good margins on items that I specify.',
                              'From': 'hesbergc@yandex.com'
                              })
    return r.json()["data"]


def getTimeSeriesById(id):
    r = requests.get('https://prices.runescape.wiki/api/v1/osrs/timeseries?timestep=5m&id=' + str(id),
                     headers={'Accept': 'application/json',
                              'User-Agent': 'I am trying to create a program to quickly find good margins on items that I specify.',
                              'From': 'hesbergc@yandex.com'
                              })
    return r.json()["data"]


def calculateMarginSingle(id):
    data = getItemById(id)
    prices = data[str(id)]
    high = prices["high"]
    low = prices["low"]
    margin = high - low - high * 0.01
    return margin


def calculateMarginCollection(dictionaryOfItems):
    listOfItems = []
    for item in dictionaryOfItems:
        margin = calculateMarginSingle(item["id"])
        listOfItems.append((item["name"], margin))
    sortedList = sorted(listOfItems, key=itemgetter(1), reverse=True)
    print(sortedList)


def calculateVolatility(id):
    series = getTimeSeriesById(id)
    high = []
    low = []
    lastHigh = 0
    lastLow = 0
    for item in series:
        if(item['avgHighPrice'] != None):
            high.append(item['avgHighPrice'] - lastHigh)
            lastHigh = item['avgHighPrice']
        if(item['avgLowPrice'] != None):
            low.append(item['avgLowPrice'] - lastLow)
            lastLow = item['avgLowPrice']
    del low[0]
    del high[0]
    dataLow = low[-10:]
    dataHigh = high[-10:]
    lowVolatilityHalf = np.std(dataLow)
    highVolatilityHalf = np.std(dataHigh)
    lowVolatility = np.std(low)
    highVolatility = np.std(high)
    print(low)
    print(high)
    print(highVolatility)
    print(lowVolatility)
    print(highVolatilityHalf)
    print(lowVolatilityHalf)
    #print(lowChange)

def pandasTest(id):
    series = getTimeSeriesById(id)
    frame = pd.DataFrame(series)
    print(frame)

def priceCalc(id):
    # Assuming 'data' is a Pandas DataFrame with 'buy_price' and 'sell_price' columns
    series = getTimeSeriesById(id)
    data = pd.DataFrame(series[-11:])
    print(data)
    threshhold = .3

    # Define outlier threshold using the interquartile range (IQR) method
    q1 = data['avgLowPrice'].quantile(0.25)
    q3 = data['avgLowPrice'].quantile(0.75)
    iqr = q3 - q1
    outlier_threshold = threshhold * iqr

    # Filter outliers for buy price
    filtered_data = data[
        (data['avgLowPrice'] >= (q1 - outlier_threshold)) & (data['avgLowPrice'] <= (q3 + outlier_threshold))]
    print(filtered_data)

    # Determine good buy price
    good_buy_price = filtered_data['avgLowPrice'].mean()

    # Filter outliers for sell price
    q1 = data['avgHighPrice'].quantile(0.25)
    q3 = data['avgHighPrice'].quantile(0.75)
    iqr = q3 - q1
    outlier_threshold = threshhold * iqr
    filtered_data = data[
        (data['avgHighPrice'] >= (q1 - outlier_threshold)) & (data['avgHighPrice'] <= (q3 + outlier_threshold))]
    print(filtered_data)

    # Determine good sell price
    good_sell_price = filtered_data['avgHighPrice'].mean()

    print("Good Buy Price:", good_buy_price)
    print("Good Sell Price:", good_sell_price)


def zSort(id):
    import pandas as pd
    import numpy as np

    # Assuming 'data' is a Pandas DataFrame with 'buy_price' and 'sell_price' columns
    series = getTimeSeriesById(id)
    data = pd.DataFrame(series[-11:])
    print(data)
    # Define outlier threshold using the Z-score method
    z_threshold = 1

    # Filter outliers for buy price
    z_scores_buy = np.abs((data['avgLowPrice'] - data['avgLowPrice'].mean()) / data['avgLowPrice'].std())
    print(z_scores_buy)
    filtered_data_buy = data[z_scores_buy <= z_threshold]
    print(filtered_data_buy)

    # Determine good buy price
    good_buy_price = filtered_data_buy['avgLowPrice'].mean()

    # Filter outliers for sell price
    z_scores_sell = np.abs((data['avgHighPrice'] - data['avgHighPrice'].mean()) / data['avgHighPrice'].std())
    print(z_scores_sell)
    filtered_data_sell = data[z_scores_sell <= z_threshold]
    print(filtered_data_sell)
    # Determine good sell price
    good_sell_price = filtered_data_sell['avgHighPrice'].mean()

    print("Good Buy Price:", good_buy_price)
    print("Good Sell Price:", good_sell_price)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #zSort(13237)
    priceCalc(27657)
    #calculateVolatility(13237)
    #pandasTest(13237)
    # calculateMarginCollection(itemList.items)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
