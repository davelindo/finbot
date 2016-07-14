class Response: 

	info = {
		"-g" : """Format: `$<ticker> -g <period> <mavg>` \
		\n Example: `$AAPL -g 1y 50ma 200ma` \
		\n ```Supported time periods for graphing: 1d, 5d, 1m, 3m, 6m, 1y, 2y, 5y. The period will default to 6m if a valid value is not entered. Four moving averages are supported: 20-, 50-, 100-, and 200-day. Any combination of the four, or none at all, can be displayed at once.```""",

		"tvol" : "`tvol` calculates annualized historical volatility using daily log returns for the given number of trailing trading days. \n Format: `$<ticker> tvol <# days>`",
		"rvol" : "`rvol` calculates annualized historical volatility of a security using daily log returns over the time period specified. \n Format: `$<ticker> rvol YYYY-MM-dd YYYY-MM-dd`", 
	}

	ON_MESSAGES = [
	"Ready!",
	"Finbot is now ON.",
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
		return "No result found for '{}'".format(ticker)

	def last_price(ticker, price, month, day, trade_time): 
		return "Last Price for *{}*: *`${}`* ({} {} @ {})".format(ticker, price, month, day, trade_time)


	# Trailing Volatility
	def trailing_days(ticker): 
		return "Enter a valid number of trailing days (10-1500) to calculate trailing volatility for '{}'.".format(ticker)

	def trailing_vol(days, ticker, vol):
		return "{}-day annualized trailing volatility for *{}*: *`{}`*".format(days,ticker,vol)


	# Range Volatility
	def required_dates(ticker): 
		return "Enter a valid start and end date to calculate volatility for '{}'.".format(ticker)

	def invalid_date(ticker): 
		return "'{}' is not a valid date.".format(ticker)

	def range_size(ticker): 
		return "Enter a larger range to calculate volatility for '{}' (min. 10 trading days).".format(ticker)

	def range_vol(ticker, start, end, vol):
		return "Annualized Volatility for *{}* from {} to {}: *`{}`*".format(ticker,start,end,vol)







