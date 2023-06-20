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
    return high, low, margin


def calculateMarginCollection(dictionaryOfItems):
    listOfItems = []
    for item in dictionaryOfItems:
        margin = calculateMarginSingle(item["id"])
        listOfItems.append((item["id"], item["name"], margin))
    sortedList = sorted(listOfItems, key=itemgetter(1), reverse=True)
    return sortedList

def getTimeSeriesFromList(listOfItems):
    listOfSeries = []
    for item in listOfItems:
        print(item)
        listOfSeries.append((item[0], item[1], item[2], getTimeSeriesById(item[0])))
    return listOfSeries

def filterOutliers(series):
    amount5MinuteSlicesBack = -24
    # Assuming 'data' is a Pandas DataFrame with 'buy_price' and 'sell_price' columns
    data = pd.DataFrame(series[amount5MinuteSlicesBack:])
    print(data)
    threshhold = .1

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
    amount5MinuteSlicesBack = -16
    # Assuming 'data' is a Pandas DataFrame with 'buy_price' and 'sell_price' columns
    data = pd.DataFrame(series[amount5MinuteSlicesBack:])
    print(data)
    # Define outlier threshold using the Z-score method
    z_threshold = 1

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

    return buyVolatility, sellVolatility

def calculateMean(lists):
    buyPriceListMean = lists[0]['avgLowPrice'].mean()
    sellPriceListMean = lists[1]['avgHighPrice'].mean()
    print(buyPriceListMean)
    print(sellPriceListMean)
    return buyPriceListMean, sellPriceListMean

def calculateGoodFlips():
    margins = calculateMarginCollection(itemList.items)
    items = getTimeSeriesFromList(margins)
    itemsHandled = []

    for item in items:
        if(calculateRestriction(item)[0] == "True"):
            itemsHandled.append((item[0], item[1], item[2]))
    return itemsHandled

def calculateRestriction(item):
    margin = item[2][2]
    buy = item[2][1]
    sell = item[2][0]
    series = item[3]
    volatilityThreshold = 0.002
    #buyAndSellMultiplier = 0.002
    thresholdMarginPercentage = 0.0008

    outlierFilter = zSortFilterOutliers(series)
    if(outlierFilter[0].empty or outlierFilter[1].empty):
        print("not enough data in time series")
        return ("False")
    buyAndSellMean = calculateMean(outlierFilter)
    if (margin < buyAndSellMean[1] * thresholdMarginPercentage):
        print("small margin")
        return ("False")
    buyAndSellVol = calculateVolatilityAbsMean(outlierFilter)
    if (buyAndSellVol[0] > buyAndSellMean[1] * volatilityThreshold or buyAndSellVol[1] > buyAndSellMean[1] * volatilityThreshold):
        print("Buy or sell volatile")
        return ("False")
    if (buyAndSellMean[0] + buyAndSellVol[0]) < buy:
        print("Buy deviation high")
        return ("False")
    #if (buyAndSellMean[0] - buyAndSellMean[1] * volatilityThreshold) > buy:
     #   print("Buy deviation low")
      #  return ("False")
    if (buyAndSellMean[1] - buyAndSellVol[1]) > sell:
        print("Sell deviation low")
        return ("False")
    if (buyAndSellMean[1] + buyAndSellVol[1]) < sell:
        print("Sell deviation high")
        return ("False")
    return ("True", item)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    list = calculateGoodFlips()
    print(list)
    #margins = calculateMarginCollection(itemList.items)
    #items = getTimeSeriesFromList(margins)
    #series = getTimeSeriesById(13237)
    #lists = filterOutliers(series)
    #calculateVolatilityAbsMean(lists)
    #calculateMean(lists)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
