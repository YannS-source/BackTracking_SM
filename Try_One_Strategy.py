# Import necessary libraries
import Functions_for_Strategy_Testing as STF  # Custom functions for strategy testing
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt


def apply_strategy(df, condition_params, starting, exiting, limit, exit_condition=True):
    """
    Applies a trading strategy based on specified conditions to a dataframe of stock data.

    Parameters:
    df (DataFrame): The DataFrame containing stock data.
    condition_params (dict): A dictionary where keys are condition names and values are tuples defining the conditions.
    starting (int): The starting index from the DataFrame's date list to begin applying the strategy.
    exiting (int): The ending index from the DataFrame's date list to stop applying the strategy.
    limit (float): A threshold limit that defines when to exit a position based on the strategy.
    exit_condition (bool): A flag to determine whether to apply a particular exit condition or not.

    Returns:
        - average_daily_return (float): The mean of daily returns.
        - std_daily_return (float): Standard deviation of daily returns.
        - integral (float): Percentage of days the strategy ended with less than $1.
        - nb_of_useless_days (int): Number of days that had no profitable returns.
        - total_dollar (float): Final amount of capital after applying the daily percentage returns.
        - total_dollar_frac (float): Final amount of capital after applying fractional daily returns.
        - total_top_up (float): Final capital in the top-up strategy after adjustments.
        - total_add_dollar (float): Final capital in the daily dollar addition strategy after adjustments.
    """

    # Initialize variables for storing results and tracking the investment process
    list_return = []
    list_mean_return = []
    current_holdings = []
    nb_of_useless_days = 0
    total_dollar = 1  # Starting capital in dollars
    total_dollar_frac = 1  # Fractional investment strategy starting amount
    total_top_up = 1  # Starting amount for top-up strategy
    additional_investment_top_up = 0  # To track extra amount needed for maintaining strategy
    total_add_dollar = 1  # Starting amount for adding $1 daily strategy
    additional_investment_daily = 0  # Track total additional investment for daily $1 strategy

    all_dates = sorted(set(list(df['Date'])))
    condition_order = list(condition_params.keys())
    for a_date in all_dates[starting:exiting]:
        df_date = df[(df['Date'] == a_date)]
        result_df = STF.apply_conditions(df_date, condition_params, condition_order)
        inves_return = STF.when_to_exit(result_df, limit=limit, condition=exit_condition)
        if inves_return == 0:
            nb_of_useless_days += 1

        decimal_return = inves_return / 100.0
        list_return.append(inves_return)

        # Update investment based on the day's return
        total_dollar *= (1 + decimal_return)
        total_dollar_frac = total_dollar_frac * 0.50 + total_dollar_frac * 0.50 * (1 + decimal_return)

        # Top-up strategy to maintain a minimum of $1
        if total_top_up * (1 + decimal_return) < 1:
            additional_investment_top_up += 1 - (total_top_up * (1 + decimal_return))
            total_top_up = 1
        else:
            total_top_up *= (1 + decimal_return)
        current_holdings.append(total_top_up - additional_investment_top_up)

        # Invest an additional dollar every day
        additional_investment_daily += 1
        total_add_dollar += (1 + decimal_return)

        # Calculate running mean of returns
        list_mean_return.append(np.mean(list_return))

    # Calculate overall statistics of the strategy
    average_daily_return = np.mean(list_return)
    std_daily_return = np.std(list_return)
    integral_of_values_less_than_1 = sum(value for value in current_holdings if value < 1)
    integral_of_values_more_than_1 = sum(value for value in current_holdings if value > 1)
    if integral_of_values_less_than_1 + integral_of_values_more_than_1 == 0:
        integral = 0
    else:
        integral = integral_of_values_less_than_1 / (integral_of_values_less_than_1 + integral_of_values_more_than_1) * 100

    return average_daily_return, std_daily_return, integral, nb_of_useless_days, total_dollar, total_dollar_frac, \
           total_top_up - additional_investment_top_up, total_add_dollar - additional_investment_daily


# Load stock data from CSV file
path_to_csv = "/Users/yannsakref/Dev/Stocks/Data/Healt_Tech_1Y_1h_19May.csv"
df = pd.read_csv(path_to_csv)

# Define conditions for strategy, this is an example
# The name of the columns are given in the csv file.
conditions = ['None', 'Superior to 0', 'Inferior to 0']
all_cols = ['Change Previous Day', 'Change Previous 9 to 10', 'Change 7 Days', 'Change 28 Days']
all_combinations = list(itertools.product(conditions, repeat=len(all_cols)))  # Generate all combinations of conditions
condition_params = {}  # Dictionary to hold conditions and their parameters

# Fill the condition_params dictionary based on combinations
for idx, combination in enumerate(all_combinations):
    if combination == ('None', 'None', 'Superior to 0', 'None'): # just try on one combination for testing
        one_condition = []
        condition_params = {}
        for col, cond in zip(all_cols, combination):
            one_condition.append(cond)
            if cond == 'None':
                condition_params[col] = (STF.c_col_inf_sup, (col, -1000, 1000))
            elif cond == 'Superior to 0':
                condition_params[col] = (STF.c_col_inf_sup, (col, 0, 1000))
            elif cond == 'Inferior to 0':
                condition_params[col] = (STF.c_col_inf_sup, (col, -1000, 0))

        # Define more complex conditions
        condition_params['Minimal Price'] = (STF.c_col_inf_sup, ("Price Previous Day", 30, 100))
        condition_params['Minimal Change'] = (STF.c_col_inf_sup, ('Change Previous Day', -100, 60))

        # # Soft Conditions -> Use to select the stocks. Here, e.g., you will end up with 2 stocks
        condition_params['Largest Change'] = (STF.c_largest_change, (4, 'Change Previous Day'))
        condition_params['Smallest Change'] = (STF.c_smallest_change, (2, 'Change Previous Day'))

        # Try the strategy
        first, slit = 0, 400
        average_daily_return, std_daily_return, integral, nb_of_useless_days, return_comp, return_comp_frac, return_top_up, \
        return_daily_inv = apply_strategy(df=df, condition_params=condition_params,
                                          starting=first, exiting=first + slit, limit=-2,
                                          exit_condition=True)
        print("")
        print("Daily Return", average_daily_return)
        print("Return Top-Up Strategy: ", return_top_up)
        print("")


# Set up for plotting the investment returns over time
## Define order of conditions and retrieve unique sorted dates from the DataFrame
condition_order = list(condition_params.keys())
all_dates = sorted(set(list(df['Date'])))

## Initialize lists to store returns and mean returns over time
list_return = []
list_mean_return = []

## Initialize variables for the top-up investment strategy
total_top_up = 1  # Start with $1
additional_investment_top_up = 0  # Track additional investment needed for maintaining minimum balance
current_holdings = []  # Track the effective balance after each day's transaction
additional_inv = []  # Track the additional investment made each day


## Additional variables for another top-up strategy
total_top_up_2 = 1
additional_investment_top_up_2 = 0
previous_return_positive = True  # Assume first day's return is positive to initialize investment

# Iterate over the specified date range
for a_date in all_dates[first:first + slit]:
    df_date = df[(df['Date'] == a_date)]
    result_df = STF.apply_conditions(df_date, condition_params, condition_order)
    inves_return = STF.when_to_exit(result_df, limit=-2, condition=True)
    decimal_return = inves_return / 100.0
    list_return.append(inves_return)

    # Apply top-up strategy: if balance falls below $1, top up to maintain $1 balance
    if total_top_up * (1 + decimal_return) < 1:
        additional_investment_top_up += 1 - (total_top_up * (1 + decimal_return))
        total_top_up = 1
    else:
        total_top_up *= (1 + decimal_return)

    current_holdings.append(total_top_up - additional_investment_top_up)
    additional_inv.append(additional_investment_top_up)

    # Calculate the running mean of returns for visualization
    list_mean_return.append(np.mean(list_return))

average_daily_return = np.mean(list_return)

# Plot the effective balance over time
plt.figure(figsize=(10, 5))  # Set the figure size
plt.plot(current_holdings, lw=3, color='#1f77b4')  # Plot the balance data
plt.plot(list_return, lw=1, color='black')  # Plot the balance data
plt.axhline(y=1, color='red', ls="dashed")
plt.xlabel("Days", size=20)  # Label x-axis
plt.ylabel("Return (%)", size=20)  # Label y-axis
# plt.yscale("symlog")
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.xticks(size=17)  # Set size of x-axis tick labels
plt.yticks(size=17)  # Set size of y-axis tick labels
plt.show()  # Display the plot
