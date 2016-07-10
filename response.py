class Response: 

	info = {
		"tvol" : "`tvol` calculates annualized historical volatility using daily log returns for the given number of trailing trading days. \n Format: `$<ticker> tvol <# days>`",
		"rvol" : "`rvol` calculates annualized historical volatility of a security using daily log returns over the time period specified. \n Format: `$<ticker> rvol YYYY-MM-dd YYYY-MM-dd`", 
	}


	# General
	def data_notfound(ticker): 
		return "Error getting data for symbol '{}'.".format(ticker)




	# Last Price
	def last_price_notfound(ticker):
		return "No result found for '{}'".format(ticker)

	def last_price(ticker, price, month, day, trade_time): 
		return "Last Price for *{}*: *`${}`* ({} {} @ {})".format(ticker, price, month, day, trade_time)


	# Trailing Volatility
	def trailing_days(ticker): 
		return "Enter a valid number of trailing days (10-1500) to calculate trailing volatility for '{}'.".format(ticker)

	def trailing_vol(days, ticker, vol):
		return "{}-day trailing volatility for *{}*: *`{}`*".format(days,ticker,vol)


	# Range Volatility
	def required_dates(ticker): 
		return "Enter a valid start and end date to calculate volatility for '{}'.".format(ticker)

	def invalid_date(ticker): 
		return "'{}' is not a valid date.".format(ticker)

	def range_size(ticker): 
		return "Enter a larger range to calculate volatility for '{}' (min. 10 trading days).".format(ticker)

	def range_vol(ticker, start, end, vol):
		return "Volatility for *{}* from {} to {}: *`{}`*".format(ticker,start,end,vol)







