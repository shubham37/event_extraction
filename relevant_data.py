import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import time
import os
import sys
import nltk

class TwitterClient(object):

    def __init__(self):
        consumer_key = "XXXXXXXXXXXXXXXXXXXXX"
        consumer_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        access_token = "XXXXXXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXX"
        access_token_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        try:
            # create OAuthHandler object
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
            # for Lemmitization
            self.lemmatizer = nltk.WordNetLemmatizer()
            # For Steamization
            self.stemmer = nltk.stem.porter.PorterStemmer()
        except:
            print("Error: Authentication Failed")

    def tweet_search(self, query, max_tweets, max_id, since_id):

        searched_tweets = []
        while len(searched_tweets) < max_tweets:
            remaining_tweets = max_tweets - len(searched_tweets)
            try:
                new_tweets = self.api.search(q=query, count=remaining_tweets,
                                        since_id=str(since_id),
                                        max_id=str(max_id - 1))
                print('found', len(new_tweets), 'tweets')
                if not new_tweets:
                    print('no tweets found')
                    break
                searched_tweets.extend(new_tweets)
                max_id = new_tweets[-1].id
            except tweepy.TweepError:
                print('exception raised, waiting 5 minutes')
                print('(until:', dt.datetime.now() + dt.timedelta(minutes=5), ')')
                time.sleep(5 * 60)
                break  # stop the loop
        return searched_tweets, max_id

    def get_tweet_id(self, date='', days_ago=9, query='a'):

        if date:
            # return an ID from the start of the given day
            td = date + dt.timedelta(days=1)
            tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
            tweet = self.api.search(q=query, count=1, until=tweet_date)
        else:
            # return an ID from __ days ago
            td = dt.datetime.now() - dt.timedelta(days=days_ago)
            tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
            # get list of up to 10 tweets
            tweet = self.api.search(q=query, count=10, until=tweet_date)
            print('search limit (start/stop):', tweet[0].created_at)
            # return the id of the first tweet in the list
            return tweet[0].id

    def write_tweets(self,tweets, filename):
        ''' Function that appends tweets to a file. '''

        with open(filename, 'a') as f:
            for tweet in tweets:
                json.dump(tweet._json, f)
                f.write('\n')

def main():
    ''' search variables: '''
    search_phrases = ['dhoni', 'trump']
    time_limit = 0.5  # runtime limit in hours
    max_tweets = 10000  # number of tweets per search (will be
    # iterated over) - maximum is 10000
    min_days_old, max_days_old = 0,3  # search limits e.g., from 7 to 8
    # gives current weekday from last week,
    # min_days_old=0 will search from right now

    # Making an object
    api = TwitterClient()
    # loop over search items,
    # creating a new file for each
    for search_phrase in search_phrases:

        print('Search phrase =', search_phrase)

        ''' other variables '''
        name = search_phrase.split()[0]
        json_file_root = name + '/' + name
        os.makedirs(os.path.dirname(json_file_root), exist_ok=True)
        read_IDs = False

        # open a file in which to store the tweets
        if max_days_old - min_days_old == 1:
            d = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
        else:
            d1 = dt.datetime.now() - dt.timedelta(days=max_days_old - 1)
            d2 = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
                d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
        json_file = json_file_root + '_' + day + '.json'
        if os.path.isfile(json_file):
            # print('Appending tweets to file named: ', json_file)
            read_IDs = True

        # authorize and load the twitter API
        # api = load_api()

        # set the 'starting point' ID for tweet collection
        if read_IDs:
            # open the json file and get the latest tweet ID
            with open(json_file, 'r') as f:
                lines = f.readlines()
                max_id = json.loads(lines[-1])['id']
                # print('Searching from the bottom ID in file')
        else:
            # get the ID of a tweet that is min_days_old
            if min_days_old == 0:
                max_id = -1
            else:
                max_id = api.get_tweet_id(days_ago=(min_days_old - 1))
        # set the smallest ID to search for
        since_id = api.get_tweet_id(days_ago=(max_days_old - 1))
        print('max id (starting point) =', max_id)
        print('since id (ending point) =', since_id)

        ''' tweet gathering loop  '''
        start = dt.datetime.now()
        end = start + dt.timedelta(hours=time_limit)
        count, exitcount = 0, 0
        while dt.datetime.now() < end:
            count += 1
            print('count =', count)
            # collect tweets and update max_id
            tweets, max_id = api.tweet_search(search_phrase, max_tweets,
                                          max_id=max_id, since_id=since_id)
            # write tweets to file in JSON format
            if tweets:
                api.write_tweets(tweets, json_file)
                exitcount = 0
            else:
                exitcount += 1
                if exitcount == 3:
                    if search_phrase == search_phrases[-1]:
                        sys.exit('Maximum number of empty tweet strings reached - exiting')
                    else:
                        print('Maximum number of empty tweet strings reached - breaking')
                        break

if __name__ == "__main__":
    main()
