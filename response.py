class Response: 

	def last_price_notfound(ticker):
		return "No result found for '{}'".format(ticker)

	def last_price(ticker, price, month, day, trade_time): 
		return "*{} Last Price:* {} ({} {} @ {})".format(ticker, price, month, day, trade_time)


