"""
Calculate misinformation-exposure scores for a user based on the falsity scores
of public figures the user follows.

Note:
This package replicates Mohsen Mosleh's R package (https://github.com/mmosleh/minfo-exposure)
which does the same thing and is based on Mosleh and Rand's paper (2021). 
- Paper         : https://psyarxiv.com/ye3pf/ 
- Data          : https://github.com/mmosleh/minfo-exposure/tree/main/data
- Data retrieved: 2021/01/15

Author: Matthew R. DeVerna (https://github.com/mr-devs)
"""
import os
import warnings
from collections import defaultdict

import tweepy
import pandas as pd


class PyMisinfoExposure:
    
    def __init__(
        self,
        bearer_token: str = None,
        verbose: bool = False,
        update_on: int = 25,
        save_friends_to_disk: bool = False,
        output_dir: str = "py_misinfo_friend_data"
    ):
        # Check input types
        if bearer_token is None:
            raise ValueError("Twitter bearer token is missing.")
        if not isinstance(verbose, bool):
            raise ValueError("`verbose` must be of type `bool`")
        if not isinstance(update_on, int):
            raise ValueError("`update_on` must be of type `int`")
        if not isinstance(save_friends_to_disk, bool):
            raise ValueError("`save_friends_to_disk` must be of type `bool`")
        if not isinstance(output_dir, str):
            raise ValueError("`output_dir` must be of type `str`")

        self._bearer_token = bearer_token
        self._verbose = verbose
        self._update_on = update_on
        self._save_friends_to_disk = save_friends_to_disk
        self._client = None
        self._output_dir = output_dir

        # Load falsity data.
        # Retrieved from: https://github.com/mmosleh/minfo-exposure/tree/main/data
        self.falsity_data = pd.read_csv(
            "./data/falsity_scores.csv",
            dtype = {
                "elite_account" : str,
                "pf_score" : float,
                "elite_id_str" : str,
                "falsity" : float
            }
        )


    def tweepy_bearer_authorization(self):
        """
        Authorize the Tweepy package using your developer bearer token.

        Note on Twitter API rate limiting:
            This function automatically waits the proper amount of time when Twitter
            sends a rate limit error.

        References:
        - Tweepy: https://www.tweepy.org/
        - Twitter bearer token: https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens

        Parameters:
        ----------
        - bearer_token (str) : a Twitter-provided developer bearer token. See reference above for
            more information

        Returns:
        ----------
        - client (tweepy.client.Client) : a Tweepy api client that that allows one to gather Twitter data

        Exceptions:
        ----------
        - TypeError
        """
        if not isinstance(self._bearer_token, str):
            raise TypeError(
                f"`bearer_token` must be a string."
                "Please reinitialize the PyMisinfoExposure class with a string type bearer token."
            )

        self._client = tweepy.Client(bearer_token=self._bearer_token, wait_on_rate_limit=True)


    def _get_users_data(self, user_id_list=list) -> pd.core.frame.DataFrame:
        """
        Return user info needed for `get_misinfo_exposure_score`.

        Parameters:
        ----------
        - user_id_list (str) : the list of unique Twitter user IDs for which you'd like data.
        - client (tweepy.client.Client) : a Tweepy api client that allows one to gather Twitter data

        Returns:
        ----------
        results = (list) : a list of tuples where each item is:
            ('queried_user', 'friend_id', 'friend_name', 'friend_username')

        Exceptions:
        ----------
        - ValueError
        - TypeError
        """

        # Throw errors if function input is incorrect
        if self._client is None:
            raise ValueError("No Tweepy client provided.")

        if not isinstance(user_id_list, list):
            raise TypeError(f"`user_id_list` must be a list.")

        if not all(isinstance(uid, str) for uid in user_id_list):
            out_string = "\n\nNon-string user IDs and corresponding indices:\n"
            for idx, uid in enumerate(user_id_list):
                if not isinstance(uid, str):
                    out_string += f"\tProvided ID: {uid} | List index: {idx}\n"
            raise TypeError("Some user IDs are not strings..." + out_string)

        if self._verbose:
            print(f"Beginning to pull friends for {len(user_id_list):,} users.")
            print(f"Will update on progress every {self._update_on:,} users.")

        if self._save_friends_to_disk:
            if not os.path.exists(self._output_dir):
                os.mkdir(self._output_dir)
            if self._verbose:
                print(f"Friends data will be saved here: {self._output_dir}")

        # Gather results
        results = []
        for user_count, user in enumerate(user_id_list, start=1):

            ### Get friends data ###

            # If save_friends_to_disk == True, we write these results to the disk
            if self._save_friends_to_disk:
                out_path = os.path.join(self._output_dir, f"{user}_data.txt")

                try:
                    if os.path.exists(out_path):
                        if self._verbose:
                            print(
                                f"\t - Data for user ({user}) already exists, so we will "
                                "skip this user. If you think this is a mistake and want to "
                                f"gather data for this user, delete this user's file ({out_path}) and rerun."
                            )
                        continue

                    with open(out_path, "w") as f:
                        for friend in tweepy.Paginator(self._client.get_users_following, id=user, max_results=1000).flatten():
                            friend_info = tuple([user] + list(friend.values()))
                            f.write(f"{friend_info}\n")

                except KeyboardInterrupt:
                    except_string = "MANUAL ABORT!!!\n\n"
                    except_string += f"WARNING: this file {out_path} may be incomplete!!!"
                    raise Exception(except_string)

            # Otherwise, we save the data in working memory
            else:
                for friend in tweepy.Paginator(self._client.get_users_following, id=user, max_results=1000).flatten():
                    friend_info = tuple([user] + list(friend.values()))
                    results.append(friend_info)

            if self._verbose and (user_count % self._update_on == 0):
                print(f"{user_count} users processed...")

        return results


    def _load_cached_friend_data(self):
        """
        Load all individual friend data files in self._output_dir

        Returns:
        ----------
        - results = (list) : a list of tuples where each item is:
            ('queried_user', 'friend_id', 'friend_name', 'friend_username')
            Note: This will include all data for all files with any data
        """

        results = []
        files = os.listdir(self._output_dir)

        for file in files:
            file_to_load = os.path.join(self._output_dir, file)
            with open(file_to_load, "r") as f:
                for line in f:
                    results.append(eval(line))

        return results


    def get_misinfo_exposure_score(self, user_id_list=list) -> pd.core.frame.DataFrame:
        """
        Calculate a user's misinformation exposure score based on the Twitter accounts they follow.
            - Misinformation Exposure reference: https://psyarxiv.com/ye3pf/

        Parameters:
        ----------
        - user_id_list (str) : the list of unique Twitter user IDs for which you'd like data.
        - client (tweepy.client.Client) : a Tweepy api client that allows one to gather Twitter data

        Returns:
        ----------
        - results (pandas.core.frame.DataFrame) : a pandas dataframe containing all of the queried results.
        - missing_users (set, None) : a set of users for whom no friends were found. This may happen, for example,
            if the account has been suspended or it does not exist. If there are no missing users, `missing_users`
            is returned as `None`.

        Exceptions:
        ----------
        - ValueError
        - TypeError
        """

        # Throw errors if function input is incorrect
        if self._client is None:
            raise ValueError("No Tweepy client provided.")

        if not isinstance(user_id_list, list):
            raise TypeError(f"`user_id_list` must be a list.")

        if not all(isinstance(uid, str) for uid in user_id_list):
            out_string = "\n\nNon-string user IDs and corresponding indices:\n"
            for idx, uid in enumerate(user_id_list):
                if not isinstance(uid, str):
                    out_string += f"\tProvided ID: {uid} | List index: {idx}\n"
            raise TypeError("Some user IDs are not strings..." + out_string)

        # Remove duplicate IDs and get all user data
        user_id_list = list(set(user_id_list))
        results = self._get_users_data(user_id_list)

        # If the below is true, `results` is currently an empty list so we load the
        # cached data from self._output_dir and use that
        if self._save_friends_to_disk:
            results = self._load_cached_friend_data()

        # Create dictionary of the following form: {queried_user : list_of_friends}
        df_dict = defaultdict(list)
        for queried_user, friend_id, _, _ in results:
            df_dict[queried_user].append(str(friend_id))

        # Get misinformation exposure scores
        falsity_data = self.falsity_data
        misinfo_scores = []
        for user, friends in df_dict.items():
            misinfo_score = falsity_data[falsity_data["elite_id_str"].isin(friends)].falsity.mean()
            misinfo_scores.append((user, misinfo_score))

        # Convert results to dataframe
        misinfo_scores_df = pd.DataFrame(misinfo_scores, columns=["user", "misinfo_score"])
        num_unique_users = misinfo_scores_df.user.nunique()

        # If user IDs are missing, raise a warning
        user_set = set(user_id_list)
        missing_users = None
        if len(user_set) != num_unique_users:
            users_w_scores = set(misinfo_scores_df.user.unique())
            missing_users = user_set.difference(users_w_scores)
            warning_str = f"\n\nWARNING!! Misinfo. exposure scores missing for {len(missing_users)} users.\n\n"
            warning_str += "Missing users:\n"
            for user in missing_users:
                warning_str += f"\t- User ID: {user}\n"
            warnings.warn(message = warning_str)

        return misinfo_scores_df, missing_users