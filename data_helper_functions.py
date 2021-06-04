# -*- coding: utf-8 -*-
"""
Created on Mon May 31 17:05:30 2021

@author: AlexGolden
"""

import datetime
import yfinance as yf
from sklearn.linear_model import LinearRegression
import numpy as np

def get_prices_prev_day(ticker_df,final_datetime,db_dt = 30*60):
    # final datetime should be in datetime objects
    # db_dt is the sampling frequency of the database in seconds
    final_datetime = final_datetime.replace(microsecond = 0)
    
    # get the index of the last entry before the tweet
    final_dt_idx = ticker_df.index.get_loc(ticker_df[ticker_df.index <= str(final_datetime)].iloc[-1].name)
    
    # get the index of the entry "one day" before the tweet
    # "one day" in quotes because it ignores time gaps like time between open/close, weekends, etc
    # a trading day is 6.5 hours long (9:30-4:00)
    one_day_idxs = int(3600*6.5/db_dt)
    start_dt_idx = final_dt_idx - one_day_idxs
    
    # just get the opening prices for that time period
    return ticker_df['Open'].iloc[start_dt_idx:final_dt_idx]
    
def get_vols_prev_day(ticker_df,final_datetime,db_dt = 30*60):
    # final datetime should be in datetime objects
    # db_dt is the sampling frequency of the database in seconds
    final_datetime = final_datetime.replace(microsecond = 0)
    
    # get the index of the last entry before the tweet
    final_dt_idx = ticker_df.index.get_loc(ticker_df[ticker_df.index <= str(final_datetime)].iloc[-1].name)
    
    # get the index of the entry "one day" before the tweet
    # "one day" in quotes because it ignores time gaps like time between open/close, weekends, etc
    # a trading day is 6.5 hours long (9:30-4:00)
    one_day_idxs = int(3600*6.5/db_dt)
    start_dt_idx = final_dt_idx - one_day_idxs
    
    # just get the opening prices for that time period
    return ticker_df['Volume'].iloc[start_dt_idx:final_dt_idx]
    
    
def generate_ticker_db(symbol,first_dt,last_dt):
    # symbol should be a string
    # first_dt & last_dt should be dates of the earliest and latest times we need (not including times within the day)
    # they should be strings of the form "YYYY-MM-DD"
    # note: last_dt should be the day following the last day
    # this probably isn't that necessary though, it seems like getting the ticker history directly is easy enough
    tick = yf.Ticker(symbol)
    ticker_db = tick.history(interval = '30m',start = first_dt,end = last_dt)
    return ticker_db

def inc_or_dec_prices(ticker_db,ticker,dt):
    # function for returning 0 or 1 based on whether the price data for a specific ticker increases or decreases
    # datetime should be a datetime object corresponding to a tweet
    prices = get_prices_prev_day(ticker_db,datetime).to_numpy()
    idxs = np.arange(prices.size)
    reg = LinearRegression().fit(idxs.reshape(-1,1), prices.reshape(-1,1))
    slope = reg.coef_[0,0]
    return np.heaviside(slope,0.5)
    