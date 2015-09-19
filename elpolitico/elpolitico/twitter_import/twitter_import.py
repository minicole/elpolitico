__author__ = 'Nicole'

import tweepy
from tweepy import Stream
import json
import indicoio
import time
from googleapiclient.discovery import build

# Tokens and keys
consumer_key = "nEcXxJ8rQ7UyDrPYzzDTFScLl"
consumer_secret = "60GrqyEeVwLLP5fLnx6OUtAixrAGpinZ1eBcujwCi4xKRutSPz"
access_token = "23385479-1AuhkNFfVDuzScTDh6cQzS5YoBjTLbA2h4qp1VGdj"
access_token_secret = "0tza6LdGohaT7QqU6L9oyAT7c8ifWNqNEy1FoL9lc7Old"

indicoio.config.api_key = 'e30201b851eb84179e68bf31aa36684a'

googleAPIKey = 'AIzaSyBo1twK-Cb-Mb1q7YCK1HaLFBCLb6BWwrc'

points = list()

#override tweepy.StreamListener to add logic to on_status
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
        self.counter += 1
        if self.counter == 2:
            self.on_disconnect('2 messages received')
        data = json.loads(raw_data)
        message = data['text']
        # if isNotEnglish(message):
        #     message = translateFromUnknownLanguageToEnglish(message)
        tags = indicoTags(message)
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
                else:
                    mostAccurateLocation = None
        # print(sys.getsizeof(mostAccurateLocation) + sys.getsizeof(tags))
        points.append([tags, mostAccurateLocation])
        print(points)


def indicoTags(tweet):
    tag_dict = indicoio.text_tags(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:3]

def indicoKeywords(tweet):
    tag_dict = indicoio.keywords(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:1]

def translateFromUnknownLanguageToEnglish(tweetText):
    service = build('translate', 'v2', developerKey=googleAPIKey)
    lFrom = service.detections().list(q=tweetText).execute()['detections'][0][0]['language']
    return service.translations().list(source=lFrom, target='en', q=tweetText).execute()

def isNotEnglish(text):
    language = indicoio.language(text)
    print(language)
    return sorted(language.keys(), key=lambda x: language[x], reverse=True)[:1] < 0.5

start = time.time()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.secure = True
auth.set_access_token(access_token, access_token_secret)

myApi = tweepy.API(auth)

keywords = list()

myKeywordStream = Stream(auth, tweepy.StreamListener())
timeline = myApi.home_timeline()
for raw_data in timeline:
    message = raw_data.text
    kw = indicoKeywords(message)
    for keyword in kw:
        keywords.append(keyword)

myKeywordStream.disconnect()

print(keywords)

myStream = Stream(auth, MyStreamListener())
for keyword in keywords:
    decoded_str = keyword.decode("windows-1252")
    encoded_str = decoded_str.encode("utf8")
    print(keyword + " " + decoded_str + " " + encoded_str)
    if(encoded_str is None):
        print(keyword + " was passed as NoneType")
        continue
    myStream.filter(track=["%s", encoded_str])

end = time.time()
print(end - start)