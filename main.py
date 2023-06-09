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
        listOfItems.append((item["id"], item["name"], margin))
    sortedList = sorted(listOfItems, key=itemgetter(1), reverse=True)
    print(sortedList)
    return sortedList

def getTimeSeriesFromList(listOfItems):
    listOfSeries = []
    for item in listOfItems:
        listOfSeries.append((item[1], item[2], getTimeSeriesById(item[0])))
    return listOfSeries

def filterOutliers(series):
    # Assuming 'data' is a Pandas DataFrame with 'buy_price' and 'sell_price' columns
    data = pd.DataFrame(series[-24:])
    print(data)
    threshhold = .3

    # Define outlier threshold using the interquartile range (IQR) method
    q1 = data['avgLowPrice'].quantile(0.25)
    q3 = data['avgLowPrice'].quantile(0.75)
    iqr = q3 - q1
    outlier_threshold = threshhold * iqr

    # Filter outliers for buy price
    filtered_data_buy = data[
        (data['avgLowPrice'] >= (q1 - outlier_threshold)) & (data['avgLowPrice'] <= (q3 + outlier_threshold))]
    print(filtered_data_buy)

    # Filter outliers for sell price
    q1 = data['avgHighPrice'].quantile(0.25)
    q3 = data['avgHighPrice'].quantile(0.75)
    iqr = q3 - q1
    outlier_threshold = threshhold * iqr
    filtered_data_sell = data[
        (data['avgHighPrice'] >= (q1 - outlier_threshold)) & (data['avgHighPrice'] <= (q3 + outlier_threshold))]
    print(filtered_data_sell)
    return filtered_data_buy, filtered_data_sell

def zSortFilterOutliers(series):
    # Assuming 'data' is a Pandas DataFrame with 'buy_price' and 'sell_price' columns
    data = pd.DataFrame(series[-24:])
    print(data)
    # Define outlier threshold using the Z-score method
    z_threshold = .85

    # Filter outliers for buy price
    z_scores_buy = np.abs((data['avgLowPrice'] - data['avgLowPrice'].mean()) / data['avgLowPrice'].std())
    print(z_scores_buy)
    filtered_data_buy = data[z_scores_buy <= z_threshold]
    print(filtered_data_buy)

    # Filter outliers for sell price
    z_scores_sell = np.abs((data['avgHighPrice'] - data['avgHighPrice'].mean()) / data['avgHighPrice'].std())
    print(z_scores_sell)
    filtered_data_sell = data[z_scores_sell <= z_threshold]
    print(filtered_data_sell)
    return filtered_data_buy, filtered_data_sell

def calculateVolatilityAbsMean(lists):
    buyPriceList = lists[0]['avgLowPrice']
    sellPriceList = lists[1]['avgHighPrice']

    buyDiff = buyPriceList.diff()
    sellDiff = sellPriceList.diff()

    print(buyDiff)
    print(sellDiff)

    buyVolatility = buyDiff.abs().mean()
    sellVolatility = sellDiff.abs().mean()

    print(buyVolatility)
    print(sellVolatility)


def calculateMean(lists):
    buyPriceListMean = lists[0]['avgLowPrice'].mean()
    sellPriceListMean = lists[1]['avgHighPrice'].mean()
    print(buyPriceListMean)
    print(sellPriceListMean)
    return buyPriceListMean, sellPriceListMean

def calculateGoodFlips():
    margins = calculateMarginCollection(itemList.items)
    items = getTimeSeriesFromList(margins)

    



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #series = getTimeSeriesById(13239)
    #lists = zSortFilterOutliers(series)
    #calculateVolatilityAbsMean(lists)
    #calculateMean(lists)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
