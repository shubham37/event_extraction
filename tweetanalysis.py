import tweepy
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

class TwitterClient(object):

    # Class constructor or initialization method.
    def __init__(self):

        # keys and tokens from the Twitter Dev Console
        # consumer_key = "XXXXXXXXXXXXXXXXXXXXX"
        # consumer_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        #
        # access_token = "XXXXXXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXX"
        # access_token_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        consumer_key = "1AuAlJYU92dRhQbs4bLV1OkmB"
        consumer_secret = "ZTx4b3Wja2jxCAxNUz3F6UuIRE6fOwy0nfiVKJey3AE2yXQiZw"

        access_token = "1036668553435537409-yWNdCXPEabt1CRUldWc93LwFOCGyyH"
        access_token_secret = "blPTtk6ZFTVu9tGSd7ESwSnEuNXPzElPX0PxDyjkqGQnc"

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            #
            # # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)

            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)

            #for Lemmitization
            self.lemmatizer = nltk.wordnet.WordNetLemmatizer()

            #For Steamization
            self.stemmer = nltk.stem.PorterStemmer()

            #For Stopwords
            self.stopwords_eng = stopwords.words('english')

            # Happy Emoticons
            self.emoticons_happy = set([
                ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
                ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
                '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
                'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
                '<3'
            ])

            # Sad Emoticons
            self.emoticons_sad = set([
                ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
                ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
                ':c', ':{', '>:\\', ';('
            ])

            # all emoticons (happy + sad)
            self.emoticons = self.emoticons_happy.union(self.emoticons_sad)
        except:
            print("Error: Authentication Failed")

    # Method for tokenization
    def get_tokenize(self,tweet):
        tokens = word_tokenize(tweet) # Word Tokenization
        return tokens

    # Method for lemmatizaton and stemmerization
    def normalize_word(self, word):
        word = self.stemmer.stem(word)  # if we consider stemmer then results comes with stemmed word, but in this case word will not match with comment
        word = self.lemmatizer.lemmatize(word)
        return word

    # Method for cleaning tweet removing links, special character, emotions, stopwords, punchuations etc.
    def clean_tweet(self, tweet):

        emoji_pattern = re.compile("["
                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                   "]+", flags=re.UNICODE)
        tweet  = emoji_pattern.sub(r'', tweet)

        # remove stock market tickers like $GE
        tweet = re.sub(r'^\$\w*', '', tweet)

        # remove old style retweet text "RT"
        tweet = re.sub(r'^RT[\s]+', '', tweet)

        # remove hyperlinks
        tweet = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet, flags=re.MULTILINE)

        # remove hashtags
        # only removing the hash # sign from the word
        tweet = re.sub(r'#', '', tweet)

        # tokenize tweets
        # tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
        tweet_tokens = self.get_tokenize(tweet)

        tweets_clean = []
        for word in tweet_tokens:

            if (word not in self.stopwords_eng) and (word not in self.emoticons) and (word not in list(string.punctuation)):  # remove punctuation
                    stem_word = self.normalize_word(word)  # stemming word
                    tweets_clean.append(stem_word)

        return tweets_clean

    # Tag words to a Part of speech
    def get_pos_tagging(self, tweet_tokens):
        tag_pos = nltk.pos_tag(tweet_tokens)
        return tag_pos

    # Making Chunks using Tagged word
    def get_chunkers(self,pos):
        grammar = r"""         
            NP:{<NN.*|JJ.*|VBZ>} 
                """
        chunkParser = nltk.RegexpParser(grammar)
        tree = chunkParser.parse(pos)
        return tree

    def leaves(self,tree):
        topics = []
        """Finds NP (nounphrase) leaf nodes of a chunk tree."""
        for s in tree.subtrees(filter=lambda t: t.label() == 'NP'):
            print(s)
            topics.append(list(s[0])[0])
        return topics

    def get_tweets(self, query, count=1):

        # empty list to store parsed tweets
        data = {}
        tweets = []
        created_dates = {}

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:

                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                created_dates[tweet.text] = tweet.created_at
                # saving sentiment of tweet
                # parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

                    # return parsed tweets
            data['tweets'] = tweets
            data['dates'] = created_dates

            return data

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

def fetch(word,n):
    api = TwitterClient()
    data = api.get_tweets(query=word, count=n)
    tweets = data['tweets']
    for tweet in tweets:
        tweet_clean_tokens = api.clean_tweet(str(tweet['text']))
        tagged_tokens = api.get_pos_tagging(tweet_clean_tokens)
        chunks_tree = api.get_chunkers(tagged_tokens)
        titles = api.leaves(chunks_tree)
        print("Topic : " + str(tweet['text']))
        print("Possible Titles : " + titles)
        print('\n')

fetch('Dhoni',10)


