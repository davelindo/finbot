## finbot

![screenshot](/screenshots/finbot1.png?raw=true "finbot 1")
![screenshot](/screenshots/finbot2.png?raw=true "finbot 2")

#### What it is
Basic finance bot for Slack. 

#### How it works
Queries to be executed are denoted with '$'. The bot parses up to 5 queries per message and returns the requested information for each.
![screenshot](/screenshots/finbot3.png?raw=true "finbot 3")

Finbot won't respond to a message that doesn't begin with a valid query, but it can be turned on and off if you want it to ignore messages.
The user can also tag finbot and ask for help with using a certain operation. 
![screenshot](/screenshots/finbot4.png?raw=true "finbot 4")


#### Current Functionality
* Fetch Last Price
* Fetch Historical Price by Date
* Fetch Price Range over any two dates
* Fetch list of dividends and stock splits
* Upload graph with specified time period and requested moving averages displayed
* Get annualized historical volatility with # of trailing days or over a given period
* Fetch P/E ratio
* Currency Exchange Rates
* Fetch data from the St. Louis Fed Database by Symbol (single value or range)
* Strong Error Handling. 
