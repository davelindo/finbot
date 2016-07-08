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


patterns = {
	"tvol": re.compile(r'^([1-9][0-9]|[1-9][0-9][0-9]|[1-1][0-4][0-9][0-9]|1500)$'),
	"rvol": re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'),
}



# Create built in documentation
# if Function is called with "info" as only component, return a message explaining how the function works
# (arguments, what it returns, boundaries etc)




def current_date(): 
	return datetime.date.today().strftime("%Y-%m-%d")
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


def trailing_volatility(ticker, components):
	days=None
	for each in components: 
		if patterns['tvol'].match(each):
			days = int(each)
			break
	if days==None:
		message = "Enter a valid number of trailing days (10-1500) to calculate trailing volatility for '{}'.".format(ticker)
		return message
	print(days, type(days))
	try:
		quotes = data.DataReader(ticker, 'google')['Close'][-days:]
	except Exception:
		message = "Error getting data for symbol '{}'.".format(ticker)
		return message
	logreturns = np.log(quotes / quotes.shift(1))
	vol = round(np.sqrt(252*logreturns.var()), 5)
	message = "{}-day trailing volatility for *{}*: {}".format(days,ticker,vol)
	return message


# 2010-01-04 to present
def range_volatility(ticker, components): 
	# Parse and check: find components matching dates, ensure start and end are present, ensure dates are valid
	today, dates = current_date(), []
	for each in components: 
		if patterns['rvol'].match(each):
			dates.append(each)
	if len(dates)!=2:
		return "Enter a valid start and end date to calculate volatility for '{}'.".format(ticker)
	for each in dates: 
		if each > today: 
			return "'{}' is an invalid date.".format(each)
		try: 
			date = datetime.datetime.strptime(each, '%Y-%m-%d')
		except ValueError: 
			return "'{}' is an invalid date.".format(each)

	# Volatility Calculation
	dates = sorted(dates)
	start, end = dates[0], dates[1]
	try:
		quotes = data.DataReader(ticker, 'google')['Close'].loc[start:end]
	except Exception:
		return "Error getting data for symbol '{}'.".format(ticker)
	logreturns = np.log(quotes / quotes.shift(1))
	vol = round(np.sqrt(252*logreturns.var()), 5)
	if np.isnan(vol): 
		return "Enter a larger range to calculate volatility for '{}'.".format(ticker)
	message = "Volatility for _`{}`_ from {} to {}: *`{}`*".format(ticker,start,end,vol)
	return message





OPERATIONS = {
	"last_price":last_price,
	"tvol":trailing_volatility,
	"rvol":range_volatility,
}








