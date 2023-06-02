# Important!
This package has not been updated since Twitter made drastic changes to the cost of using their API.
Please make sure that you understand how this code works before using it.
Also, note that the rate limiting information mentioned in this README file is out of date, as Twitter made changes to this as well.

# `py_misinfo_exposure`
A Python package that can be used to calculate misinformation-exposure scores for a user based on the falsity scores of public figures they follow on Twitter.

The falsity score is based on PolitiFact fact-checks of the public figures.

> 🚨 Notes 🚨:
> 1. This package replicates [Mohsen Mosleh's R package](https://github.com/mmosleh/minfo-exposure) which does the same thing and is based on Mosleh and Rand's paper (2022).
>     - [Paper](https://doi.org/10.1038/s41467-022-34769-6)
>     - [Data](https://github.com/mmosleh/minfo-exposure/tree/main/data) last retrieved on: 2021/01/15
>         - Note: The data in this repository is based on the preprint version of this paper ([found here](https://psyarxiv.com/ye3pf/)). See the Nature Communications paper linked-to above for access to a Rapid API tool built by the Moseleh & Rand.
> 2. **This package requires you have a Twitter developer account with access to [_Twitter's V2 API_](https://developer.twitter.com/en/docs/twitter-api)** 


## Contents
- [Installation](#installation)
- [Quick start](#quick-start)
- [Understanding the package and more control](#understanding-the-package-and-more-control)
    - [Rate limits](#rate-limits)
    - [Calculating scores for a large list of users](#calculating-scores-for-a-large-list-of-users)
    - [Verbosity](#verbosity)
- [Example script](#example-script)


## Installation
This package has been uploaded to the PyPi index so it can be installed via the command line via...
```python
pip install py_misinfo_exposure
```


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

# Where `misinfo_scores` is the below pandas.DataFrame

                  user  misinfo_score
0  1260526934678740993            NaN # NaN means this user does not follow any of the tracked political elites
1  1312850357555539972       0.675167
```
> Note that `pme.get_misinfo_exposure_score` returns a tuple.
>
> In the tuple above, `misinfo_scores` represents a [pandas dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) object and `missing_users` will return a set of users for whom no friends were found. This may happen, for example, if the account has been suspended or it does not exist. If there are no missing users, `missing_users` is returned as `None`.


## Understanding the package and more control

### How the package works
The package works by taking the list of user IDs that you provide and then asking Twitter to provide all of their friends on Twitter (the people that they follow). After this has been done, the mean "falsity" score is taken from all of the friends that a user follows that are present within the [PolitiFact data](https://github.com/mr-devs/py_misinfo_exposure/blob/main/py_misinfo_exposure/data/falsity_scores.csv).


### Rate limits
`py_misinfo_exposure` uses the [`tweepy`](https://www.tweepy.org/) package under the hood to gather Twitter data and, with the Twitter bearer token that you provide, initializes a [`tweepy`](https://www.tweepy.org/) client that will automatically wait the proper amount of time when Twitter rate limits have been hit.


### Calculating scores for a large list of users
The default way that `py_misinfo_exposure` works is to download all of the friends data from Twitter and hold it in your machine's working memory. This becomes problematic when calculating scores for a large list of users because your machine may crash from holding too much data at once.

To solve this problem you can simply set `save_friends_to_disk=True` when you initialize the `PyMisinfoExposure` class like so:

```python
pme = PyMisinfoExposure(
    bearer_token=bearer,
    save_friends_to_disk=True   # <---------- Add this to save friends data to your machine
    )
```

Then, when you call `pme.get_misinfo_exposure_score(users)`, friends data will be downloaded into a folder within your current working directory.
By default, this folder will be called `py_misinfo_friend_data`, however, you can again manually control the name of this folder by setting the `output_dir` parameter when you initialize the `PyMisinfoExposure` class in the following way.

```python
pme = PyMisinfoExposure(
    bearer_token=bearer,
    save_friends_to_disk=True,      # <---------- Add this to save friends data to your machine
    output_dir='myoutputdirectory'  # <---------- Add this to save friends data into the 'myoutputdirectory' folder
    )
```


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
This repository also includes an example script called [`get_users_misinfo_exposure_scores.py`](https://github.com/mr-devs/py_misinfo_exposure/blob/main/scripts/get_users_misinfo_exposure_scores.py) that takes in a file which contains one Twitter user ID on each line and returns a CSV file containing all of those users misinformation-exposure scores. I suggest first executing the below line of code from your command line...

```bash
python3 get_users_misinfo_exposure_scores.py -h
```

...which will display what the script does and all of the command line flags that are available.

For a quick start, it can be run in the following way...

```bash
python3 get_users_misinfo_exposure_scores.py --input_file py_misinfo_exposure/data/randomusers.txt --output_file 'my_output_filename' --bearer_token $TWITTER_BEARER_TOKEN
```

... where `$TWITTER_BEARER_TOKEN` should be replaced with your Twitter developer bearer token. 

> Note: The parameters set inside of this script for `PyMisinfoExposure` will likely need to be updated for more practical use. For example, this script provides updates after every 2 users, which is quite fast (to provide feedback for testing quickly).
