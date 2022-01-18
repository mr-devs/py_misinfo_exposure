# `py_misinfo_exposure`
A Python package that can be used to calculate misinformation-exposure scores for a user based on the falsity scores of public figures they follow on Twitter.

The falsity score is based on PolitiFact fact-checks of the public figures.

> 🚨 Note 🚨:
> This package replicates [Mohsen Mosleh's R package](https://github.com/mmosleh/minfo-exposure) which does the same thing and is based on Mosleh and Rand's paper (2021). 
> - [Paper](https://psyarxiv.com/ye3pf/)
> - [Data](https://github.com/mmosleh/minfo-exposure/tree/main/data) last retrieved on: 2021/01/15

## Contents
- [[Quick start]]
- [[Rate Limits and more control]]
Rate Limits and more control


## Quick start

```python
from py_misinfo_exposure import PyMisinfoExposure

# Set your personal Twitter bearer token
bearer = "YOUR TWITTER BEARER TOKEN"

# Initialize the PyMisinfoExposure class with your bearer token
pme = PyMisinfoExposure(bearer_token=bearer)

# Under the hood, py_misinfo_exposure utilizes Tweepy to access Twitter data
# This function authorizes your access to Twitter with the earlier provided bearer token
pme.tweepy_bearer_authorization()

# Create a list of unique Twitter user IDs that you would like misinformation exposure scores for
user_test_list = ["1312850357555539972", "1260526934678740993"]

# Get misinformation exposure scores
misinfo_scores, missing_users = pme.get_misinfo_exposure_score(user_test_list)

# Which returns
                  user  misinfo_score
0  1260526934678740993            NaN # NaN means this user does not follow any of the tracked political elites
1  1312850357555539972       0.675167
```
> Note that `pme.get_misinfo_exposure_score` returns a tuple.
>
> In the tuple above, `misinfo_scores` represents a [pandas dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) object and `missing_users` will return a set of users for whom no friends were found. This may happen, for example, if the account has been suspended or it does not exist. If there are no missing users, `missing_users` is returned as `None`.


## Rate Limits and more control

`py_misinfo_exposure` uses the [`tweepy`](https://www.tweepy.org/) package under the hood to gather Twitter data and, with the Twitter bearer token that you provide, initializes a [`tweepy`](https://www.tweepy.org/) client that will automatically wait the proper amount of time when Twitter rate limits have been hit.

### Verbosity 
If you would like misinformation exposure scores for a large set of users, it may take some time to retrieve all of the friends for all of the users you are interested in.

> Note: How long it will take is explicitly determined by Twitter's API rate limits. For more information, you can see Twitter's API [documentation](https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-following) for the endpoint utilized by `py_misinfo_exposure`. 
>
> **TLDR: You can retrieve _up to_ 15,000 friends every 15 minutes.** In reality, the number of friends you can retrieve from Twitter in 15 minutes will likely be less because rate limits are based on the _number of API calls_ made to Twitter and not the number of friends returned.

**To print updates for a long-running script, you can utilize the other `PyMisinfoExposure` arguments: `verbose` and `update_on`.**

For example, if you want the `PyMisinfoExposure` class to let you know every time another 500 users have been processed, you can initialize the class in the following way:

```python
pme = PyMisinfoExposure(
    bearer_token=bearer,
    verbose=True,
    update_on=500 # default value = 100
    )
```

## Example script
This repository also includes an example script called [`get_users_misinfo_exposure_scores.py`](https://github.com/mr-devs/py_misinfo_exposure/blob/main/get_users_misinfo_exposure_scores.py) that takes in a file which contains one Twitter user ID on each line and returns a CSV file containing all of those users misinformation-exposure scores. I suggest first executing the below line of code from your command line...

```bash
python3 get_users_misinfo_exposure_scores.py -h
```

...which will display what the script does and all of the command line flags that are available.

For a quick start, it can be run in the following way...

```bash
python3 get_users_misinfo_exposure_scores.py --input_file data/randomusers.txt --output_file 'my_output_filename' --bearer_token $TWITTER_BEARER_TOKEN
```

... where `$TWITTER_BEARER_TOKEN` should be replaced with you Twitter developer bearer token. 