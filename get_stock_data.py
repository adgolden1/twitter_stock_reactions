# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 20:32:05 2021

@author: AlexGolden
"""

import numpy as np
from datetime import datetime, timedelta
import requests
import pandas as pd
import time
import logging
import matplotlib.pyplot as plt
from searchtweets import load_credentials, gen_request_parameters, collect_results, ResultStream, write_result_stream
import os.path
import yfinance as yf
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

search_args = load_credentials(
    filename="twitter_keys.yaml", yaml_key="search_tweets_v2", env_overwrite=False
)

count_args = load_credentials(
    filename="twitter_keys_count.yaml", yaml_key="count_tweets_v2", env_overwrite=False
)
log = logging.getLogger(__name__)

bearer_token_path = 'C:\\Users\\AlexGolden\\Dropbox (BOSTON UNIVERSITY)\\twitter_stocks_project\\bearer_token.txt'

with open(bearer_token_path) as fp:
    bearer_token = fp.read()
    
dtformat = '%Y-%m-%dT%H:%M:%SZ'
dtformat_st = '%Y%m%d%H%M'
    
def get_data(tweet):
    data = {
        'id': tweet['id'],
        'created_at': tweet['created_at'],
        'text': tweet['text']
    }
    return data

def gather_tweets_st(search_term,start_time,end_time):
    if type(start_time) is datetime:
        start_time = start_time.strftime(dtformat_st)
    if type(end_time) is datetime:
        end_time = end_time.strftime(dtformat_st)
    
    query = gen_request_parameters(search_term, results_per_call=500, start_time=start_time,tweet_fields = "id,created_at,text", end_time=end_time,granularity = None)
    
    tweets = collect_results(query,
                         max_tweets=500,
                         result_stream_args=search_args)
   
    return tweets
        
def count_tweets_st(search_term,start_time,end_time):
    if type(start_time) is datetime:
        start_time = start_time.strftime(dtformat_st)
    if type(end_time) is datetime:
        end_time = end_time.strftime(dtformat_st)
    
    query = gen_request_parameters(search_term, start_time=start_time, end_time=end_time,granularity = None)
    
    counts = collect_results(query,
                         max_tweets=500,
                         result_stream_args=count_args)
   
    return counts

def get_tweet_counts_timerange_st(search_term,query_endtime,increment,num_queries):
    '''    
    Parameters
    ----------
    search_term : string
        the term to search twitter for.
    query_endtime : datetime
        the datetime at the end of the seach window.
    increment : timedelta
        the datetime increment for each individual search.
    num_queries : integer
        the number of searches to do/number of time increments

    Returns
    -------
    pandas dataframe
    
    outline:
        attempt to submit the query
        check for rate-limiting or error output
        sleep and try again if we got a bad result

    '''
    df = pd.DataFrame()
    for i in range(num_queries):
        query_start = query_endtime - increment
        
        end_time = query_endtime.strftime(dtformat_st)
        start_time = query_start.strftime(dtformat_st)
        
        # get the query response
        response = count_tweets_st(search_term,start_time,end_time)
        time.sleep(1)
        if not response:
            continue
        for tweet in response[0]['data']:
            if tweet['text'][:2] != 'RT':
                row = get_data(tweet)
                df = df.append(row,ignore_index = True)
        query_endtime = query_start
    return df

def get_tweets_timerange_st(search_term,query_endtime,increment,num_queries):
    '''    
    Parameters
    ----------
    search_term : string
        the term to search twitter for.
    query_endtime : datetime
        the datetime at the end of the seach window.
    increment : timedelta
        the datetime increment for each individual search.
    num_queries : integer
        the number of searches to do/number of time increments

    Returns
    -------
    pandas dataframe
    
    outline:
        attempt to submit the query
        check for rate-limiting or error output
        sleep and try again if we got a bad result

    '''
    df = pd.DataFrame()
    for i in range(num_queries):
        query_start = query_endtime - increment
        
        end_time = query_endtime.strftime(dtformat_st)
        start_time = query_start.strftime(dtformat_st)
        
        # get the query response
        response = gather_tweets_st(search_term,start_time,end_time)
        time.sleep(1)
        if not response:
            # print('No response')
            continue
        else:
            
            # print('response length:',len(response[0]['data']))
            pass
        RT_count = 0
        for tweet in response[0]['data']:
            if tweet['text'][:2] != 'RT':
                row = get_data(tweet)
                df = df.append(row,ignore_index = True)
            else:
                RT_count += 1
        # print('removed ',RT_count,'RTs')
        query_endtime = query_start
    return df

def get_tweets_from_ticker(ticker,days):
    search_term = '($'+ticker+') (lang:en)'
    df = pd.DataFrame()
    endtime = datetime.now()
    for i in range(days):
        if (i%(days//10)) == 0:
            print(i/days*100,'% done')
        tweets = get_tweets_timerange_st(search_term,endtime,timedelta(minutes = 60),24)
        if not tweets.empty:
            df = df.append(tweets)
        endtime = endtime - timedelta(days = 1)
    return df

def get_snp_ticker_tweets():
    sp100_df = pd.read_csv('s_and_p_100.csv')
    path = 'C:\\Users\\AlexGolden\\Dropbox (BOSTON UNIVERSITY)\\twitter_stocks_project\\Tweets_CSVs\\'
    tickerlist = list(sp100_df['Symbol'])
    for ticker in tickerlist:
        print('now getting tweets from ticker: ',ticker)
        ticker_csvname = path+ticker+'tweets.csv'
        if not os.path.isfile(ticker_csvname):
            ticker_df = get_tweets_from_ticker(ticker,50)
            print('number of entries:',len(ticker_df))
            ticker_df = label_tweets_inline(ticker,ticker_df)
            ticker_df = ticker_df.reset_index()[['created_at', 'id', 'text', 'slope_labels']]
            ticker_df.to_csv(ticker_csvname)
        else:
            print('ticker ',ticker,'found, skipping')
            
def get_prices_prev_day(ticker_df,final_datetime,db_dt = 30*60):
    # final datetime should be in datetime objects
    # db_dt is the sampling frequency of the database in seconds
    # print(final_datetime,type(final_datetime))
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

def generate_ticker_db(symbol,first_dt,last_dt):
    # symbol should be a string
    # first_dt & last_dt should be dates of the earliest and latest times we need (not including times within the day)
    # they should be strings of the form "YYYY-MM-DD"
    # note: last_dt should be the day following the last day
    # this probably isn't that necessary though, it seems like getting the ticker history directly is easy enough
    tick = yf.Ticker(symbol)
    ticker_db = tick.history(interval = '30m',start = first_dt,end = last_dt)
    return ticker_db

def inc_or_dec_prices(ticker_db,dt):
    # function for returning 0 or 1 based on whether the price data for a specific ticker increases or decreases
    # datetime should be a datetime object corresponding to a tweet
    prices = get_prices_prev_day(ticker_db,dt).to_numpy()
    idxs = np.arange(prices.size)
    reg = LinearRegression().fit(idxs.reshape(-1,1), prices.reshape(-1,1))
    slope = reg.coef_[0,0]
    return np.heaviside(slope,0.5)

def label_tweets_inline(ticker_str,tweets):
    start_time = (datetime.now()-timedelta(days = 59)).strftime('%Y-%m-%d')
    end_time = (datetime.now()).strftime('%Y-%m-%d')
    if '.' in ticker_str:
        ticker_str = ticker_str.replace('.','-')
    ticker = yf.Ticker(ticker_str)
    ticker_db = ticker.history(interval = '30m',start = start_time,end = end_time)
    slope_labels = np.zeros(tweets['created_at'].shape)
    mintime = (datetime.now()-timedelta(days = 59)).timestamp()
    for i in range(slope_labels.size):
        dt = datetime.strptime(tweets.iloc[i]['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
        # current = (df['created_at'].min()-timedelta(days = 2)+timedelta(days = 58) < datetime.now(df['created_at'].min().tzinfo))
        if (dt-timedelta(days = 2)).timestamp() > mintime:
            slope_labels[i] = inc_or_dec_prices(ticker_db,dt)
        else:
            slope_labels[i] = np.nan
    tweets['slope_labels'] = slope_labels
    return tweets
    

def label_tweets(ticker_str):
    '''

    Parameters
    ----------
    ticker : string
        twitter cashtag for given s&p100 company. Of the form 'XXX'.

    Returns
    -------
    None.
    
    Loads tweet csv for a given ticker, annotates each tweet entry with
    whether or not the stock went up or down in the previous 6 hours, and
    re-saves the tweet csv

    '''
    tweet_csv_fname = ticker_str+'tweets.csv'
    df = pd.read_csv(tweet_csv_fname, parse_dates=['created_at'])
    start_time = (datetime.now()-timedelta(days = 59)).strftime('%Y-%m-%d')
    end_time = (datetime.now()).strftime('%Y-%m-%d')
    if '.' in ticker_str:
        ticker_str = ticker_str.replace('.','-')
    
    print('now labelling:',ticker_str)
    ticker = yf.Ticker(ticker_str)
    ticker_db = ticker.history(interval = '30m',start = start_time,end = end_time)
    slope_labels = np.zeros(df['created_at'].shape)
    mintime = (datetime.now()-timedelta(days = 59)).timestamp()
    for i in range(slope_labels.size):
        dt = df.iloc[i]['created_at']
        # current = (df['created_at'].min()-timedelta(days = 2)+timedelta(days = 58) < datetime.now(df['created_at'].min().tzinfo))
        if (dt-timedelta(days = 2)).timestamp() > mintime:
            slope_labels[i] = inc_or_dec_prices(ticker_db,df.iloc[i]['created_at'])
        else:
            slope_labels[i] = np.nan
    df['slope_labels'] = slope_labels
    df.to_csv(tweet_csv_fname)
    return None

def label_snp100():
    sp100_df = pd.read_csv('s_and_p_100.csv')
    tickerlist = list(sp100_df['Symbol'])
    for ticker in tickerlist:
        label_tweets(ticker)
    