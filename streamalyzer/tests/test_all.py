import os
import pathlib

import pytest
import responses

from streamalyzer.clients import Tweet, TwitterAPIClient, WeatherAPIClient
from streamalyzer.start import start
from streamalyzer.transforms import LatLonTransformer, AvgTempTransformer, TemperatureTransformer

HERE = pathlib.Path(__file__).parent.resolve()

os.environ["TWITTER_BEARER_TOKEN"] = "FAKE"
os.environ["WEATHER_API_KEY"] = "FAKE"

@pytest.fixture
def tweet_stream_all():
    with open(HERE / "fixtures" / "tweet_stream.jsonl", "r") as tweetfile:
        yield tweetfile.read()


@responses.activate
def test_twitter_client(tweet_stream_all):
    responses.add(
        responses.GET,
        'https://api.twitter.com/2/tweets/sample/stream',
        body=tweet_stream_all,
        status=200
    )
    client = TwitterAPIClient()
    tweets = [t for t in client.stream_tweets()]
    assert len(tweets) == 4
    assert tweets[0].data['id'] == "11"
    assert tweets[1].data['id'] == "12"


@responses.activate
def test_weather_client():
    responses.add(
        responses.GET,
        'http://api.weatherapi.com/v1/current.json?key=FAKE&q=34.95%2C137.26',
        json={'location': {'lat': 34.95, 'lon': 137.26}, 'current': {'temp_c': 0.3, 'temp_f': 32.5}},
        status=200
    )
    client = WeatherAPIClient()
    temp_f = client.current(34.95, 137.26)
    assert temp_f == 32.5


def test_transform_latlon():
    transformer = LatLonTransformer()
    tweet_json = '{"data": {"geo": {"place_id": "8d742fb555fbff21"}, "id": "1490107240551956480", "text": "textttt"}, "includes": {"places": [{"geo": {"type": "Feature", "bbox": [-84.307688, 39.695193, -84.093044, 39.865523], "properties": {}}, "id": "8d742fb555fbff21", "place_type": "city"}]}}'
    tweet = Tweet.from_json(tweet_json)
    latlon = transformer.transform(tweet, [])
    assert latlon == [39.78035800000001, -84.200366]


def test_transform_avgtemp():
    transformer = AvgTempTransformer(n_lookback=3)
    tweets = [
        Tweet(data=None, includes=None) for n in range(5)
    ]
    new_tweet = Tweet(data=None, includes=None)
    for i, tweet in enumerate(tweets):
        tweet.transforms['temp_f'] = i * 10
    
    new_tweet.transforms['temp_f'] = 23
    avgtemp = transformer.transform(new_tweet, tweets)
    assert avgtemp == 31


@responses.activate
def test_transform_temp():
    responses.add(
        responses.GET,
        'http://api.weatherapi.com/v1/current.json?key=FAKE&q=34.95%2C137.26',
        json={'location': {'lat': 34.95, 'lon': 137.26}, 'current': {'temp_c': 0.3, 'temp_f': 32.5}},
        status=200
    )
    transformer = TemperatureTransformer()
    tweet = Tweet(data=None, includes=None)
    tweet.transforms['latlon'] = [34.95, 137.26]
    temp_f = transformer.transform(tweet, [])
    assert temp_f == 32.5


@responses.activate
def test_start(tweet_stream_all):
    """Test entire pipeline"""
    responses.add(
        responses.GET,
        'https://api.twitter.com/2/tweets/sample/stream',
        body=tweet_stream_all,
        status=200
    )
    responses.add(
        responses.GET,
        'http://api.weatherapi.com/v1/current.json?key=FAKE&q=39.78035800000001%2C-84.200366',
        json={'location': {'lat': 34.95, 'lon': 137.26}, 'current': {'temp_c': 0.3, 'temp_f': 30}},
        status=200
    )
    responses.add(
        responses.GET,
        'http://api.weatherapi.com/v1/current.json?key=FAKE&q=34.0141850535568%2C-118.28796282775565',
        json={'location': {'lat': 34.95, 'lon': 137.26}, 'current': {'temp_c': 0.3, 'temp_f': 40}},
        status=200
    )
    responses.add(
        responses.GET,
        'http://api.weatherapi.com/v1/current.json?key=FAKE&q=40.780709%2C-73.9685415',
        json={'location': {'lat': 34.95, 'lon': 137.26}, 'current': {'temp_c': 0.3, 'temp_f': 50}},
        status=200
    )

    start(n_lookback=3)

    with open("temps.txt", "r") as tempsfile:
        temps = tempsfile.readlines()
        assert temps == ['30\n', '40\n', '50\n']
    
    with open("avg_temp.txt", "r") as avgfile:
        avgs = avgfile.readlines()
        assert avgs == ['30.0\n', '35.0\n', '40.0\n']
