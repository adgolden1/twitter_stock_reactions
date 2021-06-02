# -*- coding: utf-8 -*-
"""
Created on Mon May 31 17:05:30 2021

@author: AlexGolden
"""

import datetime
import yfinance as yf

def get_prices_prev_day(ticker_db,final_datetime):
    # final datetime should be in datetime objects
    final_datetime = final_datetime.replace(microsecond = 0)
    start_datetime = datetime.datetime.fromtimestamp(final_datetime.timestamp() - 24*60*60)
    start_datetime = start_datetime.replace(microsecond = 0)
    # just get the opening prices for that time period
    return ticker_db['Open'][str(start_datetime):str(final_datetime)]
    
    
    
def generate_ticker_db(symbol,first_dt,last_dt):
    # symbol should be a string
    # first_dt & last_dt should be dates of the earliest and latest times we need (not including times within the day)
    # they should be strings of the form "YYYY-MM-DD"
    # note: last_dt should be the day following the last day
    # this probably isn't that necessary though, it seems like getting the ticker history directly is easy enough
    tick = yf.Ticker(symbol)
    ticker_db = tick.history(interval = '30m',start = first_dt,end = last_dt)
    return ticker_db