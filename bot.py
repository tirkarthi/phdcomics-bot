import time
from collections import OrderedDict
import json
import os
import re

import praw
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv())

client_id=os.environ['REDDIT_CLIENT_ID']
client_secret=os.environ['REDDIT_CLIENT_SECRET']
password=os.environ['REDDIT_PASSWORD']
username=os.environ['REDDIT_USERNAME']
subreddit=os.environ['SUBREDDIT']
user_agent='user-agent for /u/PhDComicsBot'

if __name__ == "__main__":

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         password=password,
                         username=username,
                         user_agent=user_agent)

    while True:
        print("Collecting all comics")
        r = requests.get("http://phdcomics.com/comics/archive_list.php")

        # Save for debugging if something goes wrong
        with open('index.html', 'w') as outfile:
            outfile.write(r.text)

        comic_dict = OrderedDict()
        # We have no idea!
        regex = r'href\=.*?comicid=(\d+)>\s*<b>(.*?)</b>.*?<font.*?>(.*?)</font>'
        BASE_URL = 'http://www.phdcomics.com/comics/archive.php?comicid='

        # Some have newlines so use re.S to enable dot to match multilines
        items = re.findall(regex, r.text, re.S)
        for comic_id, date, title in items:
            comic_url = BASE_URL + comic_id
            comic_dict[comic_id] = {'id': comic_id, 'link': comic_url, 'date': date, 'title': title}

        print("Saving it to data.json")
        with open('data.json', 'w') as outfile:
            json.dump(comic_dict, outfile)

        last_comic_id = 0

        try:
            with open('last_comic.txt', 'r') as infile:
                last_comic_id = int(infile.read())
        except ValueError:
            print("File is empty. Something wrong happened. Better exit the program")
            exit(1)
        except FileNotFoundError:
            print("File not found so this must be the first run")

        for comic_id in comic_dict:
            if int(comic_id) <= last_comic_id:
                continue
            date = comic_dict[comic_id]['date']
            title = comic_dict[comic_id]['title']
            comic_url = BASE_URL + comic_id
            print("Submitting {0} with title '{1}'".format(comic_url, title))
            reddit.subreddit(subreddit).submit(title, url=comic_url)
            print("Saving the latest comic id : {}".format(comic_id))
            with open('last_comic.txt', 'w') as outfile:
                outfile.write(comic_id)
            break
        time.sleep(24 * 60 * 60) # Sleep for a day
