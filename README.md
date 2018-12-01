# unfound_nlp_assignment
There are 3 python files for each problem statement.

# Dependencies Used
1. NLTK
2. Tweepy

# Description

# 1. event_extraction.py

    This file extract the event names from given pieace of text/tweet/article.
    I. First we do tokenization - converting sentences into words called tokenization
       nltk.word_tokenize()

    II. Before doing tokenization we have to do Cleaning Proces. we use regular expression to do this task

    III. After Tokenization we tag individual word with part of speech.
        nltk.pos_tag()

    IV. Next Step is Chunking. To do this step we first define grammer and than appply parser 
        nltk.RegexpParser(grammer)

    V. Final  step is choosing event or NP phrase.
    
# 2. relevant_data.py

    This file extract tweets ofpast 3 days.
    I. In this file we work on tweepy api that is provided by twitter.
    II. save relevant tweets into a /json file
    
# 3. tweetanalysis.py

    This file is used to tag title of an tweet.
    I. First we get tweet using tweepy api.
    II. Tokenization  - Broke a sentence into words  
        nltk.word_toknize()
    III. CLeaning  - remove annoying data like stopwords,emojis, hyperinks,emotions , punchuationetc.
    IV. POS tagging  -  trace out which is noun or other part of speech
        nltk.pos_tag()
    V. Chunking   -  Extract phrases from pos tagger. first decide grammer than apply parser.
        nltk.RegexParser(grammer)
        
    VI. Chinking  - the process of removing a sequence of tokens from a chunk
        Lemmitization - nltk.wordnet.WordNetLemmatizer()
        Stemmerization - nltk.stem.PorterStemmer()
    VII. Spell Checking and CLeaning
    VIII. Final  step is tagging title.
 
 
 # How To Use?
 
 
# 1. event_extraction.py
    Fisrt set article variable with string/pieace of text and than run a python file

# 2. relevant_data.py
      Just Run it and pass  word/phrases

# 3. tweetanalysis.py
    call  fetch(query, no_of_tweets) function with two parameters
