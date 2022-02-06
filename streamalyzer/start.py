import argparse

from .clients import TwitterAPIClient
from .transforms import LatLonTransformer, TemperatureTransformer, AvgTempTransformer
from .exporters import TransformFileExporter

def start(n_lookback=5):
    twitter_client = TwitterAPIClient()

    transformers = [
        LatLonTransformer(),
        TemperatureTransformer(),
        AvgTempTransformer(n_lookback=n_lookback),
    ]

    exporters = [
        TransformFileExporter(transform="temp_f", filename="temps.txt"),
        TransformFileExporter(transform="avg_temp", filename="avg_temp.txt")
    ]

    tweets = []

    print('Starting Streamalyzer... Press [Ctrl+C] to Exit')

    for tweet in twitter_client.stream_tweets():
        if tweet.data.get('geo'):
            for t in transformers:
                tweet.transforms[t.name] = t.transform(tweet, tweets)

            print(f"Transformed Tweet: {tweet.transforms}")

            tweets.append(tweet)

            for e in exporters:
                e.export(tweet)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_lookback', type=int, required=True)
    args = parser.parse_args()
    n_lookback = args.n_lookback
    if n_lookback < 2 or n_lookback > 100:
        print("Error: N Lookback must be between 2 and 100")
        exit(1)
    start(n_lookback=n_lookback)