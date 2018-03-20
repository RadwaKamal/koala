import feedparser as fp
import tweepy as tp
import os
import csv
import time
from datetime import datetime
import psycopg2
import urllib.parse

def tweet(new_entries, publication_name):
	for new_entry in new_entries:
		tweet = new_entry[1] + " " + new_entry[0]
		try:
			api.update_status(tweet)
			cur = conn.cursor()
			cur.execute(insert_sql,(new_entry[0][21:], new_entry[2], publication_name))
			conn.commit()
			cur.close()
		except tp.error.TweepError as e:
			print(e.response.text)
			print(new_entry[0][21:])


def manipulate_entry_tags(tags):
	hashtags = ""
	for tag in tags:
		"""
		tag is in form : {'label': None, 'scheme': None, 'term': 'web-development'} 
		Extract term only and replace "-" if exists with "_"
		"""
		hashtag = tag.term
		if(hashtag.find('-') != -1):
			hashtag = str.replace(hashtag, "-", "_")
		hashtags += "#" + hashtag + " "
	return hashtags


def handle_entries(entries, publication_name):
	new_entries = []
	for entry in entries:
		cur = conn.cursor()
		entry_published_date = str.replace(entry.published, ' GMT', '')
		formated_publication_dt = datetime.strptime(entry_published_date, '%a, %d %b %Y %H:%M:%S')
		cur.execute(select_sql,(entry.id[21:],))
		row = cur.fetchone()
	
		if not row:
			entry_tags = manipulate_entry_tags(entry.tags)
			new_entries.append([entry.id, entry_tags, formated_publication_dt])
		cur.close()
	tweet(new_entries, publication_name)

def init(publication_name):
	rss = fp.parse(urls[publication_name])
	handle_entries(rss.entries, publication_name)

if __name__ == '__main__':
	#Auth for tweepy 
	C_KEY = os.environ.get('C_KEY')
	C_SECRET = os.environ.get('C_SECRET')
	A_TOKEN = os.environ.get('A_TOKEN')
	A_TOKEN_SECRET = os.environ.get('A_TOKEN_SECRET')

	auth = tp.OAuthHandler(C_KEY, C_SECRET)
	auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)  
	api = tp.API(auth)

	urllib.parse.uses_netloc.append("postgres")
	url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
	insert_sql = "INSERT INTO medium_publications (publication_id, published_at, publication_name) VALUES (%s, %s, %s)"
	select_sql = "SELECT 1 FROM medium_publications WHERE publication_id=%s"

	conn = psycopg2.connect(
    	database=url.path[1:],
    	user=url.username,
    	password=url.password,
    	host=url.hostname,
    	port=url.port
	)

	while True:
		#Get feed
		urls = {
			"free_code_camp": "https://medium.freecodecamp.org/feed",
			"javascript_scene": "https://medium.com/feed/javascript-scene",
			"reloading": "https://medium.com/feed/reloading",
			"prototypr": "https://blog.prototypr.io/feed",
			"uxdesign": "https://uxdesign.cc/feed",
			"dev_channel": "https://medium.com/feed/dev-channel",
			"hackernoon": "https://hackernoon.com/feed",
			"vue": "https://medium.com/feed/the-vue-point"
		}

		map(init, urls)

		time.sleep(43200)
