from abc import ABCMeta, abstractmethod

from .clients import WeatherAPIClient

class Transformer(metaclass=ABCMeta):
    @abstractmethod
    def transform(self, tweet, tweets):
        pass


class LatLonTransformer(Transformer):
    """Finds lat/lon centroid of tweet's bounding box"""

    @property
    def name(self):
        return "latlon"
    
    def transform(self, tweet, tweets):
        place_id = tweet.data['geo']['place_id']
        for place in tweet.includes['places']:
            if place['id'] == place_id:
                bbox = place['geo']['bbox']
                center_lat, center_lon = (bbox[1]+bbox[3]) / 2, (bbox[0]+bbox[2]) / 2
                return [center_lat, center_lon]
        return None


class TemperatureTransformer(Transformer):
    """Gets current temperature of tweet's lat/lon"""

    def __init__(self):
        self.api_client = WeatherAPIClient()
    
    @property
    def name(self):
        return "temp_f"
    
    def transform(self, tweet, tweets):
        return self.api_client.current(
            tweet.transforms['latlon'][0],
            tweet.transforms['latlon'][1],
        )


class AvgTempTransformer(Transformer):
    """Calculates average temperature of last n tweets"""

    def __init__(self, n_lookback) -> None:
        self.n_lookback = n_lookback

    @property
    def name(self):
        return "avg_temp"
    
    def transform(self, tweet, tweets):
        all_tweets = tweets + [tweet]
        n_tweets = all_tweets[-self.n_lookback:]
        temps = [t.transforms['temp_f'] for t in n_tweets]
        return sum(temps) / len(temps)
