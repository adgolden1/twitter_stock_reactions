# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 20:01:07 2021

@author: AlexGolden
"""

from datetime import datetime, timedelta
import requests
import pandas as pd
import time
import logging
import matplotlib.pyplot as plt
log = logging.getLogger(__name__)

bearer_token_path = '/projectnb2/biophys/goldalex/twitter/bearer_token.txt'

with open(bearer_token_path) as fp:
    bearer_token = fp.read()
    
dtformat = '%Y-%m-%dT%H:%M:%SZ'
    
def get_data(tweet):
    data = {
        'id': tweet['id'],
        'created_at': tweet['created_at'],
        'text': tweet['text']
    }
    return data

def gather_tweets(search_term,start_time,end_time):
    endpoint = 'https://api.twitter.com/2/tweets/search/all'
    headers = {'authorization': f'Bearer {bearer_token}'}
    params = {
    'max_results': '500',
    'tweet.fields':'created_at,lang'
    }
    params['query'] = search_term
    params['end_time'] = end_time
    params['start_time'] = start_time
    
    response = requests.get(endpoint,
                       params=params,
                       headers=headers)
   
    return response
        
def append_tweets(search_term, ending, num_queries, data_frame):
    
    remaining_calls = None
    reset_time = None
    
    for i in range(num_queries):
        end_temp = ending - timedelta(minutes = i*15)
        end_time = end_temp.strftime(dtformat)
        start_time = (end_temp - timedelta(minutes = 15)).strftime(dtformat)
        #print('start time = ', start_time)
        #print('end time = ', end_time)
        
        if (reset_time is not None and remaining_calls is not None 
            and remaining_calls < 1):
            
            sleep_time = int(reset_time) - int(time.time())
            if sleep_time > 0:
                log.warning(f"Rate limit reached. Sleeping for: {sleep_time}")
                time.sleep(sleep_time + 5)  # Sleep for an extra second
        
        response = gather_tweets(search_term,start_time,end_time)
        
        rem_calls = response.headers.get('x-rate-limit-remaining')
        if rem_calls is not None:
            remaining_calls = int(rem_calls)
        elif remaining_calls is not None:
            remaining_calls -= 1
            
        reset_time = response.headers.get('x-rate-limit-reset')
        if reset_time is not None:
            reset_time = int(reset_time)
        
        sleep_inc = 2
        while 'data' not in response.json().keys():
            log.warning(f'Rate limit detection error. Sleeping for: {sleep_inc} seconds')
            response = gather_tweets(search_term,start_time,end_time)
            if sleep_inc > 3600:
                log.warning('Rate limit recovery duration over 1 hr. Aborting.')
                return response
            sleep_inc = sleep_inc*2
            
        for tweet in response.json()['data']:
            if tweet['text'][:2] != 'RT':
                row = get_data(tweet)
                data_frame = data_frame.append(row,ignore_index = True)
        
        if i<num_queries-1: time.sleep(1) #wait 1 second for each iteration to avoid overloading
        
    return data_frame


end = datetime.now() - timedelta(days = 1)
df_tsla = pd.DataFrame()
df_tsla = append_tweets('($tsla) (lang:en)', end, 40000 ,df_tsla)
df_tsla.to_csv('/projectnb2/biophys/goldalex/twitter/twitter_df_tsla.csv')