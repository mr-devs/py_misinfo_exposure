"""
The setup script for PyPi package installation/updates.
"""

from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="py_misinfo_exposure",
    version="1.1",
    description="Calculate misinformation-exposure scores for users based on "
                "the falsity scores of public figures they follow on Twitter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Creative Commons",
    author="Matthew DeVerna",
    author_email="mdeverna@iu.edu",
    url="https://github.com/mr-devs/py_misinfo_exposure",
    project_urls={
        "Documentation": "https://github.com/mr-devs/py_misinfo_exposure",
        "Issue Tracker": "https://github.com/mr-devs/py_misinfo_exposure/issues",
        "Source Code": "https://github.com/mr-devs/py_misinfo_exposure",
    },
    download_url="https://pypi.org/project/py_misinfo_exposure/",
    packages=["py_misinfo_exposure"],
    package_data={
        'py_misinfo_exposure': ['data/falsity_scores.csv']
    },
    include_package_data = True,
    install_requires=[
        "tweepy>=4.4.0",
        "pandas>=1.2.4"
    ],
    python_requires=">=3.7",
)