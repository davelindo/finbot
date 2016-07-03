import quandl as ql
import pandas as pd
import numpy as np 
import datetime
import time
import calendar
from yahoo_finance import Share, Currency

class Utils: 

	@staticmethod
	def current_date(): 
		today = datetime.date.today().strftime("%Y-%m-%d")

		# "%Y-%m-%d %H:%M:%S %Z%z"

class Source: 

	@staticmethod
	def last_price(ticker): 
		price = Share(ticker).get_price()
		if not price: 
			return "No result found for '{}'".format(ticker)
		trade_datetime = Share(ticker).get_trade_datetime().split(' ')
		month, day = calendar.month_name[int(trade_datetime[0][5:7].lstrip('0'))], trade_datetime[0][8:10].lstrip('0')
		trade_time = trade_datetime[1] + " UTC+0"
		response = "{} Last Price: {} ({} {} @ {})".format(ticker, price, month, day, trade_time)
		return response
 
	# @staticmethod
	# def historical_range(ticker, start=None, end=None): 
	# 	return Share(ticker).get_historical('')

