"""
Collect misinformation scores from the command line by providing a list of unique
user IDs.

Input: a file with one user ID per line

Output: 
    - a CSV file including user ID and misinformation exposure score on each line
        will be saved in the current working directory
    - if certain user IDs cannot be found, they will be written to another file
        called `missing_users.txt` in the current working directory

Author: Matthew DeVerna
Date: 2022/01/126
"""

import argparse
from datetime import datetime as dt

from argparse import RawDescriptionHelpFormatter
from py_misinfo_exposure import PyMisinfoExposure

# Create Functions.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def parse_cl_args():
    """Set CLI Arguments."""

    # Initiate the parser
    parser = argparse.ArgumentParser(
        description="A script for gathering a list of Twitter user IDs misinformation exposure scores."
        "\n\n"
        "Notes:"
        "\n1. Results will be saved in the current working directory"
        "\n2. If data cannot be gathered for certain users in your list, this script will output "
        "a separate file called `missing_users.txt` with those users for further investigation "
        "\n3. The misinformation exposure score was developed by Mosleh and Rand (2021) and a working"
        "paper can be found here: https://psyarxiv.com/ye3pf/",
        formatter_class=RawDescriptionHelpFormatter
    )
    # Add arguments
    parser.add_argument(
        "-i", "--input_file",
        metavar='Input file',
        help="Full path to the file containing the USER IDS you would like to scrape.",
        required=True
    )

    parser.add_argument(
        "-b", "--bearer_token",
        metavar='Twitter bearer token',
        help="Your unique Twitter developer bearer token.",
        required=True
    )

    parser.add_argument(
        "-o", "--output_file",
        metavar='Output files',
        help="Prefix of output file to be saved in the current directory. Your "
        "input will be followed by the date + .csv like: `--Y_m_d__H_M_S.csv`",
        required=False
    )

    # Read parsed arguments from the command line into `args`
    args = parser.parse_args()

    return args


def load_users(ids_file):
    """
    Load all user IDs into a list.

        Note: The input file must be a plain text file where each line contains
        only a single unique Twitter user ID.

    Parameters:
    -----------
    - ids_file (str) : the full path to the Twitter user IDs file that you'd like to load

    Returns:
    ----------
    - users (list) : a list of Twitter user IDs
    """

    with open(ids_file, 'r') as f:
        users = [x.strip('\n') for x in f.readlines()]

    return users


def add_date_to_output_filename(output_filename):
    """
    Add the date the script completes into the output file name.
        - Format: %Y_%m_%d__%H_%M_%S

    Parameters:
    ----------
    - output_filename (str, None) : if type == string, this is the file name
        provided by the user. If type == None, then we use the default output
        name (see below).

    Returns:
    ----------
    - output_filename (str) : the final output file name like the below:
        - `outputfilename--%Y_%m_%d__%H_%M_%S.csv`
    """

    if output_filename is None:
        output_filename = "misinfo_exposure_scores" # Default name if nothing is provided

    date_suffix = dt.strftime(dt.today(), "--%Y_%m_%d__%H_%M_%S.csv")

    return output_filename + date_suffix



# Execute the program
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_cl_args()
    user_ids_file = args.input_file
    bearer_token = args.bearer_token
    output_filename = args.output_file

    # Load and download misinformation exposure scores for a list of user ids
    user_ids_list = load_users(user_ids_file)
    pme = PyMisinfoExposure(
        bearer_token=bearer_token,
        verbose=True,                 # True = print updates | False = do not
        update_on=2,                  # Print updates after this many users processed
        save_friends_to_disk=True     # True = save intermediate friends data to disk | False = do not
    )
    pme.tweepy_bearer_authorization()
    misinfo_scores, missing_users = pme.get_misinfo_exposure_score(user_ids_list)

    output_filename = add_date_to_output_filename(output_filename)
    misinfo_scores.to_csv(output_filename, index=False)

    if missing_users is not None:
        with open("missing_users.txt", "w") as f:
            for user in missing_users:
                f.write(f"{user}\n")

    print("--- Script Complete ---")