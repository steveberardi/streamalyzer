# Streamalyzer

Streamalyzer is a lightweight platform for analyzing realtime data streams. It currently supports analyzing tweets from Twitter's streaming API. It's been tested with Python 3.9.4.

## Getting Started

1. Create API keys for the [Twitter API](https://developer.twitter.com/en/docs/twitter-api) and [Weather API](https://www.weatherapi.com/), and put them in a `.env` file at the root of the repo:
```
    TWITTER_BEARER_TOKEN=YOUR_API_KEY
    WEATHER_API_KEY=YOUR_API_KEY
```

2. `make start` to start Streamalyzer. This will create a virtual environment and install all requirements.

3. `make test` to run the tests

## How It Works

When you start Streamalyzer (via `make start`), it will start the process of collecting tweets, and for each new tweet it will:

1. Determine the lat/lon of the tweet (if geo-tagged)
2. Determine the current temperature in farenheit at that lat/lon, via WeatherAPI
3. Calcuate the sliding average temperature of the past N tweets that were collected
4. Output the calculated data (lat/lon, temp, average temp) of the tweet to `stdout`
5. Output the temperature to a new line in the file `temps.txt`
6. Output the sliding average temperature to a new line in the file `avg_temp.txt`

To stop Streamalyzer, press Ctrl+C. This will gracefully close the output files too :)

## Runtime Options

You can adjust the number of tweets used in the sliding average by setting `N_LOOKBACK`, for example:

    make N_LOOKBACK=2 start

This value must be between 2 and 100. By default, `make start` will use `N_LOOKBACK=5`.

## Cloud Architecture

A potential architecture for deploying Streamalyzer to Google Cloud Platform can be found in the `docs` folder.
