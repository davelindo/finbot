import quandl as ql
from yahoo_finance import Share, Currency
import pandas as pd
from pandas import np
from pandas_datareader import data
import datetime
import calendar
import re

from response import Response


PATTERNS = {
	"-g": {
		'period' : ['1d','5d','1m','3m','6m','1y','2y','5y'],
		'mavg' : ['20ma','50ma','100ma','200ma']
		}, 
	"tvol": re.compile(r'^([1-9][0-9]|[1-9][0-9][0-9]|[1-1][0-4][0-9][0-9]|1500)$'),
	"rvol": re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'),
}


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

def historical_range(ticker, start=None, end=None): 
	return Share(ticker).get_historical('')

def historical_price(ticker, date=None): 
	pass

def full_historical_data(ticker, start, end): 
	pass

def name_exchange(ticker, components): 
	exchanges = {"NMS":"NASDAQ","NYQ":"NYSE"}
	try: 
		info = data.get_components_yahoo(ticker)
	except Exception: 
		message = Response.data_notfound(ticker)
	name, symbol = info['name'][0], info['exchange'][0]
	exchange = exchanges.get(symbol)
	if not exchange: 
		exchange = symbol
	message = Response.name_exchange_response(ticker, name, exchange)
	output = {"message": message, "attachments": '[]'}
	return output




"""

historical time series (as Excel or XLV? as graph? use pandas datareader - other indexes besides 'close')

"""

def graph(ticker, components): 
	"""
	Fetches graph by ticker from Yahoo Finance and sends image as an attachment. 
	Input for time period and displayed moving averages.
	"""
	period = None
	components = [item.lower() for item in components]
	date_patterns = list(set(PATTERNS['-g']['period']).intersection(components))
	mavg_patterns = list(set(PATTERNS['-g']['mavg']).intersection(components))
	if not date_patterns: 
		period = '1d'
	else:
		period = date_patterns[0]

	# Build Graph URL
	url = 'http://chart.finance.yahoo.com/z?s=' + str(ticker.upper()) + '&t=' + period + '&q=l&l=on&z=s&p='
	if mavg_patterns: 
		for each in mavg_patterns: 
			each.rstrip('ma')
			each = "m"+each+","
			url+=each	

	# Build Attachment
	fallback = "Graph for {} – {}".format(ticker, url)
	title = "{} - {}".format(ticker, period)
	text = ""
	footer = "Retrieved from Yahoo! Finance"
	attachment = '[{{"fallback": "{}", "title": "{}", "title_link": "{}", "text": "{}", "image_url": "{}", "color": "38629c", "footer": "{}" }}]'.format(fallback, title, url, text, url, footer)
	output = {"attachments" : attachment, "message" : ''}
	return output


def trailing_volatility(ticker, components):
	days=None
	for each in components: 
		if PATTERNS['tvol'].match(each):
			days = int(each)
			break
	if days==None:
		return Response.trailing_days(ticker)
	try:
		quotes = data.DataReader(ticker, 'google')['Close'][-days:]
	except Exception:
		return Response.data_notfound(ticker)
	logreturns = np.log(quotes / quotes.shift(1))
	vol = round(np.sqrt(252*logreturns.var()), 5)
	message = Response.trailing_vol(days, ticker, vol)
	output = {"message" : message, "attachments" : '[]'}
	return output


# 2010-01-04 to present
def range_volatility(ticker, components): 
	# Parse and check: find components matching dates, ensure start and end are present, ensure dates are valid
	today, dates = current_date(), []
	for each in components: 
		if PATTERNS['rvol'].match(each):
			dates.append(each)
	if len(dates)!=2:
		return Response.required_dates(ticker)
	for each in dates: 
		if each > today: 
			return Response.invalid_date(each)
		try: 
			date = datetime.datetime.strptime(each, '%Y-%m-%d')
		except ValueError: 
			return Response.invalid_date(each)

	# Volatility Calculation
	dates = sorted(dates)
	start, end = dates[0], dates[1]
	try:
		quotes = data.DataReader(ticker, 'google')['Close'].loc[start:end]
		if len(quotes) < 10: 
			return Response.range_size(ticker)
	except Exception:
		return Response.data_notfound(ticker)
	logreturns = np.log(quotes / quotes.shift(1))
	vol = round(np.sqrt(252*logreturns.var()), 5)
	message = Response.range_vol(ticker, start, end, vol)
	output = {"message" : message, "attachments" : '[]'}
	return output





OPERATIONS = {
	"last_price":last_price,
	"?":name_exchange,
	"-g":graph,
	"tvol":trailing_volatility,
	"rvol":range_volatility,
}








