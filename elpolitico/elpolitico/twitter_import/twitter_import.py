__author__ = 'Nicole'

import tweepy
from tweepy import Stream
import json
import indicoio
import time



# Tokens and keys
consumer_key = "nEcXxJ8rQ7UyDrPYzzDTFScLl"
consumer_secret = "60GrqyEeVwLLP5fLnx6OUtAixrAGpinZ1eBcujwCi4xKRutSPz"
access_token = "23385479-1AuhkNFfVDuzScTDh6cQzS5YoBjTLbA2h4qp1VGdj"
access_token_secret = "0tza6LdGohaT7QqU6L9oyAT7c8ifWNqNEy1FoL9lc7Old"

indicoio.config.api_key = 'e30201b851eb84179e68bf31aa36684a'


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
        tags = indicoTags(message)
        with open('data.txt', 'ab') as outfile:
            outfile.write(raw_data)
            outfile.write('\n')
        outfile.close()


keywords = list()


def indicoTags(tweet):
    print(tweet)
    tag_dict = indicoio.text_tags(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:3]

def indicoKeywords(tweet):
    tag_dict = indicoio.keywords(tweet)
    return sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:1]



# thread.start_new_thread(MyStreamAccessor.readStream(MyStreamAccessor()))

start = time.time()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.secure = True
auth.set_access_token(access_token, access_token_secret)

myApi = tweepy.API(auth)

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
    print(type(keyword))
    # keyword2 = keyword.encode('ascii')
    # keyword2 = keyword.decode('utf8')
    decoded_str = keyword.decode("windows-1252")
    encoded_str = decoded_str.encode("utf8")
    print(type(encoded_str))
    myStream.filter(track=["%s", encoded_str])

end = time.time()
print(end - start)