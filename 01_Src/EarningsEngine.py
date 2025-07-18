# encoding: utf-8

# Copyright (c) Ivan Antunović (ivantun05@gmail.com) - All rights reserved.
# Unintended redistribution can be punishable by law.
# By reading this message, you are automatically consenting to it
# and you are accepting that the financial data might be incorrect.
# The financial data generated by this script is for informational purposes only
# and should not be considered as investment advice.
# Use at your own risk.


# Standard Python Modules
import math
import pandas as pd    # Data Manipulation Module
import numpy as np     # Data Manipulation Module

# Local Modules
from AlphaVantageHelper import fetch_earnings_alpha_vantage



# ---------------------- Custom Exceptions ----------------------

class EPSCalcError (Exception):
    """
        Custom exception for errors in Earnings per Share (EPS) calculation.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class NetIncomeCalcError (Exception):
    """
        Custom exception for errors in Net Income calculation.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class EVARCalcError (Exception):
    """
        Custom exception for errors in Earnings Variability (EVAR) calculation.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class EarningsGrowthCalcError(Exception):
    """Custom exception for errors in Earnings Growth calculation."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message



# ---------------------- Earnings Class ----------------------

class Earnings:

    """
    Class to hold Earnings data for a stock, including EPS and Net Income.
    This class is used to store and manage earnings data for financial analysis and screening.
    It includes attributes for Earnings per Share (EPS) and Net Income, along with their growth rates and variability.

    Attributes:
        - eps_list: List of Earnings per Share (EPS) annual values for different years.
        - eps_growth_list: List of EPS growth values year-on-year.
        - eps_evar: Earnings Variability (EVAR) for EPS, calculated as the standard deviation of EPS growth.
        - eps_cagr: Compound Annual Growth Rate (CAGR) for EPS, calculated over the specified period.
        - net_income_list: List of Net Income annual values for different years.
        - net_income_growth_list: List of Net Income growth values year-on-year.
        - net_income_evar: Earnings Variability (EVAR) for Net Income, calculated as the standard deviation of Net Income growth.
        - net_income_cagr: Compound Annual Growth Rate (CAGR) for Net Income, calculated over the specified period.

    """

    # EPS data
    eps_list = None
    eps_growth_list = None
    eps_evar = None
    eps_cagr = None  # Compound Annual Growth Rate (CAGR) for EPS

    # Net Income data
    net_income_list = None
    net_income_growth_list = None
    net_income_evar = None
    net_income_cagr = None  # Compound Annual Growth Rate (CAGR) for Net Income


    def __init__(self, eps_list, eps_growth_list, eps_evar, eps_cagr, net_income_list, net_income_growth_list, net_income_evar, net_income_cagr ):
        
        # EPS data
        self.eps_list = eps_list
        self.eps_growth_list = eps_growth_list
        self.eps_evar = eps_evar
        self.eps_cagr = eps_cagr  # Compound Annual Growth Rate (CAGR) for EPS

        # Net Income data
        self.net_income_list = net_income_list
        self.net_income_growth_list = net_income_growth_list
        self.net_income_evar = net_income_evar
        self.net_income_cagr = net_income_cagr  # Compound Annual Growth Rate (CAGR) for Net Income


# ---------------------- Function definitions ----------------------

def get_net_income (stock, ticker, reporting_period='TTM'):
    """
    Fetches the net income from the quarterly financials as TTM or latest annual net income.
    Net income is the total profit of a company after all expenses, taxes, and costs have been deducted from total revenue.
    It is calculated as Revenues - COGS - SGA - Interest - Taxes = Net Income.

    Parameters:
        stock (object): The stock object containing financial data.
        ticker (str): The stock ticker symbol.
        reporting_period (str): The reporting period, either 'TTM' (Trailing Twelve Months) or 'Annual'.

    Returns:
        net_income (float): The net income for the specified reporting period.

    Raises:
        ValueError: If required Net Income data is missing or insufficient for the requested period.
    """
    
    net_income = None


    if 'ttm' == reporting_period.lower():

        # Fetch Quarterly Income Statement data
        income_statement_quart = stock.quarterly_financials.T  # Transpose to have dates as rows

        # Check if 'Net Income' is available in the income statement
        if 'Net Income' not in income_statement_quart:
            raise ValueError (f"Cannot calculate Net Income TTM! Net Income data is missing in the Quarterly Income Statement (Ticker: {ticker}).")

        # Fetch the last 4 quarters of net income
        net_income_list = income_statement_quart['Net Income'].tolist()   # Convert to list for easier indexing

        # Remove all NaN values from the list
        net_income_list = [net_income for net_income in net_income_list if not pd.isna(net_income)]

        # Check if we have at least 4 quarters of data for TTM calculation
        if len(net_income_list) < 4:
            raise ValueError (f"Cannot calculate Net Income TTM! Not enough Net Income Quarterly data is available (Ticker: {ticker}). \n Data for at least 4 quarters is required .")
        
        # Calculate TTM Net Income from the last 4 quarters
        # Latest quarter is the 0th index in the list
        net_income_ttm = sum(net_income_list[:4])

        net_income = net_income_ttm


    elif 'annual' == reporting_period.lower():

        # Fetch the Annual Income Statement data
        income_statement_annual = stock.financials.T   # Transpose to have dates as rows

        # Check if 'Net Income' is available in the income statement
        if 'Net Income' not in income_statement_annual:
            raise ValueError (f"Cannot fetch Annual Net Income! Net Income data is missing in the Annual Income Statement (Ticker: {ticker}).")

        net_income_list = income_statement_annual['Net Income'].tolist()  # Convert to list for easier indexing

        # Remove all NaN values from the list
        net_income_list = [net_income for net_income in net_income_list if not pd.isna(net_income)]

        # Check if we have at least 1 year of annual data
        if len(net_income_list) < 1:
            raise ValueError (f"Cannot fetch Annual Net Income! No Net Income annual data is available in the Annual Income Statement (Ticker: {ticker}). \n Data for at least 1 year is required .") 
    
        # Get the latest annual net income
        # Latest annual net income is the 0th index in the list
        net_income = net_income_list[0]

    return net_income



def get_earnings (stock, ticker, earnings_type, earnings_period_req, av_api_key, av_base_url):
    """
        Get Earnings data (EPS or Net Income) from Yahoo Finance or Alpha Vantage for a specified earnings period.

        Parameters:
            - stock (yf.Ticker): A yfinance Ticker object representing the stock.
            - ticker (str): The stock ticker symbol.
            - earnings_period_req (int): The number of earnings periods (in years) requested.
            - earnings_type (str): The type of earnings data to fetch: "eps" for EPS, "net_income" for Net Income.
            - av_api_key (str): The Alpha Vantage API key.
            - av_base_url (str): The base URL for the Alpha Vantage API.

        Returns:
            - list: A list of Earnings data (EPS or Net Income) fetched from Yahoo Finance or Alpha Vantage

        Raises:
            NetIncomeCalcError: If annual income statement data is missing or Net Income is not found.
            EPSCalcError: If EPS data is missing or insufficient.
    """

    try:
        # Fetch Income Statement from Yahoo Finance
        income_statement_annual = stock.financials.T  # Annual financial data (transpose to get dates as rows)
        
        # Check if there is data in the income statement
        if income_statement_annual.empty:
            raise NetIncomeCalcError (f"No Annual Income Statement data found on Yahoo Finance (Ticker: {ticker}).")

        # ------------------- EPS -------------------
        if earnings_type == "eps":

            # Check if Basic EPS is available in the income statement
            if 'Basic EPS' in income_statement_annual.columns:
                
                eps_basic_annual_list = None
 
                # Extract the 'Basic EPS' data from the income statement
                eps_basic_annual_yf = income_statement_annual['Basic EPS']

                # Check if the fetched EPS list from Yahoo Finance is empty
                if eps_basic_annual_yf is None:
                    raise EPSCalcError (f"'Basic EPS' data from Yahoo Finance is empty or missing (Ticker: {ticker}).")

                # Convert the EPS data to a list
                eps_basic_annual_yf = eps_basic_annual_yf.tolist()

                # Remove 'nan' values from the EPS list
                eps_basic_annual_yf = [eps for eps in eps_basic_annual_yf if not math.isnan(eps)]

                # Ensure there's enough earnings data for the requested periods
                if len(eps_basic_annual_yf) >= earnings_period_req:

                    # Set the EPS list to the Yahoo Finance data for the requested periods
                    eps_basic_annual_list = eps_basic_annual_yf[:earnings_period_req]

                # If there are fewer earnings periods than requested
                elif len(eps_basic_annual_yf) < earnings_period_req:
                    # logging.warning(f"Not enough 'Basic EPS' data available (Ticker: {ticker}) on Yahoo Finance. Need at least {earnings_period_req} earning periods.")
                    # logging.warning(f"Fetching from a fallback data source.")

                    # Fallback to Alpha Vantage to fetch EPS data
                    eps_basic_annual_av = fetch_earnings_alpha_vantage (
                        av_api_key, 
                        av_base_url, 
                        ticker, 
                        "eps",
                        "annual"
                    )

                    # Check if the fetched EPS list from Alpha Vantage is empty
                    if eps_basic_annual_av is None:

                        # logging.warning(f"'Basic EPS' data from 'Alpha Vantage' is empty or missing (Ticker: {ticker}).")
                        
                        # logging.warning(f"Using Yahoo Finance data as fallback.")

                        # If the Alpha Vantage data is empty, then at least return the Yahoo Finance data
                        return eps_basic_annual_yf

                    # Remove 'nan' values from the Alpha Vantage EPS list
                    eps_basic_annual_av = [eps for eps in eps_basic_annual_av if not math.isnan(eps)]

                    # Check if Alpha Vintage dataset is bigger than Yahoo Finance
                    # If so, use the Alpha Vantage data
                    if len(eps_basic_annual_av) > len(eps_basic_annual_yf):

                        # Ensure there's enough earnings data for the requested periods
                        if len(eps_basic_annual_av) >= earnings_period_req:

                            # Set the EPS list to the Alpha Vantage data for the requested periods
                            eps_basic_annual_list = eps_basic_annual_av[:earnings_period_req]

                        # If there's not enough requested data, use the available data
                        else:
                            # Get the number of available data points
                            earnings_available_cnt = len(eps_basic_annual_av)
                            # Set the EPS list to the available data
                            eps_basic_annual_list = eps_basic_annual_av[:earnings_available_cnt]

                    # If not, use the Yahoo Finance data
                    else:
                        eps_basic_annual_list = eps_basic_annual_yf

                # Return the 'Basic EPS' list
                return eps_basic_annual_list

            # If 'Basic EPS' data is not available in the income statement
            else:
                raise EPSCalcError (f"Cannot find 'Basic EPS' data for {ticker}.")


        # ------------------- Net Income -------------------
        elif earnings_type == "net_income":

            if 'Net Income' in income_statement_annual.columns:

                net_income_annual_list = None

                # Extract the 'Net Income' data from the income statement
                net_income_annual_yf = income_statement_annual['Net Income']

                if net_income_annual_yf is None:
                    raise NetIncomeCalcError (f"'Net Income' data from Yahoo Finance is empty or missing (Ticker: {ticker}).")

                # Convert the Net Income data to a list
                net_income_annual_yf = net_income_annual_yf.tolist()

                # Remove 'nan' values from the Net Income list
                net_income_annual_yf = [net_income for net_income in net_income_annual_yf if not math.isnan(net_income)]

                # Ensure there's enough earnings data for the requested periods
                if len(net_income_annual_yf) >= earnings_period_req:

                    # Set the earnings_annual_list to the Net Income list for the requested periods
                    net_income_annual_list = net_income_annual_yf[:earnings_period_req]

                # Ensure there's enough earnings data for the specified periods (minimum 3)
                elif len(net_income_annual_yf) < earnings_period_req:
                    # logging.warning(f"Not enough 'Net Income' data available (Ticker: {ticker}) on Yahoo Finance. Need at least {earnings_period_req} earning periods.")
                    # logging.warning(f"Fetching from a fallback data source.")

                    # Fallback to Alpha Vantage to fetch Net Income data
                    net_income_annual_av = fetch_earnings_alpha_vantage (
                        av_api_key, 
                        av_base_url, 
                        ticker,
                        "net_income",
                        "annual"
                    )

                    # Check if the fetched Net Income list from Alpha Vantage is empty
                    if net_income_annual_av is None:
                        # logging.warning(f"'Net Income' data from 'Alpha Vantage' is empty or missing (Ticker: {ticker}).")
                        
                        # logging.warning(f"Using Yahoo Finance data as fallback.")

                        # If the Alpha Vantage data is empty, then at least return the Yahoo Finance data
                        return net_income_annual_yf
                    
                    # Remove 'nan' values from the Alpha Vantage Net Income list
                    net_income_annual_av = [net_income for net_income in net_income_annual_av if not math.isnan(net_income)]
                    
                    # Check if Alpha Vintage dataset is bigger than Yahoo Finance
                    # If so, use the Alpha Vantage data
                    if len(net_income_annual_av) > len(net_income_annual_yf):

                        # Ensure there's enough earnings data for the requested periods
                        if len(net_income_annual_av) >= earnings_period_req:

                            # Set the Net Income list to the Alpha Vantage data for the requested periods
                            net_income_annual_list = net_income_annual_av[:earnings_period_req]

                        # If there's not enough requested data, use the available data
                        else:
                            # Get the number of available data points
                            earnings_available_cnt = len(net_income_annual_av)
                            # Set the Net Income list to the available data
                            net_income_annual_list = net_income_annual_av[:earnings_available_cnt]
                    
                    # If not, use the Yahoo Finance data
                    else:
                        net_income_annual_list = net_income_annual_yf

                # Set the earnings_annual_list to the Net Income list
                o_earnings_annual_list = net_income_annual_list

                # Return the 'Net Income' list
                return o_earnings_annual_list

            else:
                raise NetIncomeCalcError (f"Cannot find 'Net Income' data for {ticker}.")

    except Exception as exc:
        raise NetIncomeCalcError(f"Error fetching Earnings ({ticker}): {exc}") from exc



def calc_eps_ttm (stock, ticker, trailing_eps_quarters=4):
    """
    Calculate Trailing 12-Month EPS (TTM) for a given stock.

    Parameters:
        - stock (yfinance.Ticker): The stock object fetched using yfinance.
        - ticker (str): The stock ticker symbol for logging purposes.
        - trailing_eps_quarters (int): Number of trailing quarters to calculate EPS TTM (default is 4 quarters).

    Returns:
        - float: The trailing 12-month EPS value, or None if data is insufficient or unavailable.

    Raises:
        EPSCalcError: If EPS data is missing or insufficient for the requested quarters.
    """
    
    o_trailing_eps = 0

    try:
        # Get quarterly income statement data
        income_statement = stock.quarterly_financials.T  # Transpose to have dates as rows

        # Check if Basic EPS is available in the income statement
        if 'Basic EPS' not in income_statement.columns:
            raise EPSCalcError (f"Cannot calculate Trailing EPS! EPS data is missing (Ticker: {ticker}).")

        # Get the Basic EPS data and clean 'nan' values
        basic_eps_list = income_statement['Basic EPS'].tolist()
        basic_eps_list = [eps for eps in basic_eps_list if not math.isnan(eps)]

        # Check if there is enough data for the specified trailing quarters
        if len(basic_eps_list) < trailing_eps_quarters:
            raise EPSCalcError (f"Cannot calculate Trailing EPS! Not enough EPS data for the last {trailing_eps_quarters} quarters (Ticker: {ticker}).")

        # Calculate TTM EPS by summing up the latest trailing quarters of EPS data
        o_trailing_eps = sum(basic_eps_list[:trailing_eps_quarters])

    except KeyError as exc:
        raise EPSCalcError (f"Cannot calculate Trailing EPS! EPS data is not available (Ticker: {ticker}).") from exc

    return o_trailing_eps



def calc_evar (ticker, earnings_growths_yoy):
    """
    Calculate Earnings Variability (EVAR), i.e. standard deviation, based on the MSCI methodology.
    MSCI calculates Earnings Variability as the standard deviation of year-on-year Earnings per Share (EPS) growth 
    in the last five fiscal years.

    The calculation is done over the period defined by evar_period (e.g., 5 years).
    If there are fewer periods than requested, the function uses the available periods.

    MSCI calculates Earnings Variability as the standard deviation of year-on-year Earnings per Share (EPS) growth.

    Formula:
        EVAR = sqrt( Σ( (EPS_g_i - EPS_g_m)^2 ) / (n - 1) )

    Where:
        - EPS_g_i = (EPS_i - EPS_{i-1}) / EPS_{i-1} : Year-on-year EPS growth for the i-th year.
        - EPS_g_m = mean(EPS_g_i) : Mean of the year-on-year EPS growth rates.
        - n = number of EPS growth data points (e.g., 4 for 5 fiscal years).

    Parameters:
        - ticker (str): The stock ticker symbol.
        - evar_type (str): The source for the growth calculation: "eps" for EPS growth, "net_income" for Net Income growth.
    
    Returns:
        - float: The calculated Earnings Variability (EVAR) in fractions.

    Raises:
        EVARCalcError: If earnings growth data is missing, insufficient, or calculation fails.
    """

    EARNINGS_GROWTH_MIN_DATA_POINTS = 2


    if earnings_growths_yoy is None:
        raise EVARCalcError (f"Cannot calculcate EVAR. No Earnings Growth data available (Ticker: {ticker}).")

    earnings_growth_data_points_cnt = len(earnings_growths_yoy)

    # Check if there are enough earnings periods (data points) for EVAR calculation
    if earnings_growth_data_points_cnt < EARNINGS_GROWTH_MIN_DATA_POINTS:
        raise EVARCalcError(f"Not enough Earnings Growth data to calculate EVAR for {ticker}. At least {EARNINGS_GROWTH_MIN_DATA_POINTS} data points are required.")


    try:

        # Step 1: Calculate the mean of Earnings Growth (EPS or Net Income) 
        # The mean of EPS growth is calculated by averaging the EPS growth values over the period.
        #  - EPS_mean = sum(EPS_growth_1, EPS_growth_2, ..., EPS_growth_n) / n
        mean_earnings_growth = np.mean(earnings_growths_yoy)
        
        # Step 2: Calculate the variance of Earnings growth (for standard deviation)
        # Variance is calculated as:
        # Variance = ( (EPS_growth_1 - Mean_Growth)^2 + (EPS_growth_2 - Mean_Growth)^2 + ... + (EPS_growth_n - Mean_Growth)^2 ) / (n-1)
        # Where:
        # - EPS_growth_i = EPS growth for the i-th year
        # - Mean_Growth = The average EPS growth (calculated in Step 2)
        # - n = Number of periods (years)
        earnings_variance_sum = 0

        for earnings_growth in earnings_growths_yoy:
            # Calculate the sum of squared differences
            earnings_variance_sum += (earnings_growth - mean_earnings_growth) ** 2


        # Calculate the variance by dividing the sum of squared differences by the number of periods (N-1)
        variance = earnings_variance_sum / (earnings_growth_data_points_cnt - 1)
        
        # -------------------- Step 4: Calculate Earnings Variability (EVAR) --------------------
        # Earnings Variability (EVAR) is the square root of variance (Standard Deviation):
        # - EVAR = sqrt(Variance)
        evar_frac = np.sqrt(variance)
        
        # Return EVAR as a fraction
        return evar_frac
    
    except Exception as exc:
        raise EVARCalcError(f"Error calculating EVAR for {ticker}: {exc}") from exc



def calc_earnings_growth (ticker, earnings_list):

    """
    
    Calculate Earnings Growth using 'Basic EPS' or 'Net Income' from Yahoo Finance for a specified earnings period.

    http://fortmarinus.com/blog/1214/#edit-5374639318
    
    Parameters:
        - ticker (str): The stock ticker symbol.
        - earnings_list (list): A list of Earnings data (EPS or Net Income).

    Returns:
        - list: A list of Earnings Growth YoY values for a specified earnings period.

    Raises:
        EarningsGrowthCalcError: If earnings data is missing, insufficient, or calculation fails.
    """

    # Initialize the list to hold the calculated Earnings Growth YoY values
    o_earnings_growths = []

    # Minimum number of data points required for Earnings Growth calculation
    MIN_EARNINGS_DATA_POINTS = 2

    try:

        if earnings_list is None:
            raise EarningsGrowthCalcError (f"Cannot calculate Earnings Growth. No Earnings data available (Ticker: {ticker}).")

        # Check if there are enough earnings data points, else use the available data
        available_data_periods = len(earnings_list)

        # Check if there are enough earnings periods (data points) for Earnings Growth calculation
        if available_data_periods < MIN_EARNINGS_DATA_POINTS:
            raise EarningsGrowthCalcError (f"Not enough data to calculate Earnings Growth (Ticker: {ticker}). At least {MIN_EARNINGS_DATA_POINTS} periods are required.")

        # Calculate EPS Growth Year-on-Year (YoY) for each year
        #   The EPS growth is calculated as:
        #   EPS Growth = (EPS_i - EPS_(i+1)) / abs ( EPS_(i+1) )
        # Where:
        # - EPS_i = Earnings per share for the current year
        # - EPS_(i+1) = Earnings per share for the previous year
        #
        # Adjusting the denominator to the absolute value helps prevent misleading results.
        # For example, if the EPS for the previous year is negative,
        # but the EPS for the current year is postive,
        # then the growth rate would be mistakenly calculated as negative.
        #
        # For more details see: http://fortmarinus.com/blog/1214/#edit-5374639318
        for i in range(0, available_data_periods - 1):
            earnings_growth = (earnings_list[i] - earnings_list[i + 1]) / abs(earnings_list[i + 1])
            o_earnings_growths.append(earnings_growth)

        # Return the calculated Earnings Growth YoY List
        return o_earnings_growths

    except Exception as exc:
        raise EarningsGrowthCalcError(f"Error calculating Earnings Growth for {ticker}: {exc}") from exc
