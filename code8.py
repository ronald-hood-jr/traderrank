#Shiller Ranking and Sentiment Analysis Script

import nltk
import string
import ssl
from nltk.sentiment import SentimentIntensityAnalyzer
#from pprint import pprint

#nlp resources
nltk.download(['names','stopwords','averaged_perceptron_tagger','vader_lexicon','punkt'])
stopwords = nltk.corpus.stopwords.words("english")

#Variables for
traderTemplate = {"handle":"","tweetText":"","percentChange":0}#template, tweetText and percentChange will array containing all tweet strings and corresponding changes
traders = [traderTemplate for x in range (8)]#Array of trader dictionaries
traderScores=[0]#Array containing average of scores from all of each traders tweets,idk how many tweets so plz resize and make 2d

handle="handle"
tweetText="tweetText"
percentChange="percentChange"

Awice = traderTemplate #example
Awice[handle]="Awice"
Awice[tweetText]="Dear poors,\n\n#Bitcoin is not a hot potato like $GME. There will be price swings but you can confidently buy and hold for life, not just a quick pump.\n\nRetweet this. https://t.co/Ep8c7gam0A"
Awice[percentChange]=1.347

#Fill in traders to template template with real data from JSON. This is just an example for 1.
#Everything below here needs to be generalized in the loop to traders[i][tweetText]
#for trader in traders:

#remove the escape sequences and tokenize meaningful words
Awice[tweetText] = (Awice[tweetText]).strip('\n')
Awice[tweetText] = (Awice[tweetText]).strip('\t')
Awice[tweetText] = (Awice[tweetText]).replace('\n','')
Awice[tweetText] = (Awice[tweetText]).replace('\t','')
translator=str.maketrans(string.punctuation,' '*len(string.punctuation))
Awice[tweetText] =  (Awice[tweetText]).translate(translator)
tokens = nltk.word_tokenize(Awice[tweetText])                   
tokens = [t for t in tokens if t.isalpha()]
tokens = [t for t in tokens if t.lower() not in stopwords]
#pprint(tokens, width=79, compact=True)

#Sentiment Analysis
tokensString = ' '.join(tokens)#combine tokens into one string
sia = SentimentIntensityAnalyzer()
tScores = sia.polarity_scores(tokensString)['compound']*Awice[percentChange]*100

print(tScores)
#repeat for each trader for each tweet then sum and order them by average score

