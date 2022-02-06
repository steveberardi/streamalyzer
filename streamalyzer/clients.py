import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

class Tweet(object):
    def __init__(self, data, includes):
        self.data = data
        self.includes = includes
        self.transforms = {}
    
    @staticmethod
    def from_json(tweet_json):
        parsed = json.loads(tweet_json)
        return Tweet(parsed['data'], parsed.get('includes'))


class TwitterAPIClient(object):
    def __init__(self):
        self.bearer_token = os.environ["TWITTER_BEARER_TOKEN"]
        self.base_url = "https://api.twitter.com/2/"
    
    def stream_tweets(self):
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        params = {
            "tweet.fields": "geo",
            "expansions": "geo.place_id",
            "place.fields": "full_name,geo,id,place_type",
        }
        r = requests.get(
            f"{self.base_url}tweets/sample/stream",
            headers=headers,
            params=params,
            stream=True
        )
        for tweet in r.iter_lines():
            if tweet:
                yield Tweet.from_json(tweet)


class WeatherAPIClient(object):
    def __init__(self):
        self.key = os.environ["WEATHER_API_KEY"]
        self.base_url = "http://api.weatherapi.com/v1/"
    
    def current(self, lat, lon):
        params = {
            "key": self.key,
            "q": f"{lat},{lon}",
        }
        r = requests.get(f"{self.base_url}current.json", params=params)
        data = r.json()
        return data['current']['temp_f']
