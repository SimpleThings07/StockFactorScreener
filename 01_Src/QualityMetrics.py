# encoding: utf-8

# Copyright (c) Ivan Antunović (ivantun05@gmail.com) - All rights reserved.
# Unintended redistribution can be punishable by law.
# By reading this message, you are automatically consenting to it
# and you are accepting that the financial data might be incorrect.
# The financial data generated by this script is for informational purposes only
# and should not be considered as investment advice.
# Use at your own risk.

from EarningsEngine import Earnings


# ---------------------- Classes for Quality Metrics ----------------------

# Quality Score Calculation from "Size Matters if You Control Your Junk" by Asness, Frazzini, and Pedersen

# To avoid data mining, the authors base their measures on their theoretical model 
# using standard “off-the-shelf” empirical measures to compute three composite 
# quality measures: Profitability, Growth, and Safety.

# These three quality components are averaged to compute a single overall quality score.
# Results are described as qualitatively robust to the specific choices of factors.

# Profitability:
# Theoretical intuition suggests that profitability should be measured as the 
# “sustainable” part of profits in relation to book value, adjusted for accruals. 
# Empirically, several profitability measures are averaged to reduce noise and focus on sustainability:
# - Gross Profits over Assets (GPOA)
# - Return on Equity (ROE)
# - Return on Assets (ROA)
# - Cash Flow over Assets (CFOA)
# - Gross Margin (GMAR)
# - Accruals (ACC)
# 
# To ensure all metrics are on equal footing, each month the authors convert each variable 
# into ranks and standardize them to obtain a z-score.
# The z-score for a variable x is calculated as:
# z(x) = (r - μ_r) / σ_r
# where:
# - r is the vector of ranks
# - μ_r is the cross-sectional mean of the ranks
# - σ_r is the standard deviation of the ranks.
# 
# Profitability score is the average of the individual z-scores for the measures listed above:
# Profitability = z(z_gpoa + z_roe + z_roa + z_cfoa + z_gmar + z_acc)

# Growth:
# Growth is measured as the five-year growth in profitability (excluding accruals).
# Five-year growth is calculated as the change in the numerator (e.g., profits) 
# divided by the lagged denominator (e.g., assets).
# The five growth measures calculated are:
# - Five-year growth in GPOA
# - Five-year growth in ROE
# - Five-year growth in ROA
# - Five-year growth in CFOA
# - Five-year growth in GMAR
# 
# The growth score is the average of the z-scores of these five metrics:
# Growth = z(z_Δgpoa + z_Δroe + z_Δroa + z_Δcfoa + z_Δgmar)

# Safety:
# Safety is defined as a measure of financial stability and low risk.
# The metrics considered include:
# - Low beta (BAB)
# - Low leverage (LEV)
# - Low bankruptcy risk (O-Score and Z-Score)
# - Low ROE volatility (EVOL)
# 
# The safety score is calculated as the average of the z-scores of the above metrics:
# Safety = z(z_bab + z_lev + z_o + z_z + z_evol)

# Quality Score:
# The three measures are combined into a single composite quality score:
# Quality = z(Profitability + Growth + Safety)

# Missing Data Handling:
# To construct the composite quality measure as well as the individual subcomponents,
# the authors use all available information. If a particular measure is missing due to
# lack of data availability, the remaining available measures are averaged instead.

# Robustness Tests:
# The authors conducted robustness tests, including using raw values rather than ranks.



# Value metrics as described in  MSCI Value Weighted Methodology:
# 
#    - Book Value per Share (P/B Ratio)
#    - Sales Value (3-year average Sales per Share)
#    - Earnings Value (3-year average Earnings per Share)
#    - Cash Earnings Value (3-year average Cash Flow per Share)
#    
#    https://www.msci.com/eqb/methodology/meth_docs/MSCI_Value_Weighted_Index_Methodology_Book_May2012.pdf
#
class ValueMetrics:
    def __init__(self, price_to_book, price_to_earnings):
        #self.book_value_to_price = None      #
        #self.earnings_to_price = None        # 
        #self.sales_value = None              # 
        #self.cash_earnings_value = None      #
        self.price_to_book = price_to_book                # Book Value per Share (P/B Ratio)
        self.price_to_earnings = price_to_earnings        # Price to Earnings    (P/E Ratio)


# Classes for storing quality metrics as described in Asness, Frazzini, and Pedersen (2014)
# Each metric is initialized as None and can be populated later using financial data
class ProfitabilityMetrics:

    ticker = None
    earnings = None
    gpoa_ttm = None
    gpmar_ttm = None
    roe_ttm = None
    roa_ttm = None
    cfoa = None
    accruals = None

    def __init__(self, ticker : str, earnings : Earnings, gpoa : float, gpmar : float , roe : float, roa : float, cfoa : list, accruals):
        
        self.ticker = ticker
    
        # Profitability metrics include gross profit, margins, return on equity, return on assets,
        # cash flow over assets, and accruals

        self.earnings = earnings            # Earnings data object containing EPS, Net Income, and growth rates

        # Profitability metrics as described in Asness, Frazzini, and Pedersen (2014)
        self.gpoa = gpoa            # Gross profits over assets (GPOA)
        self.gpmar = gpmar          # Gross Profit margin (GPMAR)
        self.roe = roe              # Return on equity (ROE)
        self.roa = roa              # Return on assets (ROA)
        self.cfoa = cfoa            # Cash Flow over Assets (CFOA)

        self.accruals = accruals    # Accruals (ACC)


class GrowthMetrics:
    def __init__(self, earnings_growth, gpoa_growth, roe_growth, roa_growth, cfoa_growth, gpmar_growth):
        # Growth metrics include the five-year growth rates for profitability measures
        self.earnings_growth = earnings_growth   # Five-year growth in Earnings                      +

        # Profitability metrics as described in Asness, Frazzini, and Pedersen (2014)
        self.gpoa_growth = gpoa_growth           # Five-year growth in Gross Profits over Assets         +
        self.roe_growth = roe_growth             # Five-year growth in Return on Equity
        self.roa_growth = roa_growth             # Five-year growth in Return on Assets
        self.cfoa_growth = cfoa_growth           # Five-year growth in Cash Flow over Assets
        self.gpmar_growth = gpmar_growth         # Five-year growth in Gross Profit Margin


class SafetyMetrics:
    def __init__(self):
        # Safety metrics focus on risk and financial stability
        self.leverage = None  # Leverage (LEV)
        self.beta = None  # Market beta (BAB)
        self.bankruptcy_risk = None  # O-Score or Z-Score
        self.roe_volatility = None  # Volatility of Return on Equity (ROE)