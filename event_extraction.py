import re
import nltk
from nltk.corpus import stopwords
import string

class EventExtract(object):

    def __init__(self,article):
        self.article = article
        self.stopwords_eng = stopwords.words('english')

    def clean_article(self,tokens):
        cleand_token = []
        for token in tokens:
            if (token not in self.stopwords_eng) and (token not in list(string.punctuation)):
                cleand_token.append(token)
        return cleand_token

    def get_tokenize(self,article):
        #remove stock market tickers like $GE
        article = re.sub(r'^\$\w*', '', article)

        # remove old style retweet text "RT"
        article = re.sub(r'^RT[\s]+', '', article)

        # remove hyperlinks
        article = re.sub(r'^https?:\/\/.*[\r\n]*', '', article, flags=re.MULTILINE)

        #remove hashtags
        #only removing the hash # sign from the word
        article = re.sub(r'#', '', article)

        return nltk.word_tokenize(article)

    def get_pos_tag(self,tokens):
        tokens = self.clean_article(tokens)
        return nltk.pos_tag(tokens)

    def get_chunks(self,possed_token):
        grammar = r"""
                    NP: {<JJ>*<JJ.*|NN>}
                """
        chunkParser = nltk.RegexpParser(grammar)
        tree = chunkParser.parse(possed_token)
        return tree

    def get_tree(self):
        tokens = self.get_tokenize(self.article)
        tagged_tokens = self.get_pos_tag(tokens)
        tree = self.get_chunks(tagged_tokens)
        return tree

article = 'On Thursday, there was a massive U.S.aerial bombardment in which more than 300 Tomahawk cruise missiles rained down on Baghdad. Earlier Saturday, Baghdad was again'

event_extraction = EventExtract(article)

tree = event_extraction.get_tree()

print("Events in acrticle:")
for s in tree.subtrees(filter=lambda t: t.label() == 'NP'):
    print(s[0][0])
