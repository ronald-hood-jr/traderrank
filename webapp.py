# Entry point for the application.
from . import app    # For application discovery by the 'flask' command.
from . import views  # For import side-effects of setting up routes.
import tweepy
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta

import requests

import json

import nltk
import string
import ssl
from nltk.sentiment import SentimentIntensityAnalyzer

#nlp resources
nltk.download(['names','stopwords','averaged_perceptron_tagger','vader_lexicon','punkt'])
stopwords = nltk.corpus.stopwords.words("english")


names = ["AWice",
        "CL207",
        "LomahCrypto",
        "KeyboardMonkey3",
        "HighStakesCap",
        "RookieXBT",
        "iamjosephyoung",
        "cousincrypt0"]

#names = ["KRMA_0"]

#names = ["AWice"]

pictures = []

rankArr = []


def sentimentAnalysis(jsonArr):
    for i in range(len(jsonArr)):
        handle = jsonArr[i]['user']
        picture = jsonArr[i]['pic']
        tweetArr = jsonArr[i]['tweetArray']
        pictures.append(picture)
        tempArr = []
        for j in range(len(tweetArr)):
            tweet = list(tweetArr[j].values())[0]
            priceMovement = list(tweetArr[j].values())[1]
            #remove the escape sequences and tokenize meaningful words
            tweet = tweet.strip('\n')
            tweet = tweet.strip('\t')
            tweet = tweet.replace('\n','')
            tweet = tweet.replace('\t','')
            translator=str.maketrans(string.punctuation,' '*len(string.punctuation))
            tweet =  tweet.translate(translator)
            tokens = nltk.word_tokenize(tweet)                   
            tokens = [t for t in tokens if t.isalpha()]
            tokens = [t for t in tokens if t.lower() not in stopwords]

            tokensString = ' '.join(tokens)#combine tokens into one string
            sia = SentimentIntensityAnalyzer()
            print(priceMovement)
            tScores = sia.polarity_scores(tokensString)['compound']*float(priceMovement)*100
            tempArr.append(float(tScores))
        rankArr.append(sum(tempArr))
    print(rankArr)
    
        

def dateToSeconds(created_at):
    epoch = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S").timestamp()
    return str(int(epoch) - 21600)

def findTheTweets():
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    print("HELLO")
    sevenDaysAgoDatetime = datetime.today()-timedelta(days=7)
    sevenDaysAgo = sevenDaysAgoDatetime.strftime("%Y-%m-%d")

    print("*********************************")

    jsonArray = []

    newnum = 1

    #for i in names:
    for i in names:
        
        #                                                        i
        results = api.search(q="(btc OR bitcoin) (from:" + i + ") since:" + sevenDaysAgo, count=50, tweet_mode='extended')

        tempDict = {
            "user": i,
            "pic": results[0].user.profile_image_url_https,
            "tweetArray": []
        }
        
        #for result in results:
        #    print()
        #    print(result)
        #    print()

        for j in range(len(results)):
            print(str(results[j].created_at) + ", or " + dateToSeconds(results[j].created_at))
            cryptoCompareQuery = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&toTs=" + dateToSeconds(results[j].created_at)
            cryptoCompare = requests.get(cryptoCompareQuery)
            #print(cryptoCompare.status_code)
            #print(cryptoCompare.json())
            jsonText = json.dumps(cryptoCompare.json(), sort_keys=True, indent=2)
            jsonDict = json.loads(jsonText)
            #print(jsonDict)
            btcPrice = 0
            try:
                btcPrice = float(jsonDict["Data"]["Data"][1]["open"])
            except:
                btcPrice = 0

            cryptoCompareQuery2 = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&toTs=" + str(int(dateToSeconds(results[j].created_at)) + 3600)
            cryptoCompare2 = requests.get(cryptoCompareQuery2)
            jsonText2 = json.dumps(cryptoCompare2.json(), sort_keys=True, indent=2)
            jsonDict2 = json.loads(jsonText2)
            btcPrice2 = 0
            try:
                btcPrice2 = float(jsonDict2["Data"]["Data"][1]["open"])
            except:
                btcPrice2 = btcPrice

            if btcPrice == 0:
                btcPrice2 = 0
            
            if btcPrice == 0:
                priceMovement = 0
            else:
                priceMovement = (btcPrice2 - btcPrice) / btcPrice * 100

            print(btcPrice)
            print(btcPrice2)
            print(priceMovement)
            #print(tempDict['pic'])

            tempDict['tweetArray'].append({'tweet'+str(j):results[j].full_text, 'priceMovement':str(priceMovement)})

            print("*****************")

        jsonArray.append(tempDict)
        
        print("*********************************")

    dumps = json.dumps(jsonArray)
    jsonFile = json.loads(dumps)

    sentimentAnalysis(jsonFile)

    filename = open('tweetdata.json','w')
    json.dump(jsonFile, filename)
    filename.close()

findTheTweets()

print("NAMES:")
print(names)
print()
print("SCORE:")
print(rankArr)
print()
print("PIC URL")
print(pictures)

def returnNameScorePic():
    arrRet = []
    arrRet.append(names)
    arrRet.append(rankArr)
    arrRet.append(pictures)
    return arrRet


scheduler = BackgroundScheduler()
scheduler.add_job(func=findTheTweets, trigger="interval", seconds=604800)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())