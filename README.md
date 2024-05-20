# BackTracking_SM

In this repository, I am defining a minimal code in Python to test strategies on historical data of the stock market.
These strategies are solely based on price movements.

The dataset, sourced from Yahoo, contains data from the last year for stocks within the Health Technology Sector, and is stored in "Health_Tech_2Y_1h_19May.csv". Each row represents a potential investment for one day, tracked from one closing to the next. The columns detail various price changes: the change from the previous day's close at which the stock is purchased, as well as changes over the past 3, 7, and 28 days. Additional columns record the hourly price change on the day, the change during the current day when the stock is held, and the change from the previous day's close to the specific hour it is held on that day.

In the code "Try_One_Strategy.py", we apply one strategy (or multiple strategies by uncommenting some lines) to the historical data. For example, buy the 2 stocks with that has increased the most yesterday, but sell them if their price drop of 3%.
This code depends on "Functions_for_Strategy_Testing.py", that specify the above conditions.

The codes are rather straightforward and easy to pick up. Feel free to contact me if you have any questions or comments.

Disclosure information:
This code is based on historical data, and there can be no assurance regarding future market movements. Moreover, you should double-check it to ensure there are no errors or misunderstandings—I am not responsible for any losses or damages resulting from its use.
