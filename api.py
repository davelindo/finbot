from yahoo_finance import Share, Currency
import pandas as pd
from pandas import np
from pandas_datareader import data
from fractions import Fraction
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
	"valid_date": re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'),
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


def historical_data(ticker, components): 
	# Prices adjusted for splits
	today, dates = current_date(), []
	for each in components: 
		if PATTERNS['valid_date'].match(each):
			dates.append(each)
	if not dates: 
		return {"message": Response.missing_dates(ticker)}
	# Validate dates
	for each in dates: 
		if each > today: 
			return {"message": Response.invalid_date(each)}
		try: 
			date = datetime.datetime.strptime(each, '%Y-%m-%d')
		except ValueError: 
			return {"message": Response.invalid_date(each)}
	# Validate ticker and fetch data
	try: 
		quotes = data.get_data_google(ticker)
	except Exception: 
		return {"message": Response.data_notfound(ticker)}

	# Return price data for one day
	if len(dates)==1: 
		date = dates[0]
		try: 
			quote = quotes.loc[date]
		except KeyError: 
			return {"message": Response.no_data_for_date(date)}
		return {"message": Response.historical_price(
			ticker, date, quote['Open'], quote['High'], quote['Low'], quote['Close'], int(quote['Volume']))}

	# If 2 dates are entered, returned the range during the given period
	elif len(dates)==2: 
		dates = sorted(dates)
		start, end = dates[0], dates[1]
		quotes = quotes.loc[start:end]
		high = round(quotes['High'].max(),2)
		low = round(quotes['Low'].min(),2)
		return {"message": Response.historical_range(ticker, start, end, high, low)}

	else: 
		return {"message": Response.too_many_dates(ticker)}


def name_exchange(ticker, components): 
	exchanges = {"NMS":"NASDAQ","NYQ":"NYSE"}
	try: 
		info = data.get_components_yahoo(ticker)
	except Exception: 
		return {"message": Response.data_notfound(ticker)}
	name, symbol = info['name'][0], info['exchange'][0]
	exchange = exchanges.get(symbol)
	if not exchange: 
		exchange = symbol
	return {"message": Response.name_exchange_response(ticker, name, exchange)}


def actions(ticker, components):
	# Splits are quoted as decimals - convert to fraction ('7 for 1' vs .142857)
	def split_ratio(dec): 
		frac = Fraction.from_float(dec).limit_denominator(10)
		num, denom = frac.numerator, frac.denominator 
		return "{} for {}".format(denom, num)
	try: 
		actions = data.get_data_yahoo_actions(ticker)
	except Exception: 
		return {"message": Response.data_notfound(ticker)}
	if len(actions)==0: 
		return {"message": Response.no_actions(ticker)}
	actions.ix[actions.action=="SPLIT", 'value'] = actions.value.map(lambda x: split_ratio(x))
	actions['action'] = actions.action.map(lambda x: x.lower())
	actions.index = actions.index.map(lambda x: datetime.date(x.year, x.month, x.day).strftime('%Y-%m-%d'))
	actions.iloc[::-1]

	# Build message from DataFrame
	message = Response.list_actions(ticker)
	for date, action, value in zip(actions.index, actions.action, actions.value):
		message += ("\n{} - {} `{}`".format(date, action, value))
	return {"message": message}


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
	return {"attachments" : attachment, "message" : ''}


def trailing_volatility(ticker, components):
	days=None
	for each in components: 
		if PATTERNS['tvol'].match(each):
			days = int(each)
			break
	if days==None:
		return {"message": Response.trailing_days(ticker)}
	try:
		quotes = data.DataReader(ticker, 'google')['Close'][-days:]
	except Exception:
		return {"message": Response.data_notfound(ticker)}
	logreturns = np.log(quotes / quotes.shift(1))
	vol = round(np.sqrt(252*logreturns.var()), 5)
	return {"message" : Response.trailing_vol(days, ticker, vol)}


# 2010-01-04 to present
def range_volatility(ticker, components): 
	# Parse and check: find components matching dates, ensure start and end are present, ensure dates are valid
	today, dates = current_date(), []
	for each in components: 
		if PATTERNS['valid_date'].match(each):
			dates.append(each)
	if len(dates)!=2:
		return {"message": Response.vol_required_dates(ticker)}
	for each in dates: 
		if each > today: 
			return {"message": Response.invalid_date(each)}
		try: 
			date = datetime.datetime.strptime(each, '%Y-%m-%d')
		except ValueError: 
			return {"message": Response.invalid_date(each)}

	# Volatility Calculation
	dates = sorted(dates)
	start, end = dates[0], dates[1]
	try:
		quotes = data.DataReader(ticker, 'google')['Close'].loc[start:end]
		if len(quotes) < 10: 
			return {"message": Response.vol_range_size(ticker)}
	except Exception:
		return {"message": Response.data_notfound(ticker)}
	logreturns = np.log(quotes / quotes.shift(1))
	vol = round(np.sqrt(252*logreturns.var()), 5)
	return {"message" : Response.range_vol(ticker, start, end, vol)}


def pe_ratio(ticker, components): 
	quote = data.get_quote_yahoo(ticker)
	PE = quote['PE'][0]
	if PE=='N/A':
		return {"message": Response.pe_notfound(ticker)}
	PE = ('%.2f' % PE)
	return {"message": Response.pe_response(ticker, PE)}


def exchange_rate(symbol, components): 
	rate = Currency(symbol).get_rate()
	if not rate: 
		return {"message":Response.no_ratefound(symbol)}
	return {"message": Response.exchange_rate(symbol, rate)}


def get_fred(symbol, components): 
	symbol = symbol.upper()
	try: 
		df = data.get_data_fred(symbol)
	except Exception: 
		return {"message":Response.fred_notfound(symbol)}

	today, dates = current_date(), []
	for each in components: 
		if PATTERNS['valid_date'].match(each):
			dates.append(each)
	# No dates: get most recent value
	if not dates: 
		df.dropna()
		last_value = df.tail(1)[symbol][0]
		last_value = ('%.3f' % last_value)
		return {"message": Response.basic_fred(symbol, last_value)}

	# Clean dates
	if len(dates)>2: 
		return {"message": Response.too_many_dates(symbol)}
	for each in dates: 
		if each > today: 
			return {"message": Response.invalid_date(each)}
		try: 
			date = datetime.datetime.strptime(each, '%Y-%m-%d')
		except ValueError: 
			return {"message": Response.invalid_date(each)}


	# Return price data for one day
	if len(dates)==1: 
		date = dates[0]
		try: 
			value = df.loc[date][symbol]
		except KeyError: 
			return {"message": Response.fred_date_notfound(symbol, date)}
		if pd.isnull(value): 
			return {"message": Response.fred_date_notfound(symbol, date)}
		return {"message": Response.date_fred(symbol, date, value)}

	# If 2 dates are entered, returned the range during the given period
	else: 
		dates = sorted(dates)
		start, end = dates[0], dates[1]
		df = df.loc[start:end]
		high = ('%.3f' % df[symbol].max())
		low = ('%.3f' % df[symbol].min())
		return {"message": Response.fred_data_range(symbol, start, end, high, low)}











OPERATIONS = {
	"last_price":last_price,
	"hist":historical_data,
	"?":name_exchange,
	"actions":actions,
	"-g":graph,
	"tvol":trailing_volatility,
	"rvol":range_volatility,
	"PE":pe_ratio,
	"rate":exchange_rate,
	"fred":get_fred,
}








