import quandl as ql
from yahoo_finance import Share, Currency
import pandas as pd
from pandas import np
from pandas_datareader import data
import datetime
import time
import calendar
import re

from response import Response






def current_date(): 
	today = datetime.date.today().strftime("%Y-%m-%d")
	# "%Y-%m-%d %H:%M:%S %Z%z"


def last_price(ticker): 
	ticker = ticker.upper()
	price = Share(ticker).get_price()
	if not price: 
		return Response.last_price_notfound(ticker)
	trade_datetime = Share(ticker).get_trade_datetime().split(' ')
	month, day = calendar.month_name[int(trade_datetime[0][5:7].lstrip('0'))], trade_datetime[0][8:10].lstrip('0')
	trade_time = trade_datetime[1] + " UTC+0"
	return Response.last_price(ticker, price, month, day, trade_time)



# def historical_range(ticker, start=None, end=None): 
# 	return Share(ticker).get_historical('')



# Trailing Volatility: Allow up to 1500 days
def trailing_volatility(ticker, days=None):
	if days==None: 
		message = "To calculate trailing volatility for '{}' you must enter a valid number of trailing days (max. 1500).".format(ticker)
		return {"error":message}
	try:
		quotes = data.DataReader(ticker, 'google')['Close'][-days:]
	except Exception:
		message = "Error getting data for symbol '{}'.".format(ticker)
		return {"error":message} 
	logreturns = np.log(quotes / quotes.shift(1))
	vol = round(np.sqrt(252*logreturns.var()), 5)
	message = "{}-day trailing volatility for *{}*: {}".format(days,ticker,vol)
	return message


def range_volatility(ticker, start=None, end=None):
	
	pattern1 = re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$') 
	pattern2 = re.compile(r'^\d{4}\/(0?[1-9]|1[012])\/(0?[1-9]|[12][0-9]|3[01])$')

	if start==None or end==None: 
		message = "Missing date input for '{}'.".format(ticker)
		return {"error":message}
	if not(pattern1.match(start) or pattern2.match(start)) or not(pattern1.match(end) or pattern2.match(end)):
		message = "You did not enter a valid start and end date for '{}'.".format(ticker)
		return {"error":message}

	# Need to add handling for dates that pass regex but that are not real dates with datetime library. Test above logic first.

	try:
		quotes = data.DataReader(ticker, 'google')['Close'].loc[start:end]
	except Exception:
		message = "Error getting data for symbol '{}'.".format(ticker)
		return {"error":message} 
	logreturns = np.log(quotes / quotes.shift(1))
	vol = np.sqrt(252*logreturns.var())
	message = "*{}* Volatility, {}-{}: {}".format(ticker,start,end,vol)
	return message





OPERATIONS = {
	"last_price":last_price,
	"tvol":trailing_volatility,
	"dvol":range_volatility,
}








