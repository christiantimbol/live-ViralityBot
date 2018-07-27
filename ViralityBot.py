# begin imports
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
from credentials import *
import json
from time import sleep

# python dictionary that convertts json code to language name
langs = {'ar': 'Arabic', 'bg': 'Bulgarian', 'ca': 'Catalan', 'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish', 'et': 'Estonian',
         'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'is': 'Icelandic', 'it': 'Italian', 'iw': 'Hebrew',
         'ja': 'Japanese', 'ko': 'Korean', 'lt': 'Lithuanian', 'lv': 'Latvian', 'ms': 'Malay', 'nl': 'Dutch', 'no': 'Norwegian', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian',
         'ru': 'Russian', 'sk': 'Slovak', 'sl': 'Slovenian', 'sr': 'Serbian', 'sv': 'Swedish', 'th': 'Thai', 'tl': 'Filipino', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu',
         'vi': 'Vietnamese', 'zh_CN': 'Chinese (simplified)', 'zh_TW': 'Chinese (traditional)'}


# begin tweepy stream listener
# defined class from Tweepy's StreamListener
# on_data() function tells an action to Tweepy when a new tweet is available --> loading json data using json library


class twitter_listener(StreamListener):

  # number of tweets to grab (counter)
  # retweet_count value is 10% of most retweeted tweet of all time
  def __init__(self, num_tweets_to_grab, stats, get_tweet_html, retweet_count=30000):
    self.counter = 0
    self.num_tweets_to_grab = num_tweets_to_grab
    self.retweet_count = retweet_count
    # Twitter json object returns 2 character code under lang json key. self.languages variable stores it
    # removed for v5 # self.languages = []
    # removed for v5 # self.top_languages = []
    self.stats = stats
    self.get_tweet_html = get_tweet_html

  def on_data(self, data):
    # cant add counter for on_data function here becuase it's called fresh every time
    # counter added to __init__
    try:
      json_data = json.loads(data)
      # commented out in v4 # print(json_data["text"])
      self.stats.add_lang(langs[json_data["lang"]])
      # gone in v5 # self.languages.append(langs[json_data["lang"]])

      self.counter += 1
      retweet_count = json_data["retweeted_status"]["retweet_count"]

      if retweet_count >= self.retweet_count:
        # v5 # print(json_data["text"], retweet_count, langs[json_data["lang"]])
        # v5 # self.top_languages.append(langs[json_data["lang"]])
        self.stats.add_top_tweets(self.get_tweet_html(json_data['id']))
        self.stats.add_top_lang(langs[json_data["lang"]])

      if self.counter >= self.num_tweets_to_grab:
        # v5 # print(self.languages)
        # v5 # print(self.top_languages)
        # v5 # print(Counter(self.languages))
        # v5 # print(Counter(self.top_languages))
        return False  # causes class to exit (how Tweepy internally works). Returning true makes it look for new tweets.

      return True
    except:
      # @ToDo: need a better fix for this becuase bad tweets and bugs get hidden
      pass

  def on_error(self, status):
    print(status)


# begin authentications
class TwitterMain():
  def __init__(self, num_tweets_to_grab, retweet_count=30000):
    self.auth = tweepy.OAuthHandler(cons_tok, cons_sec)
    self.auth.set_access_token(app_tok, app_sec)

    self.api = tweepy.API(self.auth)
    self.num_tweets_to_grab = num_tweets_to_grab
    self.retweet_count = retweet_count
    self.stats = stats()

  # create twitter stream with authentications and twitter_listener class
    # call sample() to get sample of tweets
  def get_streaming_data(self):
    twitter_stream = Stream(self.auth, twitter_listener(num_tweets_to_grab=self.num_tweets_to_grab, retweet_count=self.retweet_count, stats=self.stats, get_tweet_html=self.get_tweet_html))
    try:
      twitter_stream.sample()
    except Exception as e:
      print(e.__doc__)

    lang, top_lang, top_tweets = self.stats.get_stats()
    # print(Counter(lang))
    # print(Counter(top_lang))
    # print(top_tweets)

    for tweet in tweepy.Cursor(self.api.search, q='.', since='2018-07-01', until='2018-07-27', lang='en').items(5):
      if self.retweet_count >= 30000:
        print(tweet.text)
        print(tweet.retweet_count)
        tweet.retweet()
        sleep(10)

  def get_trends(self):
    trends = self.api.trends_place(1)
    trend_data = []

    for trend in trends[0]["trends"]:
      # print(trend['name'])
      trend_tweets = []
      trend_tweets.append(trend['name'])
      trend_tweets.append(self.get_tweet_html(tweet.id))
      '''
      tt = tweepy.Cursor(self.api.search, q='.', lang='en').items(5)
      '''

      '''
      for t in tt:
        trend_tweets.append(self.get_tweet_html(t.id))

        if self.retweet_count >= 30000:
          # inputting these two lines retweeted some viral tweets, but some only had a few retweets, and it exceeded my limit of # retweets stated for some reason
          print(t.text)
          print(t.retweet_count)
          sleep(5)
          t.retweet()
          # print('Retweeted')
          # print(tweet_html)
      '''

      trend_data.append(tuple(trend_tweets))

    # print(trend_data)

  def get_tweet_html(self, id):
    oembed = self.api.get_oembed(id=id, hide_media=True, hide_thread=True)

    tweet_html = oembed['html'].strip("\n")

    return tweet_html


class stats():

  def __init__(self):
    self.lang = []
    self.top_lang = []
    self.top_tweets = []

  def add_lang(self, lang):
    self.lang.append(lang)

  def add_top_lang(self, top_lang):
    self.top_lang.append(top_lang)

  def add_top_tweets(self, tweet_html):
    self.top_tweets.append(tweet_html)

  def get_stats(self):
    return self.lang, self.top_lang, self.top_tweets


if __name__ == "__main__":
  num_tweets_to_grab = 5
  retweet_count = 30000
  # pdb.set_trace()
  twit = TwitterMain(num_tweets_to_grab, retweet_count)
  twit.get_streaming_data()
  twit.get_trends()

'''
#         _
#     .__(.)< ("Quack")
#     \____)
# ~~~~~~~~~~~~~~~~~~~~
'''
