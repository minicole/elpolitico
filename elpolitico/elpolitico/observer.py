__author__ = 'foxtrot'

import tweepy
from tweepy import Stream
import json
import indicoio
import time
import threading
from googleapiclient.discovery import build
from views import *
from MyState import *

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
            time.sleep(600)

    except Exception, e:
        print("An error occurred with the keyword observer stream thread. This wasn't supposed to happen!")
        print(e.message.decode())
# end KeywordUpdateThread()

def TwitterUpdateThread():

    def TwitterObserverModule():
        finalKeywords=list()
        for keyword in KeywordsToFilter:
            print(type(keyword))
            decoded_str = keyword.decode("windows-1252")
            encoded_str = decoded_str.encode("utf8")
            print(keyword + " " + decoded_str + " " + encoded_str)
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
        TwitterStream = Stream(auth, tweepy.StreamListener())

        print("Authentication of Twitter Streamsuccessfull!")

        while True:
            if(len(KeywordsToFilter)>0):
                TwitterObserverModule()
            time.sleep(300)
    except:
        print("An error occurred with the Twitter feed. This wasn't supposed to happen!")
# end TwitterUpdateThread()


class MyStreamListener(tweepy.StreamListener):
    counter = 0

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False
        print(status_code)

    def on_data(self, raw_data):
        global PointsCaptured
        myStates = getMyStates()

        self.counter += 1
        if self.counter == 2:
            self.on_disconnect('2 messages received')
        data = json.loads(raw_data)
        message = data['text']
        # Someday we'll get to this... Not today though.
        # if isNotEnglish(message):
        #     message = translateFromUnknownLanguageToEnglish(message)
        politicalTag = indicoPolitics(message)
        if data['user']['geo_enabled'] == True:
            mostAccurateLocation = data['coordinates']['coordinates']
        else:
            location = data['user']['location']
            if location is not None:
                decoded_str = location.decode("windows-1252")
                encoded_str = decoded_str.encode("utf8")
                if(encoded_str is None):
                    print(location + " was passed as NoneType")
                if ',' in encoded_str:
                    mostAccurateLocation = encoded_str
                    # service = build('geocode', 'v1', developerKey=googleAPIKey)
                    # coordinates = service.geocoder().getLatLng().list
                    # TODO: Grab the coordinates from Google Maps API
                    coordinates = None
                else:
                    mostAccurateLocation = None
                    coordinates = None

        PointsCaptured.append([politicalTag, mostAccurateLocation])

        if(len(PointsCaptured)==MAX_CACHE_NUMBER):
            PointsCaptured.remove(0)  # Remove the first element!

        print(PointsCaptured)

        myStateOfPoint = StateOfPoint()
        myStateOfPoint.newPoint.party = politicalTag
        myStateOfPoint.newPoint.tendency = indicoPoliticsNumber(message)
        myStateOfPoint.positivity = indicoPositivity(message)
        if coordinates is not None:
            coordinates = mostAccurateLocation.split(', ')
            myStateOfPoint.newPoint.lat = coordinates[0]
            myStateOfPoint.newPoint.long = coordinates[1]

        print(myStateOfPoint)

# end Class MyStreamListener


def indicoPolitics(tweet):
    tag_dict = indicoio.political(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:1]

def indicoPoliticsNumber(tweet):
    tag_dict = indicoio.political(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict.keys()[x], reverse=True)[:1]

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

