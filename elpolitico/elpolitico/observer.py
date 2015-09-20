__author__ = 'foxtrot'

import tweepy
from tweepy import Stream
import json
import indicoio
import time
import threading
from googleapiclient.discovery import build
from MyState import *
import urllib2

# Tokens and keys
consumer_key = "nEcXxJ8rQ7UyDrPYzzDTFScLl"
consumer_secret = "60GrqyEeVwLLP5fLnx6OUtAixrAGpinZ1eBcujwCi4xKRutSPz"
access_token = "23385479-1AuhkNFfVDuzScTDh6cQzS5YoBjTLbA2h4qp1VGdj"
access_token_secret = "0tza6LdGohaT7QqU6L9oyAT7c8ifWNqNEy1FoL9lc7Old"

indicoio.config.api_key = 'e30201b851eb84179e68bf31aa36684a'

googleAPIKey = 'AIzaSyBo1twK-Cb-Mb1q7YCK1HaLFBCLb6BWwrc'

# Globals
MAX_CACHE_NUMBER = 1000  # Cache only 1k points

KeywordsToFilter = list()  # Can only add to this list.
PointsCaptured = list()


def KeywordUpdateThread():

    def KeywordUpdateModule():

        global KeywordsToFilter

        print("Authenticating Keyword Updater")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_token, access_token_secret)
        myApi = tweepy.API(auth)
        myKeywordStream = Stream(auth, tweepy.StreamListener())

        print("Authentication successfull!")

        keywords = list()

        timeline = myApi.home_timeline()
        for raw_data in timeline:
            message = raw_data.text
            kw = indicoKeywords(message)
            for keyword in kw:
                keywords.append(unicode(keyword.decode('utf-8')))
        print("Keywords collected, sleeping...")
        myKeywordStream.disconnect()

        print(keywords)
        KeywordsToFilter = keywords
    # end KeywordUpdateModule():

    try:
        while True:
            print("Asking for new political keywords")
            spawn_off = threading.Thread(target=KeywordUpdateModule)
            spawn_off.start()
            time.sleep(60)

    except Exception, e:
        print("An error occurred with the keyword observer stream thread. This wasn't supposed to happen!")
        print(e.message.decode())
# end KeywordUpdateThread()

def TwitterUpdateThread():

    def TwitterObserverModule():
        finalKeywords=list()
        for keyword in KeywordsToFilter:
            # print(type(keyword))
            decoded_str = keyword.decode("windows-1252")
            encoded_str = decoded_str.encode("utf8")
            # print(keyword + " " + decoded_str + " " + encoded_str)
            if(encoded_str is None):
                print(keyword + " was passed as NoneType")
                continue

            finalKeywords.append(encoded_str)

        TwitterStream.filter(track=finalKeywords)
    # end TwitterObserverModule()


    try:
        print("Authenticating Twitter Updater")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_token, access_token_secret)
        myApi = tweepy.API(auth)
        TwitterStream = Stream(auth, MyStreamListener())

        print("Authentication of Twitter Streamsuccessfull!")

        while True:
            if(len(KeywordsToFilter)>0):
                TwitterObserverModule()
            time.sleep(30)
    except:
        print("An error occurred with the Twitter feed. This wasn't supposed to happen!")
# end TwitterUpdateThread()


class MyStreamListener(tweepy.StreamListener):
    counter = 0
    def __init__(self):
        self.f = open("file.txt",'ab')

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False
        print(status_code)

    def on_data(self, raw_data):

        self.f.write(raw_data)
        self.f.write('\n')
        coordinates = None

        global PointsCaptured
        data = json.loads(raw_data)
        if 'text' in data:
            message = data['text']
            print(message)
            # Someday we'll get to this... Not today though.
            # if isNotEnglish(message):
            #     message = translateFromUnknownLanguageToEnglish(message)
            politicalTag = indicoPolitics(message)
            print("Doing GEog")
            if 'user' in data:
                if 'coordinates' in data['user']:
                    if 'coordinates' in data['user']['coordinates']:
                        mostAccurateLocation = data['coordinates']['coordinates']
                    else:
                        mostAccurateLocation = data['coordinates']
                        coordinates = mostAccurateLocation
                    # elif 'location' in data['user']:
                    #     location = data['user']['location']
                    #     if location is not None:
                    #         decoded_str = location.decode("windows-1252")
                    #         encoded_str = decoded_str.encode("utf8")
                    #         if encoded_str is None:
                    #             print(location + " was passed as NoneType")
                    #         if ',' in encoded_str:
                    #             mostAccurateLocation = encoded_str
                    #             try:
                    #                 url = "https://maps.googleapis.com/maps/api/geocode/json?address="+mostAccurateLocation.encode('utf-8')+"&key="+googleAPIKey
                    #                 print(url)
                    #                 result = urllib2.urlopen(url)
                    #             except Exception, e:
                    #                 print(e)
                    #             coordinates = result
                    #         else:
                    #             mostAccurateLocation = None
                    #             coordinates = None
            # coordinates=None
            # poliNumber = indicoPoliticsNumber(message)
            # print(poliNumber + "!!!")
            # positivity = indicoPositivity(message)
            # print(positivity + "!!!")
            #
            print("Finished geog, doing states")
            myStateOfPoint = StateOfPoint()
            myStateOfPoint.newPoint.party = politicalTag
            # myStateOfPoint.newPoint.tendency = poliNumber
            # myStateOfPoint.positivity = positivity
            print("doing coordinates")
            if coordinates is not None:
                print(coordinates)
                coordinates = mostAccurateLocation.split(', ')
                myStateOfPoint.newPoint.lat = coordinates[0]
                myStateOfPoint.newPoint.long = coordinates[1]
            #
            # PointsCaptured.append(myStateOfPoint)
            # if len(PointsCaptured) is MAX_CACHE_NUMBER:
            #     PointsCaptured.remove(0)  # Remove the first element!
            # print(myStateOfPoint)


# end Class MyStreamListener


def indicoPolitics(tweet):
    tag_dict = indicoio.political(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:1]

def indicoPoliticsNumber(tweet):
    tag_dict = indicoio.political(tweet)
    print(tag_dict)
    top = sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:1]
    print(tag_dict[top[0]])
    return tag_dict[top[0]]

def indicoPositivity(tweet):
    return indicoio.sentiment(tweet)

def indicoKeywords(tweet):
    tag_dict = indicoio.keywords(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:1]

def translateFromUnknownLanguageToEnglish(tweetText):
    service = build('translate', 'v2', developerKey=googleAPIKey)
    lFrom = service.detections().list(q=tweetText).execute()['detections'][0][0]['language']
    return service.translations().list(source=lFrom, target='en', q=tweetText).execute()

def InitAuth():
    global auth
    print(auth)
    if auth is None:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_token, access_token_secret)
    print(auth)
# end InitAuth()

