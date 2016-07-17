class Response: 

	info = {
		"hist": """Use `hist` with a single date to fetch price data, or with two dates to get the range of a stock's price over a period of time. Data is available from 2010 to present and is adjusted for splits. \n Format: `$<ticker> hist YYYY-MM-dd YYYY-MM-dd`""",
		"?" : "Use `$<ticker> ?` to fetch the name and exchange for a publicly traded company.",
		"actions": "Use `$<ticker> actions` to fetch a list of corporate actions (dividends and stock splits).",
		"-g" : """Format: `$<ticker> -g <period> <mavg>` \
			\n Example: `$AAPL -g 1y 50ma 200ma` \
			\n ```Supported time periods for graphing: 1d, 5d, 1m, 3m, 6m, 1y, 2y, 5y. The period will default to 1d if a valid value is not entered. Four moving averages are supported: 20-, 50-, 100-, and 200-day. Any combination of the four, or none at all, can be displayed at once.```""",
		"tvol" : "`tvol` calculates annualized historical volatility using daily log returns for the given number of trailing trading days. \n Format: `$<ticker> tvol <# days>`",
		"rvol" : "`rvol` calculates annualized historical volatility of a security using daily log returns over the time period specified. \n Format: `$<ticker> rvol YYYY-MM-dd YYYY-MM-dd`", 
		"PE" : "Use `$<ticker> PE` to fetch the current price-earnings ratio for a security."
	}

	ON_MESSAGES = [
	"Ready!",
	"Finbot is now ON.",
	"Turning on...",
	"Finbot ready.",
	"How can I help?",
	"What can I do for you?"
	]

	OFF_MESSAGES = [
	"Going to sleep...",
	"Sleeping...",
	"Turning off...",
	"Shutting down...",
	"Finbot is now OFF."
	]

	TOO_MANY_REQUESTS = [
	"Take it easy! I can only handle a few requests at a time.",
	"I can only handle a few requests per message."
	]

	BOT_INFO = "Use `@finbot <operation name> info` to get information about how to format a query."


	# General
	def data_notfound(ticker): 
		return "Error getting data for symbol '{}'.".format(ticker)

	def unknown_command(ticker): 
		return "I couldn't understand your request for ticker '{}'.".format(ticker)

	# Last Price
	def last_price_notfound(ticker):
		return "No result found for '{}'.".format(ticker)

	def last_price(ticker, price, month, day, trade_time): 
		return "Last Price for *{}*: *`${}`* ({} {} @ {})".format(ticker, price, month, day, trade_time)

	# Name and Exchange
	def name_exchange_response(ticker, name, exchange): 
		return "*{} - {}* ({})".format(ticker, name, exchange)

	# Actions
	def no_actions(ticker): 
		return "No corporate actions found for {}.".format(ticker)

	def list_actions(ticker): 
		return "Corporate Actions for *{}* (Date, Type, Value):".format(ticker)


	# Trailing Volatility
	def trailing_days(ticker): 
		return "Enter a valid number of trailing days (10-1500) to calculate trailing volatility for '{}'.".format(ticker)

	def trailing_vol(days, ticker, vol):
		return "{}-day annualized trailing volatility for *{}*: *`{}`*".format(days,ticker,vol)


	# Range Volatility & Historical Data
	def vol_required_dates(ticker): 
		return "Enter a valid start and end date to calculate volatility for '{}'.".format(ticker)

	def vol_range_size(ticker): 
		return "Enter a larger range to calculate volatility for '{}' (min. 10 trading days).".format(ticker)
		
	def range_vol(ticker, start, end, vol):
		return "Annualized Volatility for *{}* from {} to {}: *`{}`*".format(ticker,start,end,vol)

	def invalid_date(date): 
		return "'{}' is not a valid date.".format(date)

	def no_data_for_date(date): 
		return "No data for {}.".format(date)

	def missing_dates(ticker):
		return "Enter valid dates to get historical data for {}.".format(ticker)

	def historical_price(ticker, date, _open, high, low, close, volume): 
		return "*{}* – {} \n Open: {} \n High: {} \n Low: {} \n Close: {} \n Volume: {}".format(ticker,date,_open,high,low,close,volume)

	def historical_range(ticker, start, end, high, low): 
		return "Range for *{}* from {} to {}: *`{}-{}`*".format(ticker, start, end, low, high)

	def too_many_dates(ticker): 
		return "Too many dates given for '{}'.".format(ticker)


	# PE
	def pe_notfound(ticker): 
		return "No P/E ratio found for '{}'.".format(ticker)

	def pe_response(ticker, PE): 
		return "Price/Earnings for *{}*: *`{}`*".format(ticker, PE)










